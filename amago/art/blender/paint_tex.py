# Texturas pintadas a mano (repetibles) para suelo y agua: python paint_tex.py <salida_dir>
# Imitan el estilo Clash Royale: base plana, manchas suaves y trazos; se sustituyen por las de Gemini cuando estén.
import sys, math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]; N = 512; random.seed(3)

def wrap_draw(layer, fn):
    d = ImageDraw.Draw(layer)
    for ox in (-N, 0, N):
        for oy in (-N, 0, N): fn(d, ox, oy)

def layer(col):
    # capa del color del trazo con alfa 0: al difuminar no salen bordes oscuros
    return Image.new('RGBA', (N, N), col[:3] + (0,))

def stroke(d, pts, col, w):
    for i in range(len(pts) - 1):
        t = i / (len(pts) - 1); ww = max(1, int(w * math.sin(math.pi * (t + .5 / len(pts)))))
        d.line([pts[i], pts[i + 1]], fill=col, width=ww)

# ---- hierba ----
img = Image.new('RGBA', (N, N), (122, 204, 58, 255))
blobs = layer((170, 222, 70))
P = [(random.uniform(0, N), random.uniform(0, N), random.uniform(30, 70)) for _ in range(14)]
wrap_draw(blobs, lambda d, ox, oy: [d.ellipse([x + ox - r, y + oy - r * .7, x + ox + r, y + oy + r * .7], fill=(170, 222, 70, 110)) for x, y, r in P])
img = Image.alpha_composite(img, blobs.filter(ImageFilter.GaussianBlur(14)))
B = []
for _ in range(170):
    x, y = random.uniform(0, N), random.uniform(0, N); h = random.uniform(12, 24); lean = random.uniform(-4, 4)
    col = random.choice([(96, 176, 44, 200), (150, 214, 70, 210), (176, 226, 90, 190)])
    B.append((x, y, h, lean, col))
def blades(d, ox, oy):
    for x, y, h, lean, col in B:
        stroke(d, [(x + ox, y + oy), (x + ox + lean * .5, y + oy - h * .5), (x + ox + lean, y + oy - h)], col, 3)
for c in set(b[4] for b in B):
    bl = layer(c); sub = [b for b in B if b[4] == c]
    wrap_draw(bl, lambda d, ox, oy: [stroke(d, [(x + ox, y + oy), (x + ox + lean * .5, y + oy - h * .5), (x + ox + lean, y + oy - h)], col, 5) for x, y, h, lean, col in sub])
    img = Image.alpha_composite(img, bl.filter(ImageFilter.GaussianBlur(.7)))
img.convert('RGB').save(f'{out}/hierba.webp', quality=90)

# ---- agua ----
W = Image.new('RGBA', (N, N), (62, 196, 200, 255))
S = []
for _ in range(55):
    y = random.uniform(0, N); x = random.uniform(0, N); L = random.uniform(120, 260); a = random.uniform(3, 7); ph = random.uniform(0, 6)
    col = random.choice([(128, 228, 226, 170), (128, 228, 226, 170), (48, 170, 178, 120), (170, 240, 236, 140)])
    S.append((x, y, L, a, ph, col, random.uniform(5, 11)))
def waves(d, ox, oy):
    for x, y, L, a, ph, col, w in S:
        pts = [(x + ox + t, y + oy + a * math.sin(t / L * 2 * math.pi + ph) - t * .12) for t in np.linspace(0, L, 24)]
        stroke(d, pts, col, w)
for c in set(v[5] for v in S):
    lay = layer(c); sub = [v for v in S if v[5] == c]
    wrap_draw(lay, lambda d, ox, oy: [stroke(d, [(x + ox + t, y + oy + a * math.sin(t / L * 2 * math.pi + ph)) for t in np.linspace(0, L, 24)], col, w) for x, y, L, a, ph, col, w in sub])
    W = Image.alpha_composite(W, lay.filter(ImageFilter.GaussianBlur(2.2)))
gl = layer((255, 255, 255))
G = [(random.uniform(0, N), random.uniform(0, N), random.uniform(2, 6)) for _ in range(40)]
wrap_draw(gl, lambda d, ox, oy: [d.ellipse([x + ox - r * 1.8, y + oy - r * .6, x + ox + r * 1.8, y + oy + r * .6], fill=(255, 255, 255, 230)) for x, y, r in G])
W = Image.alpha_composite(W, gl.filter(ImageFilter.GaussianBlur(.5)))
W.convert('RGB').save(f'{out}/agua.webp', quality=90)
print('ok')
