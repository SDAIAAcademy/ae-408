# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 2.3 · Slices with intervals
#
# Day 2 · Session 3 (Dialects and code-switching) · 25 min.
#
# One error rate for the whole line hides who gets worse service. You slice recogniser B's error rate by dialect,
# channel and code-switched speech under the full normalisation rules, add a clip-level bootstrap interval to every
# slice, and flag the slices that are worse than the whole set, with a minimum size below which you say nothing.
#
# **Reference state.** `data/clips.jsonl` and the course's normalisation (`U.normalise`, the full rules of Lab 2.2).
#
# **Tasks**
# - [ ] 1 · Error rate per dialect, channel and code-switching (7')
# - [ ] 2 · A clip-level bootstrap interval per slice (10')
# - [ ] 3 · Flag the slices that are worse, with a minimum size (5')
# - [ ] 4 · The report table (3')
# - [ ] ✱ Stretch · Cross dialect with channel and read what the small cells can say

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

import jiwer
import numpy as np
import pandas as pd

import trails as U

REC = "whisper-large-v3-turbo"
rows = []
for c in U.clips():
    o = jiwer.process_words(U.normalise(c["reference"]), U.normalise(c[REC]))
    rows.append({"clip_id": c["clip_id"], "dialect": c["dialect"], "channel": c["channel"],
                 "code_switched": "code-switched" if c["code_switched"] else "single language",
                 "edits": o.substitutions + o.deletions + o.insertions, "words": len(U.normalise(c["reference"]).split())})
clips = pd.DataFrame(rows)
OVERALL = clips.edits.sum() / clips.words.sum()
print(len(clips), "clips | overall WER of", REC, "under the full rules:", round(OVERALL, 3))

# %% [markdown]
# ## 1 · Error rate per slice (7')
#
# Each clip carries its edit count and its word count, so a slice's WER is the sum of edits over the sum of words.
#
# ✏️ **Exercise** · `slice_table(clips, by)` returns one row per value of the column `by` with `n` (clips), `words`
# and `wer`. Run it for `dialect`, `channel` and `code_switched`.

# %%
def slice_table(clips, by):
    # BEGIN SOLUTION
    g = clips.groupby(by).agg(n=("clip_id", "size"), words=("words", "sum"), edits=("edits", "sum"))
    g["wer"] = (g.edits / g.words).round(3)
    return g.drop(columns="edits")
    # END SOLUTION


# %%
def _slice_ref(clips, by):
    g = clips.groupby(by).agg(n=("clip_id", "size"), words=("words", "sum"), edits=("edits", "sum"))
    g["wer"] = (g.edits / g.words).round(3)
    return g.drop(columns="edits")


try:
    slice_table(clips, "dialect")
except NotImplementedError:
    slice_table = _slice_ref
for by in ("dialect", "channel", "code_switched"):
    print(slice_table(clips, by).to_string(), "\n")
U.check(abs(slice_table(clips, "channel").wer.min() - OVERALL) < 0.2, "slice rates are on the scale of the overall rate")

# %% [markdown]
# ## 2 · A bootstrap interval per slice (10')
#
# The unit of sampling is the **clip**: words of one clip share a speaker, a channel and a recording, so resampling
# words would make the interval too narrow.
#
# ✏️ **Exercise** · `boot(sub, reps)`: draw `len(sub)` clips with replacement, compute sum of edits over sum of words,
# repeat `reps` times, and return the 2.5th and 97.5th percentiles. Use `np.random.default_rng(408)`.

# %%
REPS = U.pick(2000, 300)


def boot(sub, reps=REPS, seed=408):
    # BEGIN SOLUTION
    rng = np.random.default_rng(seed)
    e, w = sub.edits.to_numpy(), sub.words.to_numpy()
    idx = rng.integers(0, len(sub), size=(reps, len(sub)))
    rates = e[idx].sum(1) / w[idx].sum(1)
    return float(np.percentile(rates, 2.5)), float(np.percentile(rates, 97.5))
    # END SOLUTION


# %%
def _boot_ref(sub, reps=REPS, seed=408):
    rng = np.random.default_rng(seed)
    e, w = sub.edits.to_numpy(), sub.words.to_numpy()
    idx = rng.integers(0, len(sub), size=(reps, len(sub)))
    r = e[idx].sum(1) / w[idx].sum(1)
    return float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))


