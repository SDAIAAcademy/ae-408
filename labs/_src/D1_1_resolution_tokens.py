# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 1.1 · One question, three resolutions
#
# Day 1 · Session 1 (How a vision-language model sees) · 25 min.
#
# Salem Al-Balawi, chief ranger, wants **Lamha** to read the trail-marker code (`HT-07`) on every photo a visitor
# sends, so each report lands on the right site. You ask one question of 20 photos at three widths and measure what
# each width costs in tokens and time and what it buys in accuracy.
#
# **Reference state.** The photos and their reference codes in `data/photos/`. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Load the photos, the question and the reference codes (4')
# - [ ] 2 · Send each photo at three resolutions; record tokens and latency (7')
# - [ ] 3 · Score the answers against the reference codes (7')
# - [ ] 4 · One table and the cheapest resolution that reaches 90% (7')
# - [ ] ✱ Stretch · Crop the marker region and ask again at the lowest resolution

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
import pandas as pd
import trails as U

print("vision path:", "hosted " + U.VLM_MODELS["open"] if U.hosted("vision") else "scripted stand-in")

# %% [markdown]
# ## 1 · The photos, the question and the reference codes (4')
#
# ✏️ **Exercise** · Build `items`: one dict per photo that shows a trail marker (`fields.site_code` is not `None`),
# with `photo_id`, `code` (the reference) and `marker_px` (the height of the marker's text in the full photo).
# Keep the first 20 (`U.pick(20, 8)` in quick mode).

# %%
QUESTION = ("What is the code on the trail-marker post in this photo? It looks like HT-07. "
            "Answer with the code only, or 'no marker'.")
WIDTHS = [320, 640, 1280]


def load_items(n):
    # BEGIN SOLUTION
    rows = [{"photo_id": r["photo_id"], "code": r["fields"]["site_code"], "marker_px": r["marker_px"]}
            for r in U.photo_refs() if r["fields"]["site_code"] is not None]
    return rows[:n]
    # END SOLUTION


# %%
try:
    items = load_items(U.pick(20, 8))
except NotImplementedError:
    items = [{"photo_id": r["photo_id"], "code": r["fields"]["site_code"], "marker_px": r["marker_px"]}
             for r in U.photo_refs() if r["fields"]["site_code"]][:U.pick(20, 8)]
print(len(items), "photos; first:", items[0])
U.check(len(items) == U.pick(20, 8) and all(i["code"].startswith("HT-") for i in items), "items hold reference codes")
U.photo(items[0]["photo_id"], 320)

# %% [markdown]
# ## 2 · Three resolutions, tokens and latency (7')
#
# `U.vlm(photo_id, prompt, model=..., width=..., task="marker")` returns a `Reply` with `text`, `prompt_tokens`,
# `completion_tokens` and `latency_ms`. The photo is resized to `width` before it is sent, keeping its shape.
#
# ✏️ **Exercise** · For every photo and every width, ask `QUESTION` of the `open` model and keep one row:
# `photo_id`, `width`, `answer`, `prompt_tokens`, `latency_ms`.

# %%
def run_widths(items, widths, model="open"):
    rows = []
    # BEGIN SOLUTION
    for it in items:
        for w in widths:
            r = U.vlm(it["photo_id"], QUESTION, model=model, width=w, task="marker")
            rows.append({"photo_id": it["photo_id"], "width": w, "answer": r.text.strip(),
                         "prompt_tokens": r.prompt_tokens, "latency_ms": r.latency_ms})
    # END SOLUTION
    return pd.DataFrame(rows)


# %%
try:
    runs = run_widths(items, WIDTHS)
except NotImplementedError:
    runs = pd.DataFrame([{"photo_id": it["photo_id"], "width": w, "answer": (r := U.vlm(it["photo_id"], QUESTION, width=w, task="marker")).text,
                          "prompt_tokens": r.prompt_tokens, "latency_ms": r.latency_ms} for it in items for w in WIDTHS])
print(runs.groupby("width")[["prompt_tokens", "latency_ms"]].mean().round(0))
U.check(runs.groupby("width").prompt_tokens.mean().is_monotonic_increasing, "tokens grow with resolution")

# %% [markdown]
# 🔍 **Look at** the token column: doubling the width multiplies the image tokens by about four, because tokens follow
# the area. The text of the question is the same in every row.

