# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 4.4 · The data-handling note
#
# Day 4 · Session 4 (Voice, faces and consent) · 25 min.
#
# Ghusoun Al-Mutlaq, the authority's data protection officer, will not approve the launch without a data-handling
# note: what Lamha and Rahhal collect, how each item is classified and how long it is kept, and evidence that the
# controls work. You inventory the data, blur the faces in the trail photos, redact identifiers from call transcripts,
# set retention, and time the line that tells callers they are speaking to an automated assistant with a synthetic voice.
#
# **Reference state.** The 60 photos with face boxes in `data/photos/refs.jsonl`, ten transcript lines in
# `data/transcripts_sample.jsonl` (synthetic numbers and example addresses), and the synthesis helper of Lab 3.1.
#
# The classification and retention periods below are **the case study's choices**, written to be discussed against the
# Personal Data Protection Law and the national data classification policy; they are not legal advice.
#
# **Tasks**
# - [ ] 1 · Inventory the data and classify it (6')
# - [ ] 2 · Blur the faces in the photos (7')
# - [ ] 3 · Redact identifiers and set retention (6')
# - [ ] 4 · The disclosure line and when it is said (6')
# - [ ] ✱ Stretch · Delete one caller's data on withdrawal of consent

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/ae-408.git"
    if not Path("/content/ae-408").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/ae-408"], check=True)
    os.chdir("/content/ae-408/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("trails.py").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import re

import numpy as np
import pandas as pd
from PIL import ImageFilter

import trails as U

TRANSCRIPTS = U.jsonl("transcripts_sample.jsonl")
with_faces = [r for r in U.photo_refs() if r["faces"]]
print(len(with_faces), "of 60 photos show at least one face;", len(TRANSCRIPTS), "transcript lines")

# %% [markdown]
# ## 1 · Inventory (6')
#
# ✏️ **Exercise** · Complete the inventory: one row per item the two services handle, with `personal` (does it
# identify a person, alone or with other data?), `class` (the case study's scheme: `public`, `restricted`,
# `confidential`) and `keep_days`. Add at least the caller's audio and the redacted transcript.

# %%
INVENTORY = [
    {"item": "trail photo as uploaded", "service": "Lamha", "personal": True, "class": "confidential", "keep_days": 7},
    {"item": "trail photo with faces blurred", "service": "Lamha", "personal": False, "class": "restricted", "keep_days": 365},
    {"item": "incident record (fields)", "service": "Lamha", "personal": False, "class": "restricted", "keep_days": 365},
    {"item": "booking (name, phone, site, date, party)", "service": "Rahhal", "personal": True, "class": "confidential", "keep_days": 90},
]
# BEGIN SOLUTION
INVENTORY += [
    {"item": "caller audio", "service": "Rahhal", "personal": True, "class": "confidential", "keep_days": 0},
    {"item": "full transcript", "service": "Rahhal", "personal": True, "class": "confidential", "keep_days": 30},
    {"item": "redacted transcript", "service": "Rahhal", "personal": False, "class": "restricted", "keep_days": 365},
    {"item": "latency trace (no text)", "service": "Rahhal", "personal": False, "class": "restricted", "keep_days": 365},
]
# END SOLUTION

# %%
inv = pd.DataFrame(INVENTORY)
# Voice and faces: the course treats voiceprints and face images as sensitive personal data (biometric data when they
# can identify someone), on top of the class. Items that hold a voice or a face are flagged and kept shortest.
inv["sensitive"] = inv["item"].isin(["trail photo as uploaded", "caller audio"])
print(inv.to_string(index=False))
if {"caller audio", "redacted transcript"} <= set(inv["item"]):
    U.check(True, "the inventory covers the caller's audio and the redacted transcript")
else:
    print("✏️ not done yet: add the caller's audio and the redacted transcript to the inventory")
U.check((inv[inv.personal]["class"] == "confidential").all(), "every personal item has the highest class in the scheme")
U.check((inv[inv.sensitive].keep_days <= 7).all(), "items holding a voice or a face are kept seven days or less")

# %% [markdown]
# 🔍 **Look at** `keep_days = 0` for caller audio: the case study keeps no audio once the call is transcribed. It also
# means the Day 2 evaluation cannot be repeated on production calls without a separate, consented collection.

# %% [markdown]
# ## 2 · Blur the faces (7')
#
# ✏️ **Exercise** · `blur_faces(photo_id)` returns the photo at width 640 (the frame of the face boxes) with every
# box in `faces` replaced by a strong Gaussian blur. Check it: the pixel standard deviation inside each face box must
# fall by more than half, and the pixels outside the boxes must not change.

# %%
def blur_faces(photo_id, radius=16):
    img = U.photo(photo_id, 640)
    # BEGIN SOLUTION
    for box in U.REFS[photo_id]["faces"]:
        x0, y0, x1, y1 = box
        pad = 4
        region = (max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad))
        img.paste(img.crop(region).filter(ImageFilter.GaussianBlur(radius)), region[:2])
    # END SOLUTION
    return img