try:
    lo, hi = boot(clips)
except NotImplementedError:
    boot = _boot_ref
    lo, hi = boot(clips)
print(f"overall {OVERALL:.3f}, 95% interval [{lo:.3f}, {hi:.3f}]")
U.check(lo < OVERALL < hi, "the overall rate sits inside its interval")

# %% [markdown]
# ## 3 · Flag the worse slices (5')
#
# A slice is **flagged** when its whole interval lies above the overall rate. A slice with fewer than `MIN_N` clips is
# **too small to say**, whatever its numbers.
#
# ✏️ **Exercise** · Build `report`: one row per slice of the three columns, with `factor`, `slice`, `n`, `wer`,
# `lo`, `hi` and `verdict` ("worse", "not shown worse" or "too small to say").

# %%
MIN_N = 6


def build_report(clips):
    rows = []
    # BEGIN SOLUTION
    for by in ("dialect", "channel", "code_switched"):
        for value, sub in clips.groupby(by):
            wer = sub.edits.sum() / sub.words.sum()
            lo, hi = boot(sub)
            verdict = "too small to say" if len(sub) < MIN_N else ("worse" if lo > OVERALL else "not shown worse")
            rows.append({"factor": by, "slice": value, "n": len(sub), "wer": round(wer, 3), "lo": round(lo, 3),
                         "hi": round(hi, 3), "verdict": verdict})
    # END SOLUTION
    return pd.DataFrame(rows)


# %%
try:
    report = build_report(clips)
except NotImplementedError:
    report = pd.DataFrame([{"factor": by, "slice": v, "n": len(s), "wer": round(s.edits.sum() / s.words.sum(), 3),
                            "lo": round(boot(s)[0], 3), "hi": round(boot(s)[1], 3),
                            "verdict": "too small to say" if len(s) < MIN_N else ("worse" if boot(s)[0] > OVERALL else "not shown worse")}
                           for by in ("dialect", "channel", "code_switched") for v, s in clips.groupby(by)])
print(report.to_string(index=False))
U.check("worse" in set(report.verdict), "at least one slice is shown worse than the whole set", model=True)

# %% [markdown]
# ## 4 · The report table (3')
#
# ✏️ **Exercise** · Save the table as `artifacts/D2_3/wer_by_slice.csv` with a first line that names the recogniser,
# the rule set and the number of bootstrap repetitions. A table without its rules cannot be compared.

# %%
# BEGIN SOLUTION
out = U.artifacts("D2_3") / "wer_by_slice.csv"
with open(out, "w", encoding="utf-8", newline="") as f:
    f.write(f"# recogniser={REC}; rules=full (trails.normalise); bootstrap={REPS} clip resamples; overall={OVERALL:.3f}\n")
    report.to_csv(f, index=False)
print(out.read_text(encoding="utf-8")[:300])
# END SOLUTION

# %% [markdown]
# ## ✱ Stretch · Dialect by channel
#
# Cross dialect with channel. How many cells have at least `MIN_N` clips? What can the table say about southern
# speakers on the telephone, and what can it not?

# %%
# BEGIN SOLUTION
cross = clips.groupby(["dialect", "channel"]).agg(n=("clip_id", "size"), edits=("edits", "sum"), words=("words", "sum"))
cross["wer"] = (cross.edits / cross.words).round(3)
print(cross[["n", "wer"]].to_string())
print("cells with at least", MIN_N, "clips:", int((cross.n >= MIN_N).sum()), "of", len(cross))
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why resample clips and not words?
# 2. Which slice is shown worse, and what does the interval add to the point estimate?
# 3. Egyptian visitors have 6 clips and an interval from 0 to 0.135. What do you write in the report?
#
# <details><summary>Answers</summary>
#
# 1. Words in one clip share a speaker and a channel; they are not independent, so word resampling understates
#    the uncertainty.
# 2. Read `verdict`: the southern dialect in the stand-in run (0.219, interval 0.145 to 0.309, above 0.089). The
#    telephone channel is higher too, but its interval starts just below the overall rate: not shown worse yet.
# 3. The rate and its interval, "not shown worse", and a request for more clips: an interval that wide is absence
#    of evidence, not evidence of equal service.
# </details>
#
# **Carry forward.** `artifacts/D2_3/wer_by_slice.csv` is the speech-evaluation table of the capstone.
