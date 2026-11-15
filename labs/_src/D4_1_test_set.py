# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 4.1 · A 60-item test set with coverage
#
# Day 4 · Session 1 (Multimodal test sets) · 25 min.
#
# Wedad Al-Omari will sign off Lamha and Rahhal on one test set. The authority has a pool of 240 labelled items
# (photos and call recordings) and budget to grade 60. A random 60 would follow the pool, which has few southern and
# Egyptian callers and few seeded failures. You write coverage targets first, select 60 items that meet them, print
# the coverage table, and name the gaps the pool cannot fill.
#
# **Reference state.** `data/test_pool.csv`: 240 items with modality, task, dialect, channel, code-switching, whether
# the item carries a seeded failure (Days 1 and 2), and the source (public or synthetic). Synthetic labels.
#
# **Tasks**
# - [ ] 1 · Read the pool and its composition (4')
# - [ ] 2 · Write coverage targets before selecting (6')
# - [ ] 3 · Select 60 items that meet the targets (8')
# - [ ] 4 · The coverage table and the gaps (7')
# - [ ] ✱ Stretch · Hold out 10 items nobody tunes on

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

import pandas as pd

import trails as U

pool = pd.read_csv(U.DATA / "test_pool.csv")
SIZE = 60
print(len(pool), "items in the pool;", SIZE, "to grade")
print(pool.head().to_string(index=False))

# %% [markdown]
# ## 1 · What the pool holds (4')
#
# ✏️ **Exercise** · Print the count of each value of `modality`, `dialect`, `channel`, `code_switched` and
# `seeded_failure`. Then draw a **random** 60 with `random_state=408` and count the southern and Egyptian callers in it.

# %%
COLS = ["modality", "task", "dialect", "channel", "code_switched", "seeded_failure"]


def composition(df):
    # BEGIN SOLUTION
    return {c: df[c].value_counts().to_dict() for c in COLS if c != "task"}
    # END SOLUTION


# %%
try:
    comp = composition(pool)
except NotImplementedError:
    comp = {c: pool[c].value_counts().to_dict() for c in COLS if c != "task"}
for c, v in comp.items():
    print(f"{c:15s}", v)
rand = pool.sample(SIZE, random_state=408)
print("\nrandom 60: southern", int((rand.dialect == "southern").sum()), "| egyptian", int((rand.dialect == "egyptian").sum()),
      "| seeded failures", int(rand.seeded_failure.sum()))

# %% [markdown]
# ## 2 · Targets first (6')
#
# A target is a minimum count for a value of one column (or an exact count for the modality split). Write them
# **before** looking at any result, from the questions the sign-off must answer: every dialect in the error-rate
# report, enough telephone calls, every task, and the seeded failures from the failure log.
#
# ✏️ **Exercise** · Complete `TARGETS`: 40 audio and 20 image items; at least 5 of each of the six dialects; at least
# 15 telephone calls; at least 6 code-switched calls; at least 10 seeded failures; at least 6 of each audio task and
# 4 of each image task.

# %%
AUDIO_TASKS = ["book_visit", "change_booking", "cancel_booking", "enquiry"]
IMAGE_TASKS = ["extract_fields", "grounding", "absent_object", "read_sign"]
DIALECTS = ["najdi", "hijazi", "gulf", "msa", "southern", "egyptian"]

# BEGIN SOLUTION
TARGETS = {
    ("modality", "audio"): 40, ("modality", "image"): 20,
    **{("dialect", d): 5 for d in DIALECTS},
    ("channel", "telephone"): 15, ("code_switched", 1): 6, ("seeded_failure", 1): 10,
    **{("task", t): 6 for t in AUDIO_TASKS}, **{("task", t): 4 for t in IMAGE_TASKS},
}
# END SOLUTION

# %%
try:
    TARGETS