# %% [markdown]
# ## 3 · Score the answers (7')
#
# ✏️ **Exercise** · Write `clean(answer)` that pulls the first `HT-` code out of a reply (models add words, quotes or a
# full stop) and returns it in capitals, or `None`. Then add a column `correct` to `runs`.

# %%
def clean(answer):
    # BEGIN SOLUTION
    m = re.search(r"HT\s*-?\s*(\d{2})", answer.upper())
    return f"HT-{m.group(1)}" if m else None
    # END SOLUTION


# %%
try:
    assert clean("The code is ht-07.") == "HT-07" and clean("no marker") is None
except NotImplementedError:
    clean = lambda a: (lambda m: f"HT-{m.group(1)}" if m else None)(re.search(r"HT\s*-?\s*(\d{2})", a.upper()))
ref = {it["photo_id"]: it["code"] for it in items}
runs["correct"] = [clean(a) == ref[p] for p, a in zip(runs.photo_id, runs.answer)]
print(runs.groupby("width").correct.mean())
U.check(clean("Code: HT 11") == "HT-11", "clean() reads a code with a missing dash")

# %% [markdown]
# ## 4 · One table, one decision (7')
#
# ✏️ **Exercise** · Build `table`: one row per width with `accuracy`, mean `prompt_tokens`, median `latency_ms` and the
# relative cost (tokens divided by the tokens at 320). Then set `choice` to the **smallest width whose accuracy is at
# least 0.9**, or `None` if no width reaches it.

# %%
def summarise(runs):
    # BEGIN SOLUTION
    t = runs.groupby("width").agg(accuracy=("correct", "mean"), prompt_tokens=("prompt_tokens", "mean"),
                                  latency_ms=("latency_ms", "median"))
    t["relative_cost"] = (t.prompt_tokens / t.prompt_tokens.iloc[0]).round(2)
    ok = t[t.accuracy >= 0.9]
    return t.round(2), (int(ok.index.min()) if len(ok) else None)
    # END SOLUTION


# %%
try:
    table, choice = summarise(runs)
except NotImplementedError:
    t = runs.groupby("width").agg(accuracy=("correct", "mean"), prompt_tokens=("prompt_tokens", "mean"), latency_ms=("latency_ms", "median"))
    t["relative_cost"] = (t.prompt_tokens / t.prompt_tokens.iloc[0]).round(2)
    table, choice = t.round(2), (int(t[t.accuracy >= 0.9].index.min()) if (t.accuracy >= 0.9).any() else None)
print(table.to_string())
print("cheapest width reaching 90%:", choice)
U.check(choice in WIDTHS, "a width reaches 90% on this set", model=True)

# %% [markdown]
# 🔍 **Look at** the photos still wrong at your choice: `runs[(runs.width == choice) & ~runs.correct]` beside
# `marker_px`. The misses are the photos whose marker text is smallest. The width you pay for is set by the smallest
# text you must read, not by the average photo.

# %%
small = pd.DataFrame(items).set_index("photo_id")
wrong = runs[(runs.width == (choice or 640)) & ~runs.correct].photo_id
print("marker text height (px) of the misses at", choice or 640, ":", sorted(small.loc[wrong, "marker_px"].tolist()))
print("marker text height (px) of all photos:", sorted(small.marker_px.tolist()))

# %% [markdown]
# ## ✱ Stretch · Crop before you shrink
#
# The marker always sits in the right third of the photo. Crop that region at full resolution, then send the crop at
# width 320. Compare tokens and accuracy with the whole photo at your chosen width. (The stand-in does not see the
# crop: with it, reason about the token count; with a hosted model, measure both.)

# %%
# BEGIN SOLUTION
crop = U.photo(items[0]["photo_id"]).crop((440, 160, 640, 480))
print("crop size:", crop.size, "| tokens at its own size:", U.image_tokens(*crop.size),
      "| whole photo at", choice, ":", U.image_tokens(choice or 640, round(0.75 * (choice or 640))))
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why do image tokens grow faster than the width?
# 2. Which photos decide the width you need?
# 3. Your chosen width costs how many times the tokens of 320, and what does that do to a month of 9,000 reports?
#
# <details><summary>Answers</summary>
#
# 1. Tokens follow the number of patches, which grows with the area: twice the width is four times the patches.
# 2. The ones with the smallest marker text; an average hides them.
# 3. Read `relative_cost` in the table; the monthly token bill scales by the same factor for the image part.
# </details>
#
# **Carry forward.** Lab 1.2 sends photos at width 640, the choice this table supports on the stand-in.
