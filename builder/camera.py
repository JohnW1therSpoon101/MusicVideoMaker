class PanZoom:
    def __init__(self, W, H, keyframes):
        self.W, self.H = W, H
        self.kf = keyframes or []

    def apply(self, get_frame, t):
        # Placeholder for camera movement
        return get_frame(t)