except NameError:
    TARGETS = {("modality", "audio"): 40, ("modality", "image"): 20, **{("dialect", d): 5 for d in DIALECTS},
               ("channel", "telephone"): 15, ("code_switched", 1): 6, ("seeded_failure", 1): 10,
               **{("task", t): 6 for t in AUDIO_TASKS}, **{("task", t): 4 for t in IMAGE_TASKS}}
print(len(TARGETS), "targets")
U.check(sum(v for (c, _), v in TARGETS.items() if c == "modality") == SIZE, "the modality split adds up to 60")

# %% [markdown]
# ## 3 · Select 60 that meet them (8')
#
# A greedy selection works: repeatedly take the item that satisfies the most targets still unmet, without going over
# the modality quotas; when every target is met, fill the remaining places at random (`random_state=408`).
#
# ✏️ **Exercise** · Write `select(pool, targets, size)` and `unmet(sample, targets)` (the targets a sample misses,
# with the count it has).

# %%
def unmet(sample, targets):
    # BEGIN SOLUTION
    out = {}
    for (col, val), need in targets.items():
        have = int((sample[col] == val).sum())
        if have < need:
            out[(col, val)] = (have, need)
    return out
    # END SOLUTION


def select(pool, targets, size=SIZE):
    # BEGIN SOLUTION
    quota = {val: n for (col, val), n in targets.items() if col == "modality"}
    chosen = []
    left = pool.copy()
    while len(chosen) < size:
        sample = pool.loc[chosen]
        need = {k: n - int((sample[k[0]] == k[1]).sum()) for k, n in targets.items() if k[0] != "modality"}
        open_mod = {m for m, n in quota.items() if int((sample.modality == m).sum()) < n}
        cand = left[left.modality.isin(open_mod)]
        score = sum((cand[c] == v).astype(int) for (c, v), n in need.items() if n > 0)
        if isinstance(score, int) or score.max() == 0:
            break
        best = score[score == score.max()].index[0]
        chosen.append(best)
        left = left.drop(best)
    for m, n in quota.items():
        have = int((pool.loc[chosen].modality == m).sum())
        if have < n:
            chosen += list(left[left.modality == m].sample(n - have, random_state=408).index)
    return pool.loc[chosen]
    # END SOLUTION


# %%
def _unmet_ref(sample, targets):
    return {k: (int((sample[k[0]] == k[1]).sum()), n) for k, n in targets.items() if int((sample[k[0]] == k[1]).sum()) < n}


def _select_ref(pool, targets, size=SIZE):
    quota = {v: n for (c, v), n in targets.items() if c == "modality"}
    chosen, left = [], pool.copy()
    while len(chosen) < size:
        s = pool.loc[chosen]
        need = {k: n - int((s[k[0]] == k[1]).sum()) for k, n in targets.items() if k[0] != "modality"}
        cand = left[left.modality.isin({m for m, n in quota.items() if int((s.modality == m).sum()) < n})]
        score = sum((cand[c] == v).astype(int) for (c, v), n in need.items() if n > 0)
        if isinstance(score, int) or score.max() == 0:
            break
        best = score[score == score.max()].index[0]
        chosen.append(best)
        left = left.drop(best)
    for m, n in quota.items():
        have = int((pool.loc[chosen].modality == m).sum())
        if have < n:
            chosen += list(left[left.modality == m].sample(n - have, random_state=408).index)
    return pool.loc[chosen]


try:
    unmet(rand, TARGETS)
except NotImplementedError:
    unmet = _unmet_ref
try:
    test = select(pool, TARGETS)
except NotImplementedError:
    test = _select_ref(pool, TARGETS)
print("random 60 misses:", {f"{c}={v}": f"{h}/{n}" for (c, v), (h, n) in unmet(rand, TARGETS).items()})
print("selected", len(test), "| misses:", unmet(test, TARGETS))
U.check(len(test) == SIZE and not unmet(test, TARGETS) and test.item_id.is_unique,
        "60 distinct items that meet every target")

