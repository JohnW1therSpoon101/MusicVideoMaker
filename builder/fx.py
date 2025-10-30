import numpy as np
import librosa
from moviepy.editor import ColorClip, CompositeVideoClip


def get_beats_seconds(audio_path):
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    return librosa.frames_to_time(beats, sr=sr).tolist()


def make_haze_layer(dur, size, strength=0.15):
    w, h = size
    base = ColorClip(size, color=(20, 6, 8)).set_opacity(strength).set_duration(dur)
    vign = ColorClip(size, color=(0, 0, 0)).set_opacity(0.25).set_duration(dur)
    return CompositeVideoClip([base, vign], size=size)


def flare_layer_on_beats(beats_s, dur, size, scene_start):
    w, h = size
    pulses = []
    for b in beats_s:
        t = b - scene_start
        if 0 <= t <= dur:
            pulses.append(
                ColorClip(size, color=(255, 180, 90))
                .set_duration(0.06)
                .set_start(t)
                .set_opacity(0.18)
            )
    return CompositeVideoClip(pulses, size=size) if pulses else None


def color_overlay(dur, size, color=(255, 255, 255), opacity=0.2):
    return ColorClip(size, color=color).set_opacity(opacity).set_duration(dur)


def smoke_layer(dur, size):
    return ColorClip(size, color=(150, 150, 150)).set_opacity(0.12).set_duration(dur)


def neon_sign_glow(dur, size):
    return ColorClip(size, color=(255, 0, 100)).set_opacity(0.08).set_duration(dur)


def fade_lights_layer(dur, size):
    w, h = size
    base = ColorClip(size, color=(0, 0, 0)).set_opacity(0.0).set_duration(dur)
    fade = base.crossfadein(0.0).crossfadeout(2.0)
    return fade