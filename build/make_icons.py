"""Draw the app icon (winding road with a walker) at the sizes iOS and Android need."""
import math
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bezier(p0, p1, p2, p3, n=60):
    for i in range(n + 1):
        t = i / n
        yield tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * d
                    for a, b, c, d in zip(p0, p1, p2, p3))


def icon(size):
    s = 4  # supersample
    W = size * s
    img = Image.new("RGB", (W, W))
    px = img.load()
    c1, c2 = (43, 102, 207), (122, 77, 224)
    for y in range(W):
        for x in range(0, W):
            k = (x + y) / (2 * W)
            px[x, y] = tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))
    d = ImageDraw.Draw(img)
    u = W / 100
    pts = list(bezier((22 * u, -5 * u), (22 * u, 35 * u), (78 * u, 30 * u), (78 * u, 55 * u))) + \
        list(bezier((78 * u, 55 * u), (78 * u, 80 * u), (30 * u, 75 * u), (30 * u, 110 * u)))
    d.line(pts, fill=(20, 32, 43), width=int(17 * u), joint="curve")
    d.line(pts, fill=(110, 122, 134), width=int(13 * u), joint="curve")
    for i in range(0, len(pts) - 3, 8):
        d.line(pts[i:i + 4], fill=(255, 255, 255), width=int(1.6 * u))
    trail = pts[:70]
    d.line(trail, fill=(255, 212, 59), width=int(4 * u), joint="curve")
    # walker at the end of the trail
    x, y = trail[-1]
    d.ellipse([x - 7 * u, y - 2 * u, x + 7 * u, y + 2 * u], fill=(20, 32, 43))
    d.rounded_rectangle([x - 9 * u, y - 21 * u, x - 3 * u, y - 12 * u], radius=2 * u, fill=(255, 212, 59))
    d.rounded_rectangle([x - 5 * u, y - 23 * u, x + 5 * u, y - 10 * u], radius=4 * u, fill=(255, 255, 255))
    d.line([(x - 2 * u, y - 11 * u), (x - 2 * u, y - 1 * u)], fill=(44, 62, 87), width=int(3 * u))
    d.line([(x + 2 * u, y - 11 * u), (x + 2 * u, y - 1 * u)], fill=(44, 62, 87), width=int(3 * u))
    d.ellipse([x - 5.5 * u, y - 34 * u, x + 5.5 * u, y - 23 * u], fill=(242, 194, 155))
    d.pieslice([x - 5.6 * u, y - 34.5 * u, x + 5.6 * u, y - 24 * u], 180, 360, fill=(59, 42, 32))
    # finish flag
    fx, fy = 70 * u, 14 * u
    d.line([(fx, fy), (fx, fy + 16 * u)], fill=(255, 255, 255), width=int(1.5 * u))
    for i in range(4):
        for j in range(3):
            d.rectangle([fx + i * 3 * u, fy + j * 3 * u, fx + (i + 1) * 3 * u, fy + (j + 1) * 3 * u],
                        fill=(255, 255, 255) if (i + j) % 2 else (20, 32, 43))
    return img.resize((size, size), Image.LANCZOS)


for n in (180, 192, 512):
    icon(n).save(os.path.join(ROOT, "icons", f"icon-{n}.png"), optimize=True)
print("icons ok")