# %%
def face_spread(img, box):
    return float(np.asarray(img.crop(tuple(box)).convert("L"), dtype=float).std())


def outside_unchanged(a, b, boxes, pad=4):
    x, y = np.asarray(a, dtype=int), np.asarray(b, dtype=int)
    mask = np.ones(x.shape[:2], bool)
    for x0, y0, x1, y1 in boxes:
        mask[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad] = False
    return bool((x[mask] == y[mask]).all())


def _blur_ref(photo_id, radius=16):
    img = U.photo(photo_id, 640)
    for x0, y0, x1, y1 in U.REFS[photo_id]["faces"]:
        region = (max(0, x0 - 4), max(0, y0 - 4), min(img.width, x1 + 4), min(img.height, y1 + 4))
        img.paste(img.crop(region).filter(ImageFilter.GaussianBlur(radius)), region[:2])
    return img


try:
    blur_faces(with_faces[0]["photo_id"])
except NotImplementedError:
    print("✏️ not done yet: using the reference blur so the rest of the lab runs")
    blur_faces = _blur_ref
rows = []
for r in U.pick(with_faces, with_faces[:6]):
    before, after = U.photo(r["photo_id"], 640), blur_faces(r["photo_id"])
    for box in r["faces"]:
        rows.append({"photo": r["photo_id"], "before": round(face_spread(before, box), 1),
                     "after": round(face_spread(after, box), 1), "outside_same": outside_unchanged(before, after, r["faces"])})
faces = pd.DataFrame(rows)
print(faces.head(8).to_string(index=False), f"\n... {len(faces)} faces")
blurred = (faces.after < faces.before / 2).mean()
print(f"faces blurred: {blurred:.0%}")
if blurred < 1:
    print("✏️ not done yet: blur_faces leaves faces sharp")
else:
    U.check(faces.outside_same.all(), "only the face regions changed")
    out = U.artifacts("D4_4")
    blur_faces(with_faces[0]["photo_id"]).save(out / f"{with_faces[0]['photo_id']}_blurred.png")

# %% [markdown]
# ## 3 · Redact and keep (6')
#
# ✏️ **Exercise** · `redact(text)` replaces Saudi mobile numbers (`05` and 8 digits), national and resident ID numbers
# (10 digits starting with 1 or 2) and email addresses with `[PHONE]`, `[ID]` and `[EMAIL]`. Booking codes such as
# HTB-4821 must stay: the caller needs them.

# %%
def redact(text):
    # BEGIN SOLUTION
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", text)
    text = re.sub(r"(?<!\d)05\d{8}(?!\d)", "[PHONE]", text)
    text = re.sub(r"(?<!\d)[12]\d{9}(?!\d)", "[ID]", text)
    return text
    # END SOLUTION


# %%
def _redact_ref(text):
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", text)
    text = re.sub(r"(?<!\d)05\d{8}(?!\d)", "[PHONE]", text)
    return re.sub(r"(?<!\d)[12]\d{9}(?!\d)", "[ID]", text)


