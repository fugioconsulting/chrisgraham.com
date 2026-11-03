#!/usr/bin/env python3
"""Booking photos that arrive in FOI records replies. Same bar as a news photo: the record itself must name the person on
the photo, it must show one face, and a listed case must still have no photo. Faces are located, never matched or identified.

  python3 scripts/grooming/foi_photos.py <reply folder>...          # report only
  python3 scripts/grooming/foi_photos.py --apply <reply folder>...  # save docs/grooming/img/<num>_<last>.jpg, set thumb

A photo is tied to a person only when, in the same record, exactly one listed person's first and last name appears in
(1) the image's file name, else (2) the text of the PDF page the image sits on, else (3) the reply body when the reply
carries exactly one face photo. Anything else is held. Every saved photo gets a line in data/grooming/photo_sources.csv.
Needs macOS (Vision, via eyes.swift), Pillow, and poppler (pdfimages, pdftotext)."""
import csv, os, re, subprocess, sys, tempfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
CASES = os.path.join(ROOT, "data/grooming/cases.csv"); IMG = os.path.join(ROOT, "docs/grooming/img")
SOURCES = os.path.join(ROOT, "data/grooming/photo_sources.csv")
TMP = tempfile.mkdtemp(prefix="foiph"); EYES = os.path.join(tempfile.gettempdir(), "grooming_eyes")
EXT = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic")

def eyes(paths):
    if not os.path.exists(EYES): subprocess.run(["swiftc", "-O", HERE + "/eyes.swift", "-o", EYES], check=True, capture_output=True)
    out = {}
    for l in subprocess.run([EYES, *paths], capture_output=True, text=True).stdout.splitlines():
        f = l.split("\t"); out[f[0]] = f
    return out

def words(s): return set(re.findall(r"[a-z]+", s.lower().replace("_", " ")))

def named(text, rows):
    w = words(text)
    return [r for r in rows if {r["name"].split()[0].lower(), re.sub(r"[^a-z]", "", r["name"].split()[-1].lower())} <= w
            or (r["name"].split()[-1].lower() in ("jr.", "jr", "iii", "ii") and {r["name"].split()[0].lower(), r["name"].split()[-2].lower()} <= w)]

def images(folder):
    """(image path, context text) for every picture in a reply: attachments and pictures inside PDFs."""
    body = open(os.path.join(folder, "body.txt"), errors="ignore").read() if os.path.exists(os.path.join(folder, "body.txt")) else ""
    for f in sorted(os.listdir(folder)):
        p = os.path.join(folder, f)
        if f.lower().endswith(EXT): yield p, f, "", body
        elif f.lower().endswith(".pdf"):
            pre = os.path.join(TMP, re.sub(r"\W", "_", folder[-24:] + f))
            subprocess.run(["pdfimages", "-png", "-p", p, pre], capture_output=True)
            for g in sorted(x for x in os.listdir(TMP) if x.startswith(os.path.basename(pre))):
                pg = re.search(r"-(\d+)-\d+\.png$", g).group(1)
                page = subprocess.run(["pdftotext", "-layout", "-f", pg, "-l", pg, p, "-"], capture_output=True, text=True).stdout
                yield os.path.join(TMP, g), f"{f} page {int(pg)}", page, body

def main():
    apply = "--apply" in sys.argv; folders = [a for a in sys.argv[1:] if a != "--apply"]
    rows = list(csv.DictReader(open(CASES, encoding="utf-8"))); cols = list(rows[0].keys())
    report, saved = [], []
    for folder in folders:
        req = (re.search(r"FOI-\d+", os.path.abspath(folder)) or re.search(r"", "")).group() or os.path.basename(folder)
        cand = []
        for p, label, page, body in images(folder):
            try:
                im = Image.open(p); w, h = im.size
            except Exception: continue
            if min(w, h) < 120 or os.path.getsize(p) < 6000: continue          # signature logos and icons
            cand.append((p, label, page, body))
        faces = eyes([c[0] for c in cand]) if cand else {}
        one = [c for c in cand if faces.get(c[0], ["", "", "", "NOFACE"])[3] != "NOFACE" and faces[c[0]][7] == "1"]
        for p, label, page, body in cand:
            f = faces.get(p, ["", "", "", "NOFACE", "0"])
            if f[3] == "NOFACE": continue
            if f[7] != "1": report.append(f"HOLD {req} {label}: {f[7]} faces"); continue
            who = named(label, rows) or named(page, rows) or (named(body, rows) if len(one) == 1 else [])
            why = "file name" if named(label, rows) else "PDF page text" if named(page, rows) else "reply body, only photo in the reply"
            if len(who) != 1: report.append(f"HOLD {req} {label}: record names {len(who)} listed people with this photo"); continue
            r = who[0]
            if r["thumb"]: report.append(f"SKIP {req} {label}: {r['name']} already has a photo"); continue
            if r["name"] in saved: continue
            lx, ly, rx, ry = map(float, f[3:7]); cx, cy = (lx + rx) / 2, (ly + ry) / 2
            im = Image.open(p).convert("RGB"); W, H = im.size
            s = min(W, H, max(abs(rx - lx) * 4.5, 120)); x0 = min(max(cx - s / 2, 0), W - s); y0 = min(max(cy - s * .4, 0), H - s)
            key = f"{int(r['num']):02d}_{re.sub(r'[^a-z]', '', r['name'].split()[-1].lower() if r['name'].split()[-1].lower() not in ('jr.','jr','ii','iii') else r['name'].split()[-2].lower())}.jpg"
            report.append(f"PHOTO {req} {label} -> {r['name']} ({why}){'' if apply else ' [report only]'}")
            if apply:
                im.crop((x0, y0, x0 + s, y0 + s)).resize((300, 300), Image.LANCZOS).save(os.path.join(IMG, key), quality=88)
                r["thumb"] = key; saved.append(r["name"])
                new = not os.path.exists(SOURCES)
                with open(SOURCES, "a", newline="") as o:
                    wr = csv.writer(o)
                    if new: wr.writerow(["name", "thumb", "origin", "file", "tied_by"])
                    wr.writerow([r["name"], key, f"{req} records reply", label, why])
    if saved:
        with open(CASES, "w", newline="", encoding="utf-8") as o:
            wr = csv.DictWriter(o, fieldnames=cols); wr.writeheader(); wr.writerows(rows)
    print("\n".join(report) or "no booking photos in these replies")

if __name__ == "__main__": main()
