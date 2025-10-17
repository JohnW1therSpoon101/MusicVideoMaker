import numpy as np

class PanZoom:
    def __init__(self, W, H, keyframes):
        self.W, self.H, self.kf = W, H, keyframes

    def apply(self, get_frame, t):
        f = get_frame(t)
        x,y,z = self._interp(t)
        # simple center crop + scale
        return f  # moviepy transform placeholder; pan/zoom already applied via set_position/resize in main for simplicity

    def _interp(self, t):
        if not self.kf: return 0.5,0.5,1.0
        k0 = max([k for k in self.kf if t>=k["t"]], key=lambda k:k["t"], default=self.kf[0])
        k1 = min([k for k in self.kf if t<=k["t"]], key=lambda k:k["t"], default=self.kf[-1])
        if k0==k1: return k0["x"],k0["y"],k0["zoom"]
        u = (t-k0["t"])/max(1e-6,(k1["t"]-k0["t"]))
        lerp = lambda a,b: a*(1-u)+b*u
        return lerp(k0["x"],k1["x"]), lerp(k0["y"],k1["y"]), lerp(k0["zoom"],k1["zoom"])