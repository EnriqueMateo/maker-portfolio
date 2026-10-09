# Recorta un render transparente a un retrato cuadrado: python portrait_crop.py in.png out.webp [tam]
import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; size = int(sys.argv[3]) if len(sys.argv) > 3 else 384
im = Image.open(src).convert('RGBA'); x0, y0, x1, y1 = im.getbbox()
side = int(max(x1 - x0, y1 - y0) * 1.06); cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
sq = Image.new('RGBA', (side, side), (0, 0, 0, 0)); sq.paste(im.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)), (0, 0))
sq.resize((size, size), Image.LANCZOS).save(out, quality=90, method=6)
