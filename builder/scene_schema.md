# 🎬 WMT_MUSICVIDEO Scene Schema

**File name format:**  
`Scene##_Description.json`  
Example:  
`Scene01_Performance.json`

---

## 🧩 Scene JSON Structure

Each scene file defines what’s visible, how long it runs, what moves, and what effects apply.  
It’s built to work with your Music Video Maker Python project.

---

### 🧱 Full Example

```json
{
  "scene_name": "Scene01_Performance",
  "bg": "performance",
  "start_s": 0.0,
  "end_s": 22.5,
  "camera": [
    { "t": 0.0, "type": "panzoom", "x": 0.5, "y": 0.55, "zoom": 1.05 },
    { "t": 8.0, "type": "panzoom", "x": 0.35, "y": 0.58, "zoom": 1.12 },
    { "t": 15.0, "type": "panzoom", "x": 0.5, "y": 0.5, "zoom": 1.0 }
  ],
  "actors": [
    {
      "who": "stxrn",
      "x": 0.72,
      "y": 0.75,
      "scale": 1.0,
      "actions": [
        { "t": 0.0, "type": "bob", "amp": 6 },
        { "t": 10.0, "type": "zoom", "amp": 1.1 }
      ]
    },
    {
      "who": "rj",
      "x": 0.28,
      "y": 0.77,
      "scale": 1.0,
      "actions": [
        { "t": 0.0, "type": "bob", "amp": 5 },
        { "t": 12.0, "type": "nod", "amp": 4 }
      ]
    },
    { "who": "bass", "x": 0.15, "y": 0.78, "scale": 0.95 },
    { "who": "drums", "x": 0.5, "y": 0.82, "scale": 0.95 },
    { "who": "piano", "x": 0.62, "y": 0.81, "scale": 0.95 },
    { "who": "fx", "x": 0.9, "y": 0.8, "scale": 0.95 }
  ],
  "crowd": { "visible": true, "sway": 0.02 },
  "lip_sync": [
    { "who": "stxrn", "start_s": 0.0, "end_s": 12.2 },
    { "who": "rj", "start_s": 22.6, "end_s": 44.0 }
  ],
  "fx": {
    "haze": true,
    "flare_on_snare": true,
    "sign_text": "The BURGUNDY ROOM"
  }
}
```
