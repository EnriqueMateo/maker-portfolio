# Sustituto mínimo de pyvista para TRELLIS: solo PolyData(...).decimate(), con fast_simplification.
import numpy as np
import fast_simplification


class PolyData:
    def __init__(self, points, faces):
        self.points = np.asarray(points, dtype=np.float32)
        self.faces = np.asarray(faces).reshape(-1)

    def decimate(self, target_reduction, progress_bar=False, **kw):
        tri = self.faces.reshape(-1, 4)[:, 1:]
        pts, f = fast_simplification.simplify(self.points, tri.astype(np.int64), target_reduction=float(target_reduction))
        return PolyData(pts, np.concatenate([np.full((len(f), 1), 3), f], axis=1))
