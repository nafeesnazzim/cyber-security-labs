# Usage: python3 redact_blur.py in.png out.png "secret1" "secret2" ...
# Blurs every OCR word box that matches (or is part of) a secret. Prints matched/unmatched secrets.
import sys, re, difflib
from PIL import Image, ImageFilter, ImageOps
import pytesseract
src, dst, secrets = sys.argv[1], sys.argv[2], [s for s in sys.argv[3:] if s]
img = Image.open(src).convert("RGB")
scale = 2
big = ImageOps.grayscale(img).resize((img.width*scale, img.height*scale))
found = set()
for inv in (False, True):  # dark-on-light and light-on-dark terminals
    probe = ImageOps.invert(big) if inv else big
    d = pytesseract.image_to_data(probe, output_type=pytesseract.Output.DICT, config="--psm 6")
    for i, w in enumerate(d["text"]):
        w = w.strip()
        if len(w) < 3: continue
        nw = re.sub(r'\W','',w).lower()
        for s in secrets:
            ns = re.sub(r'\W','',s).lower()
            if not nw: continue
            if (nw in ns and len(nw) >= 3) or ns in nw or difflib.SequenceMatcher(None, nw, ns).ratio() >= 0.7 \
               or any(difflib.SequenceMatcher(None, nw, ns[i:i+len(nw)]).ratio() >= 0.8 for i in range(max(1, len(ns)-len(nw)+1))):
                x, y, bw, bh = (v//scale for v in (d["left"][i], d["top"][i], d["width"][i], d["height"][i]))
                pad = 4
                box = (max(0,x-pad), max(0,y-pad), min(img.width,x+bw+pad), min(img.height,y+bh+pad))
                img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(12)).filter(ImageFilter.GaussianBlur(12)), box)
                found.add(s)
img.save(dst)
print("MATCHED:", sorted(found)); print("UNMATCHED:", sorted(set(secrets)-found))
sys.exit(0 if found == set(secrets) else 2)
