#!/usr/bin/env python3
"""Render SVG -> PNG with macOS WebKit (qlmanage). Same engine as Safari."""
import subprocess, sys, os, glob, tempfile, shutil
from PIL import Image

def render(svg_path, px=256, out=None):
    d = tempfile.mkdtemp(prefix="ql_")
    # qlmanage caches thumbnails by path+mtime and will happily hand back a
    # stale image; render from a unique filename so every run is truthful.
    tag = f"{abs(hash((svg_path, os.path.getmtime(svg_path), px))) % 10**12}"
    staged = os.path.join(d, f"{tag}.svg")
    shutil.copyfile(svg_path, staged)
    try:
        subprocess.run(["qlmanage", "-t", "-s", str(px), "-o", d, staged],
                       check=True, capture_output=True)
        pngs = glob.glob(os.path.join(d, "*.png"))
        if not pngs:
            raise RuntimeError(f"no thumbnail for {svg_path}")
        im = Image.open(pngs[0]).convert("RGBA")
        # composite on white so the mark is readable
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        out = out or os.path.splitext(svg_path)[0] + ".png"
        bg.convert("RGB").save(out)
        return out
    finally:
        shutil.rmtree(d, ignore_errors=True)

def sheet(paths, out, cols=5, cell=192, pad=14, bg=(255,255,255), grid=(228,228,228)):
    rows = (len(paths) + cols - 1) // cols
    W = cols * (cell + pad) + pad
    H = rows * (cell + pad) + pad
    canvas = Image.new("RGB", (W, H), bg)
    from PIL import ImageDraw
    dr = ImageDraw.Draw(canvas)
    for i, p in enumerate(paths):
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = pad + r * (cell + pad)
        dr.rectangle([x, y, x+cell, y+cell], outline=grid)
        im = Image.open(p).convert("RGBA").resize((cell, cell), Image.LANCZOS)
        canvas.paste(im, (x, y), im)
    canvas.save(out)
    return out

if __name__ == "__main__":
    if sys.argv[1] == "sheet":
        sheet(sys.argv[3:-1], sys.argv[-1], cols=int(sys.argv[2]))
    else:
        for p in sys.argv[1:]:
            print(render(p))
