# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 1.3 · Boxes and invented objects
#
# Day 1 · Session 3 (Grounding answers in pixels) · 25 min.
#
# A ranger trusts "rockfall, three rocks on the path" more when each rock has a box he can check. You score the boxes
# the models return against the reference boxes, then ask about objects that are **not** in the photo and flag every
# answer that invents one.
#
# **Reference state.** All 60 photos with reference boxes in `data/photos/refs.jsonl`.
#
# **Tasks**
# - [ ] 1 · Intersection over union for two boxes (6')
# - [ ] 2 · Match boxes and report precision and recall at 0.5 (7')
# - [ ] 3 · Ask about absent objects and flag invented ones (7')
# - [ ] 4 · A grounding score per model (5')
# - [ ] ✱ Stretch · Score point answers: does each point fall inside its reference box?

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

import json
import pandas as pd
from PIL import ImageDraw

import trails as U

PHOTOS = [r["photo_id"] for r in U.photo_refs()][:U.pick(60, 20)]
BOX_PROMPT = ("List every object in the photo that matters to a ranger, as JSON: "
              '[{"label": ..., "box": [x0, y0, x1, y1]}] in pixels of a 640 by 480 image.')
print(len(PHOTOS), "photos")

# %% [markdown]
# ## 1 · Intersection over union (6')
#
# ✏️ **Exercise** · `iou(a, b)` for boxes `[x0, y0, x1, y1]`: the area of the overlap divided by the area of the
# union. Two boxes that do not touch score 0.

# %%
def iou(a, b):
    # BEGIN SOLUTION
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0
    # END SOLUTION


# %%
try:
    tests = [iou([0, 0, 10, 10], [0, 0, 10, 10]), iou([0, 0, 10, 10], [5, 0, 15, 10]), iou([0, 0, 10, 10], [20, 20, 30, 30])]
except NotImplementedError:
    iou = U.iou
    tests = [iou([0, 0, 10, 10], [0, 0, 10, 10]), iou([0, 0, 10, 10], [5, 0, 15, 10]), iou([0, 0, 10, 10], [20, 20, 30, 30])]
print([round(t, 3) for t in tests])
U.check([round(t, 3) for t in tests] == [1.0, 0.333, 0.0], "iou: same box 1, half shift 1/3, apart 0")

# %% [markdown]
# ## 2 · Match and score at 0.5 (7')
#
# ✏️ **Exercise** · `match(pred, ref, thr=0.5)`: pair each predicted box with an unused reference box **of the same
# label**, best IoU first, and count a pair as a hit when IoU ≥ `thr`. Return `(hits, len(pred), len(ref))`.
# Precision is hits over predictions; recall is hits over references.

# %%
def match(pred, ref, thr=0.5):
    # BEGIN SOLUTION
    pairs = sorted(((iou(p["box"], r["box"]), i, j) for i, p in enumerate(pred) for j, r in enumerate(ref)
                    if p["label"] == r["label"]), reverse=True)
    used_p, used_r, hits = set(), set(), 0
    for v, i, j in pairs:
        if v < thr:
            break
        if i in used_p or j in used_r:
            continue
        used_p.add(i); used_r.add(j); hits += 1
    return hits, len(pred), len(ref)
    # END SOLUTION


# %%
def boxes_for(model):
    rows = []
    for pid in PHOTOS:
        pred = json.loads(U.vlm(pid, BOX_PROMPT, model=model, task="objects").text)
        try:
            h, np_, nr = match(pred, U.REFS[pid]["objects"])
        except NotImplementedError:
            h, np_, nr = U.match_boxes(pred, U.REFS[pid]["objects"])
        rows.append({"photo_id": pid, "model": model, "hits": h, "pred": np_, "ref": nr, "boxes": pred})
    return rows


boxes = pd.DataFrame(boxes_for("open") + boxes_for("hosted"))
pr = boxes.groupby("model")[["hits", "pred", "ref"]].sum()
pr["precision"] = (pr.hits / pr.pred).round(3)
pr["recall"] = (pr.hits / pr.ref).round(3)
print(pr.to_string())
U.check((pr.precision > 0).all(), "boxes matched for both models")

# %% [markdown]
# 🔍 **Look at** one photo with its reference boxes (green) and the open model's boxes (red). A box beside the object
# still has the right label: a label-only score would have counted it.

# %%
pid = boxes[(boxes.model == "open") & (boxes.hits < boxes.ref)].photo_id.iloc[0]
img = U.photo(pid)
d = ImageDraw.Draw(img)
for o in U.REFS[pid]["objects"]:
    d.rectangle(o["box"], outline=(0, 160, 0), width=3)
for o in boxes[(boxes.model == "open") & (boxes.photo_id == pid)].boxes.iloc[0]:
    d.rectangle(o["box"], outline=(220, 0, 0), width=2)
img.save(U.artifacts("D1_3") / f"{pid}_boxes.png")
print("drew", pid)
img

