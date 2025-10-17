from moviepy.editor import ColorClip, CompositeVideoClip

def build_lipsync_track(entries, vocals_path, dur, size, scene_start):
    # Placeholder: simple opacity pulse during each singer’s range (acts like spotlight cue)
    layers=[]
    for e in entries:
        s = max(0, e["start_s"]-scene_start)
        e_ = min(dur, e["end_s"]-scene_start)
        if s < e_:
            layers.append(ColorClip(size, color=(0,0,0)).set_opacity(0.0).set_start(s).set_duration(e_-s))
    return CompositeVideoClip(layers, size=size) if layers else None