# %% [markdown]
# ## 4 · Coverage table and gaps (7')
#
# ✏️ **Exercise** · Print the coverage of the audio items as a table of dialect by channel, and of all items as task by
# modality. Then list the **gaps**: dialect and task cells (audio) with fewer than 3 items in the whole pool. No
# selection can fill them; they go to the data request.

# %%
def coverage(test):
    # BEGIN SOLUTION
    audio = test[test.modality == "audio"]
    return (pd.crosstab(audio.dialect, audio.channel, margins=True),
            pd.crosstab(test.task, test.modality, margins=True))
    # END SOLUTION


def gaps(pool, min_items=3):
    # BEGIN SOLUTION
    audio = pool[pool.modality == "audio"]
    t = pd.crosstab(audio.dialect, audio.task).reindex(index=DIALECTS, columns=AUDIO_TASKS, fill_value=0)
    return [(d, ch, int(t.loc[d, ch])) for d in t.index for ch in t.columns if t.loc[d, ch] < min_items]
    # END SOLUTION


# %%
try:
    by_dialect, by_task = coverage(test)
except NotImplementedError:
    a = test[test.modality == "audio"]
    by_dialect, by_task = pd.crosstab(a.dialect, a.channel, margins=True), pd.crosstab(test.task, test.modality, margins=True)
print(by_dialect.to_string(), "\n")
print(by_task.to_string(), "\n")
try:
    g = gaps(pool)
except NotImplementedError:
    a = pool[pool.modality == "audio"]
    t = pd.crosstab(a.dialect, a.task).reindex(index=DIALECTS, columns=AUDIO_TASKS, fill_value=0)
    g = [(d, ch, int(t.loc[d, ch])) for d in t.index for ch in t.columns if t.loc[d, ch] < 3]
print("gaps in the pool (dialect, task, items):", g)
U.check(len(g) > 0, "the pool has cells that no selection can fill")
out = U.artifacts("D4_1")
test.to_csv(out / "test_set.csv", index=False)
by_dialect.to_csv(out / "coverage_dialect_channel.csv")

# %% [markdown]
# 🔍 **Look at** the source column of the selected items: the public clips are read speech, the synthetic ones are
# generated. A test set that meets every count can still be easier than real calls.

# %% [markdown]
# ## ✱ Stretch · A hold-out
#
# Set aside 10 of the 60, stratified by modality, that nobody looks at while tuning thresholds, prompts or rules.
# Check that the hold-out still contains at least one seeded failure.

# %%
# BEGIN SOLUTION
parts = []
for m, n in (("audio", 7), ("image", 3)):
    sub = test[test.modality == m]
    seeded = sub[sub.seeded_failure == 1].sample(1, random_state=1)  # at least one seeded failure per modality
    parts += [seeded, sub.drop(seeded.index).sample(n - 1, random_state=1)]
hold = pd.concat(parts)
print(hold[["item_id", "modality", "task", "dialect", "seeded_failure"]].to_string(index=False))
print("seeded failures in the hold-out:", int(hold.seeded_failure.sum()))
print("first random draw without stratifying on seeded failures would have held:",
      int(pd.concat([test[test.modality == "audio"].sample(7, random_state=1),
                     test[test.modality == "image"].sample(3, random_state=1)]).seeded_failure.sum()))
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why write the targets before selecting?
# 2. How many southern callers did the random 60 hold, and what would its error rate for them be worth?
# 3. What do you do with a gap?
#
# <details><summary>Answers</summary>
#
# 1. Targets chosen after seeing results can be set to flatter a system; written first, they state what the sign-off
#    must cover.
# 2. Very few (see step 1); an error rate on a handful of clips has an interval too wide to report.
# 3. Name it in the report and request recordings for it; never fill it by copying items from another cell.
# </details>
#
# **Carry forward.** `artifacts/D4_1/test_set.csv` and its coverage table are the capstone's test set.
