import numpy as np
from moviepy.editor import ColorClip, CompositeVideoClip
import librosa, soundfile as sf

def get_beats_seconds(audio_path):
    y, sr = librosa.load(audio_path, sr=None, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    return librosa.frames_to_time(beats, sr=sr).tolist()

def make_haze_layer(dur, size, strength=0.15):
    w, h = size
    base = ColorClip(size, color=(20,6,8)).set_opacity(strength).set_duration(dur)
    vign = ColorClip(size, color=(0,0,0)).fl_image(
        lambda frame: frame
    ).set_opacity(0.25).set_duration(dur)
    return CompositeVideoClip([base, vign], size=size)

def flare_layer_on_beats(beats_s, dur, size, scene_start):
    w,h = size
    pulses = []
    for b in beats_s:
        t = b - scene_start
        if 0 <= t <= dur:
            pulses.append(ColorClip(size, color=(255,180,90)).set_duration(0.06).set_start(t).set_opacity(0.18))
    return CompositeVideoClip(pulses, size=size) if pulses else None