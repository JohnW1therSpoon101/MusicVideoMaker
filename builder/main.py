import json, yaml, subprocess, os
from pathlib import Path
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
import numpy as np

from utils import load_img_rgba, norm_to_px
from camera import PanZoom
from fx import make_haze_layer, flare_layer_on_beats
from lipsync import build_lipsync_track

ROOT = Path(__file__).resolve().parent
CFG  = yaml.safe_load((ROOT/"config.yaml").read_text())
PROJ = Path(CFG["project_root"])

W, H = CFG["video"]["size"]
FPS  = CFG["video"]["fps"]

def build_scene(scene_json_path, audio_master, beats_s):
    spec = json.loads((PROJ/scene_json_path).read_text())
    dur  = spec["end_s"] - spec["start_s"]

    # Background
    bg_key = spec["bg"]
    bg_img = load_img_rgba(PROJ/CFG["backgrounds"][bg_key])
    bg_clip = ImageClip(bg_img).set_duration(dur).resize((W,H))

    # Camera
    cam = PanZoom(W, H, spec.get("camera", []))
    bg_clip = bg_clip.fl(cam.apply)

    # Actors
    layers = [bg_clip]
    for a in spec.get("actors", []):
        img = load_img_rgba(PROJ/CFG["characters"][a["who"]])
        x, y = norm_to_px(a["x"], a["y"], W, H)
        scale = a.get("scale", 1.0)
        c = ImageClip(img).resize(scale).set_duration(dur).set_position((x, y), relative=False)
        # simple bob
        for act in a.get("actions", []):
            if act["type"] == "bob":
                amp = act.get("amp", 6)
                c = c.fl(lambda gf, t: gf(t), apply_to=['mask']).set_position(
                    lambda t, x=x, y=y, amp=amp: (x, y + amp*np.sin(2*np.pi*(t/1.2)))
                )
        layers.append(c)

    # Crowd sway
    if spec.get("crowd", {}).get("visible", False):
        aud_img = load_img_rgba(PROJ/CFG["characters"]["audience"])
        crowd = ImageClip(aud_img).set_duration(dur).resize(width=W).set_position(("center","bottom"))
        sway = spec["crowd"].get("sway", 0.0)
        if sway:
            crowd = crowd.set_position(lambda t: ("center", H - 60 + 8*np.sin(t*2*np.pi*0.4)))
        layers.append(crowd)

    # FX
    if spec.get("fx", {}).get("haze", False):
        layers.append(make_haze_layer(dur, (W,H), CFG["style"]["haze_strength"]))
    if CFG["style"].get("flare_on_beats") and spec.get("fx", {}).get("flare_on_snare", False):
        layers.append(flare_layer_on_beats(beats_s, dur, (W,H), spec["start_s"]))

    # Lip-sync: subtle head/mic motion if no mouth sprites
    ls_entries = spec.get("lip_sync", [])
    if CFG["lip_sync"]["enabled"] and ls_entries:
        ls_clip = build_lipsync_track(ls_entries, PROJ/CFG["lip_sync"]["vocals_stem"], dur, (W,H), spec["start_s"])
        if ls_clip: layers.append(ls_clip)

    return CompositeVideoClip(layers, size=(W,H)).set_start(spec["start_s"]).set_end(spec["end_s"])

def main():
    audio = AudioFileClip(str(PROJ/CFG["audio"]["master"]))
    # Beat map (drives flares/edits)
    try:
        from fx import get_beats_seconds
        beats_s = get_beats_seconds(PROJ/CFG["audio"]["master"])
    except Exception:
        beats_s = []

    scene_paths = CFG["scenes"]
    scene_clips = [build_scene(p, audio, beats_s) for p in scene_paths]
    timeline = CompositeVideoClip(scene_clips, size=(W,H)).set_audio(audio)
    out_path = Path(CFG["export"]["preview"]).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    timeline.write_videofile(str(out_path), fps=FPS, codec="libx264", audio_codec="aac", bitrate="6000k")

if __name__ == "__main__":
    main()