# %% [markdown]
# ## 3 · Objects that are not there (7')
#
# A model asked "where is the litter?" tends to find some. A **probe** asks about an object the photo does not
# contain; any "yes" is an invented object.
#
# ✏️ **Exercise** · For every photo without litter, ask `task="probe:litter"` with the prompt below and collect one
# row per photo and model: `photo_id`, `model`, `invented` (the model said it is present). Report the invention rate per
# model, and separately on the clean scenes (`incident_type == "none"`).

# %%
PROBE = 'Is there litter in this photo? Reply as JSON: {"present": true or false, "box": [x0, y0, x1, y1] or null}.'


def probes():
    rows = []
    # BEGIN SOLUTION
    for pid in PHOTOS:
        ref = U.REFS[pid]
        if any(o["label"] == "litter" for o in ref["objects"]):
            continue
        for model in ("open", "hosted"):
            ans = json.loads(U.vlm(pid, PROBE, model=model, task="probe:litter").text)
            rows.append({"photo_id": pid, "model": model, "invented": bool(ans["present"]),
                         "clean": ref["fields"]["incident_type"] == "none"})
    # END SOLUTION
    return pd.DataFrame(rows)


# %%
try:
    pb = probes()
except NotImplementedError:
    pb = pd.DataFrame([{"photo_id": p, "model": m, "invented": json.loads(U.vlm(p, PROBE, model=m, task="probe:litter").text)["present"],
                        "clean": U.REFS[p]["fields"]["incident_type"] == "none"}
                       for p in PHOTOS if not any(o["label"] == "litter" for o in U.REFS[p]["objects"]) for m in ("open", "hosted")])
inv = pb.groupby("model").invented.mean().round(3).to_frame("all_without_litter")
inv["clean_scenes"] = pb[pb.clean].groupby("model").invented.mean().round(3)
print(inv.to_string())
U.check(inv.loc["open", "all_without_litter"] >= inv.loc["hosted", "all_without_litter"], "the open model invents at least as often as the hosted one", model=True)

# %% [markdown]
# ## 4 · One grounding score per model (5')
#
# ✏️ **Exercise** · Combine into one table per model: box precision, box recall, and the probe invention rate; then a
# `grounding` score defined as the harmonic mean of precision and recall times (1 minus the invention rate). Write
# the definition beside the number in the report: a score nobody can recompute is not a score.

# %%
def grounding(pr, inv):
    # BEGIN SOLUTION
    t = pr[["precision", "recall"]].copy()
    t["invention_rate"] = inv["all_without_litter"]
    f1 = 2 * t.precision * t.recall / (t.precision + t.recall)
    t["grounding"] = (f1 * (1 - t.invention_rate)).round(3)
    return t
    # END SOLUTION


# %%
try:
    g = grounding(pr, inv)
except NotImplementedError:
    g = pr[["precision", "recall"]].copy()
    g["invention_rate"] = inv["all_without_litter"]
    g["grounding"] = (2 * g.precision * g.recall / (g.precision + g.recall) * (1 - g.invention_rate)).round(3)
print(g.to_string())
U.check(0 < g.grounding.min() <= g.grounding.max() <= 1, "grounding scores between 0 and 1")
g.to_csv(U.artifacts("D1_3") / "grounding.csv")

# %% [markdown]
# ## ✱ Stretch · Points instead of boxes
#
# Some models answer with a point. A point is right when it falls inside the reference box of the same label. Use the
# centre of each returned box as the point and compare the point score with the box score at IoU 0.5.

# %%
# BEGIN SOLUTION
inside = total = 0
for _, r in boxes[boxes.model == "open"].iterrows():
    for p in r.boxes:
        cx, cy = (p["box"][0] + p["box"][2]) / 2, (p["box"][1] + p["box"][3]) / 2
        total += 1
        inside += any(o["label"] == p["label"] and o["box"][0] <= cx <= o["box"][2] and o["box"][1] <= cy <= o["box"][3]
                      for o in U.REFS[r.photo_id]["objects"])
print(f"points inside their box: {inside}/{total} = {inside / total:.3f} | box precision: {pr.loc['open', 'precision']}")
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. A box overlaps its rock with IoU 0.3. Is the rock grounded at your threshold? What would change your threshold?
# 2. Why probe with absent objects instead of only scoring the boxes the model chose to return?
# 3. On which scenes did the open model invent most, and what does that say about a "report litter" button?
#
# <details><summary>Answers</summary>
#
# 1. Not at 0.5. A threshold follows the use: rangers locating a rock on a path need less overlap than a crop for a
#    second model.
# 2. Returned boxes only measure what the model chose to say; probes measure what it says when the right answer is no.
# 3. Clean scenes: a question that presumes litter invites invented litter, so the button's prompt must allow "none".
# </details>
#
# **Carry forward.** The grounding table in `artifacts/D1_3/grounding.csv` is the image half of the capstone's
# evaluation.
