import json
import yaml
import numpy as np
from pathlib import Path
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from utils import load_img_rgba, norm_to_px
from camera import PanZoom
from fx import (
    make_haze_layer,
    flare_layer_on_beats,
    color_overlay,
    smoke_layer,
    neon_sign_glow,
    fade_lights_layer
)

# ------------------------------------------------------------
# Load configuration
# ------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
CFG_PATH = ROOT / "config.yaml"

if not CFG_PATH.exists():
    raise FileNotFoundError(f"Missing config.yaml at {CFG_PATH}")

CFG = yaml.safe_load(CFG_PATH.read_text())


# ------------------------------------------------------------
# Resolve project root automatically
# ------------------------------------------------------------
def resolve_project_root(cfg_root: Path) -> Path:
    candidates = [
        cfg_root,
        ROOT.parent / "WMT_MUSICVIDEO",
        ROOT.parent / "MusicVideoMaker" / "WMT_MUSICVIDEO",
        ROOT.parent / "MUSICVIDEOMAKER" / "WMT_MUSICVIDEO",
    ]
    for p in candidates:
        if p.exists() and p.is_dir():
            print(f"🔎 Using project_root: {p}")
            return p
    raise FileNotFoundError(
        "Could not locate WMT_MUSICVIDEO folder. Tried:\n" + "\n".join(str(p) for p in candidates)
    )


PROJ = resolve_project_root(Path(CFG["project_root"]))

W, H = CFG["video"]["size"]
FPS = CFG["video"]["fps"]


# ------------------------------------------------------------
# Helper to find master audio
# ------------------------------------------------------------
def pick_master_audio(configured_rel: str) -> Path:
    target = PROJ / configured_rel
    if target.exists():
        return target
    audio_dir = PROJ / "audio"
    picks = [p for p in audio_dir.iterdir() if p.suffix.lower() in (".wav", ".mp3", ".flac", ".m4a")]
    if not picks:
        raise FileNotFoundError(f"No audio files found in {audio_dir}")
    pick = sorted(picks)[0]
    print(f"🎧 Configured master not found; using detected audio: {pick.name}")
    return pick


# ------------------------------------------------------------
# Scene builder
# ------------------------------------------------------------
def build_scene(scene_json_path, audio_master, beats_s):
    scene_path = PROJ / scene_json_path
    if not scene_path.exists():
        raise FileNotFoundError(f"Scene file missing: {scene_path}")

    spec = json.loads(scene_path.read_text())
    dur = spec["end_s"] - spec["start_s"]

    # Background
    bg_key = spec["bg"]
    bg_img = load_img_rgba(PROJ / CFG["backgrounds"][bg_key])
    bg_clip = ImageClip(bg_img).set_duration(dur).resize((W, H))

    # Camera
    cam = PanZoom(W, H, spec.get("camera", []))
    bg_clip = bg_clip.fl(cam.apply)

    # Characters
    layers = [bg_clip]
    for a in spec.get("actors", []):
        who = a["who"]
        if who not in CFG["characters"]:
            print(f"⚠️ Character '{who}' not in config.yaml, skipping.")
            continue

        img_path = PROJ / CFG["characters"][who]
        if not img_path.exists():
            print(f"⚠️ Missing image for '{who}': {img_path}")
            continue

        img = load_img_rgba(img_path)
        x, y = norm_to_px(a["x"], a["y"], W, H)
        scale = a.get("scale", 1.0)

        clip = ImageClip(img).resize(scale).set_duration(dur).set_position((x, y))

        # Simple animation
        for act in a.get("actions", []):
            if act["type"] == "bob":
                amp = act.get("amp", 6)
                clip = clip.set_position(
                    lambda t, x=x, y=y, amp=amp: (x, y + amp * np.sin(2 * np.pi * (t / 1.2)))
                )

        layers.append(clip)

    # Crowd
    if spec.get("crowd", {}).get("visible", False):
        aud_img = load_img_rgba(PROJ / CFG["characters"]["audience"])
        crowd = (
            ImageClip(aud_img)
            .set_duration(dur)
            .resize(width=W)
            .set_position(("center", "bottom"))
        )
        sway = spec["crowd"].get("sway", 0.0)
        if sway:
            crowd = crowd.set_position(
                lambda t: ("center", H - 60 + 8 * np.sin(t * 2 * np.pi * 0.4))
            )
        layers.append(crowd)

    # FX base layers
    fx_settings = spec.get("fx", {})
    if fx_settings.get("haze", False):
        layers.append(make_haze_layer(dur, (W, H), CFG["style"]["haze_strength"]))

    if CFG["style"].get("flare_on_beats") and fx_settings.get("flare_on_snare", False):
        flare = flare_layer_on_beats(beats_s, dur, (W, H), spec["start_s"])
        if flare is not None:
            layers.append(flare)

    # Extended FX
    fx_name_list = [
        ("bar_reflections", (255, 200, 120)),
        ("ambient_smoke", (180, 180, 180)),
        ("red_gold_gels", (255, 100, 0)),
        ("neon_sign_glow", (255, 80, 180)),
    ]
    for tag, color in fx_name_list:
        if tag in fx_settings.get("sign_text", "").lower() or fx_settings.get(tag, False):
            layers.append(color_overlay(dur, (W, H), color=color, opacity=0.15))

    if fx_settings.get("lights_fade", False):
        layers.append(fade_lights_layer(dur, (W, H)))

    if fx_settings.get("neon_sign_glow", False):
        layers.append(neon_sign_glow(dur, (W, H)))

    # Composite final
    return CompositeVideoClip(layers, size=(W, H)).set_start(spec["start_s"]).set_end(spec["end_s"])


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    audio_path = pick_master_audio(CFG["audio"]["master"])
    print(f"🎵 Using master audio: {audio_path.name}")
    audio = AudioFileClip(str(audio_path))

    # Optional beat tracking
    try:
        from fx import get_beats_seconds
        beats_s = get_beats_seconds(audio_path)
    except Exception as e:
        print(f"⚠️ Beat detection failed: {e}")
        beats_s = []

    scene_paths = CFG["scenes"]
    scene_clips = []
    for p in scene_paths:
        try:
            sc = build_scene(p, audio, beats_s)
            scene_clips.append(sc)
        except Exception as e:
            print(f"⚠️ Error building scene {p}: {e}")

    if not scene_clips:
        raise RuntimeError("No scenes built successfully. Check scene JSON files and assets.")

    timeline = CompositeVideoClip(scene_clips, size=(W, H)).set_audio(audio)
    out_path = Path(CFG["export"]["preview"]).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎬 Rendering to {out_path}")
    timeline.write_videofile(str(out_path), fps=FPS, codec="libx264", audio_codec="aac", bitrate="6000k")


if __name__ == "__main__":
    main()