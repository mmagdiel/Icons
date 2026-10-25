import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import render
from PIL import Image, ImageDraw
png = os.path.abspath("png")
pairs = [("search","search-outline"),("arrow-left","arrow-left-outline"),
         ("arrow-right","arrow-right-outline"),("arrow-down","arrow-down-outline"),
         ("arrow-up-right","diagonal-arrow-right-up-outline"),("mail","email-outline")]
for n,_ in pairs:
    render(f"svg/{n}.svg", 320, os.path.join(png, f"pencil-{n}.png"))
cell=300; pad=12
W = 2*cell + 3*pad; H = len(pairs)*(cell+pad)+pad
c = Image.new("RGB",(W,H),(255,255,255)); d = ImageDraw.Draw(c)
for i,(n,src) in enumerate(pairs):
    y = pad + i*(cell+pad)
    o = Image.open(os.path.join(png,f"orig-{src}.png")).convert("RGBA").resize((cell,cell),Image.LANCZOS)
    p = Image.open(os.path.join(png,f"pencil-{n}.png")).convert("RGBA").resize((cell,cell),Image.LANCZOS)
    c.paste(o,(pad,y),o); c.paste(p,(pad*2+cell,y),p)
    d.rectangle([pad,y,pad+cell,y+cell],outline=(225,225,225))
    d.rectangle([pad*2+cell,y,pad*2+2*cell,y+cell],outline=(225,225,225))
    d.text((pad+6,y+6), n, fill=(120,120,120))
c.save("/tmp/cmp3.png"); print("ok /tmp/cmp3.png")