try:
    redact("x")
except NotImplementedError:
    redact = _redact_ref
red = [{"call_id": t["call_id"], "redacted": redact(t["text"])} for t in TRANSCRIPTS]
for r in red:
    print(r["call_id"], r["redacted"])
left = [r for r in red if re.search(r"\d{9,}|@", r["redacted"])]
U.check(not left and any("HTB-4821" in r["redacted"] for r in red), "no identifier left, and the booking code kept")

# %% [markdown]
# ## 4 · The disclosure line (6')
#
# The national Deepfakes Guidelines ask for synthetic content to be disclosed and labelled. Rahhal's voice is
# synthetic: the case study's rule is that the first thing every caller hears says so, in the caller's language,
# in under 6 seconds, before Rahhal asks for any personal data.
#
# ✏️ **Exercise** · Write the two lines, measure their spoken length with `U.synthesise`, and check the opening turn
# of a scripted call: the disclosure comes first, and no question about a name or a number comes before it.

# %%
# BEGIN SOLUTION
DISCLOSURE = {
    "ar": "مسارات التراث. أنا رحّال، مساعد آلي بصوت مولّد.",
    "en": "This is Rahhal, an automated assistant with a generated voice.",
}
# END SOLUTION

# %%
try:
    DISCLOSURE
except NameError:
    DISCLOSURE = {"ar": "أنا رحّال، مساعد آلي بصوت مولّد.", "en": "I am Rahhal, an automated assistant with a generated voice."}
lengths = {lang: U.synthesise(text, lang).extra["seconds"] for lang, text in DISCLOSURE.items()}
print("spoken length (s):", lengths, "| synthesis:", "hosted" if U.hosted("speech") else "stand-in estimate")
opening = [DISCLOSURE["ar"], "أي موقع تحب تزور؟", "لعدد كم شخص؟", "باسم من الحجز؟"]
first_personal = next(i for i, line in enumerate(opening) if "باسم" in line or "جوال" in line)
U.check(all(s < 6 for s in lengths.values()) and first_personal > 0 and ("آلي" in opening[0] and "مولّد" in opening[0]),
        "the disclosure is under 6 seconds and comes before any personal question")

# %% [markdown]
# ## ✱ Stretch · Withdrawal of consent
#
# A caller withdraws consent. Delete every item the inventory marks as personal for that caller (booking, full
# transcript), keep what is not personal, and print a deletion receipt that names what was deleted, without
# repeating the personal data.

# %%
# BEGIN SOLUTION
store = {"bookings": [{"ref": "HTB-4821", "name": "R01", "phone": "0551234567"}, {"ref": "HTB-1590", "name": "R02", "phone": "0509876543"}],
         "transcripts": {t["call_id"]: t["text"] for t in TRANSCRIPTS},
         "redacted": {r["call_id"]: r["redacted"] for r in red}}
caller = "R01"
deleted = {"bookings": sum(b["name"] == caller for b in store["bookings"]), "transcripts": int(caller in store["transcripts"])}
store["bookings"] = [b for b in store["bookings"] if b["name"] != caller]
store["transcripts"].pop(caller, None)
print({"caller": caller, "deleted": deleted, "kept": ["redacted transcript"], "date": U.TODAY})
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why keep the photo with faces blurred and not the photo as uploaded?
# 2. Why must the redaction keep HTB-4821?
# 3. Why is the disclosure said before the first question, not at the end of the call?
#
# <details><summary>Answers</summary>
#
# 1. The incident needs the scene, not the people in it; the blurred copy serves the rangers and is no longer personal.
# 2. It identifies a booking, not a person, and the caller needs it; over-redaction breaks the service.
# 3. The caller decides what to say knowing it is an automated system with a synthetic voice; told afterwards, they
#    could not.
# </details>
#
# **Carry forward.** The inventory, the redaction and the disclosure go into the capstone's data-handling note.
