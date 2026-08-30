import numpy as np
from skimage import measure
import json
import random

random.seed(7)
np.random.seed(7)

W, H = 1400, 1000  # working grid resolution
VIEW_W, VIEW_H = 1400, 1000

def make_heightfield(w, h, n_peaks=22):
    y, x = np.mgrid[0:h, 0:w]
    field = np.zeros((h, w), dtype=float)
    for _ in range(n_peaks):
        cx = random.uniform(0, w)
        cy = random.uniform(0, h)
        sx = random.uniform(w*0.035, w*0.09)
        sy = random.uniform(h*0.035, h*0.09)
        amp = random.uniform(0.5, 1.0) * random.choice([1, 1, 1, -0.6])
        angle = random.uniform(0, np.pi)
        # rotated anisotropic gaussian for organic elongated hills
        xr = (x-cx)*np.cos(angle) + (y-cy)*np.sin(angle)
        yr = -(x-cx)*np.sin(angle) + (y-cy)*np.cos(angle)
        field += amp * np.exp(-(xr**2/(2*sx**2) + yr**2/(2*sy**2)))
    return field

field = make_heightfield(W, H, n_peaks=46)
fmin, fmax = field.min(), field.max()
field = (field - fmin) / (fmax - fmin)  # normalize 0..1

levels = np.linspace(0.08, 0.92, 20)

def path_is_suspicious(c):
    # Reject near-straight artifact segments, at any size: a genuine closed
    # hill contour always has path length well above its bounding-box
    # diagonal (a circle is already ~3.14x); a near-straight line sits
    # close to 1x. Catches both long diagonals and short stray strokes.
    bbox_diag = np.hypot(c[:,0].max()-c[:,0].min(), c[:,1].max()-c[:,1].min())
    path_len = np.sum(np.hypot(np.diff(c[:,0]), np.diff(c[:,1])))
    if bbox_diag < 1:
        return False
    straightness = path_len / bbox_diag
    return straightness < 1.5

paths = []  # list of {d, level_index, is_index}
for li, lvl in enumerate(levels):
    contours = measure.find_contours(field, lvl)
    is_index = (li % 4 == 0)
    for c in contours:
        if len(c) < 16:
            continue
        if path_is_suspicious(c):
            continue  # drop near-straight long artifact lines
        # c is array of (row, col) = (y, x)
        pts = c[:, ::-1]  # to (x, y)
        # scale grid coords to viewBox
        pts = pts * [VIEW_W / W, VIEW_H / H]
        # simplify by taking every 3rd point to reduce size, keep closed
        pts = pts[::3]
        if len(pts) < 6:
            continue
        is_closed = np.allclose(c[0], c[-1], atol=0.6)
        d = "M" + "L".join(f"{px:.0f},{py:.0f}" for px, py in pts)
        if is_closed:
            d += "Z"
        paths.append({"d": d, "index": is_index})

print("total contour paths:", len(paths))
total_len = sum(len(p["d"]) for p in paths)
print("total path char length:", total_len)

with open("/Users/alex/Alex/Claude Projects/Hangneigungslayer Garmin/website_prototype/build/contours_data.json", "w") as f:
    json.dump({"viewW": VIEW_W, "viewH": VIEW_H, "paths": paths}, f)
