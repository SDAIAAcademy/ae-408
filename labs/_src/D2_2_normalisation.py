# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 2.2 · Rules before rates
#
# Day 2 · Session 2 (Normalisation decides the error rate) · 25 min. **AI off**: no assistant writes your rules.
#
# Lab 2.1 ranked whisper-large-v3 far ahead of whisper-large-v3-turbo. Before Wedad signs anything, you write the
# Arabic normalisation rules explicitly, recompute the error rates under three rule sets, and see whether the ranking
# survives. The rules file you save is the one the capstone report cites.
#
# **Reference state.** `data/clips.jsonl` with both recorded transcripts. Nothing from Lab 2.1.
#
# **Tasks**
# - [ ] 1 · Write the rules: diacritics, alef, ta marbuta, alef maqsura, tatweel, digits (10')
# - [ ] 2 · Recompute error rates under three rule sets (7')
# - [ ] 3 · Which rule moved the rate, and the ranking (5')
# - [ ] 4 · Save the rules file the report will cite (3')
# - [ ] ✱ Stretch · Find a pair of words the rules merge that mean different things

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
import re
import unicodedata

import jiwer
import pandas as pd

import trails as U

clips = U.clips()[:U.pick(50, 20)]
REFS = [c["reference"] for c in clips]
HYPS = {"A": [c["whisper-large-v3"] for c in clips], "B": [c["whisper-large-v3-turbo"] for c in clips]}
print(len(clips), "clips")

# %% [markdown]
# ## 1 · The rules (10')
#
# ✏️ **Exercise** · Write one small function per rule. Each takes a string and returns a string.
#
# | Rule | What it does | Example |
# |---|---|---|
# | `diacritics` | removes the short-vowel marks, shadda and sukun (U+064B to U+0652, and U+0670) | `ابَي` → `ابي` |
# | `tatweel` | removes the stretching character U+0640 | `للـاطفال` → `للاطفال` |
# | `digits` | turns Arabic-Indic digits into Western digits | `١٢٨٨` → `1288` |
# | `punct` | turns punctuation into spaces and squeezes spaces | `نعم، شكرا.` → `نعم شكرا` |
# | `alef` | turns أ إ آ ٱ into ا | `أبي` → `ابي` |
# | `maqsura` | turns final ى into ي | `على` → `علي` |
# | `ta` | turns ة into ه | `جولة` → `جوله` |

# %%
def diacritics(t):
    # BEGIN SOLUTION
    return re.sub("[ً-ْٰ]", "", t)
    # END SOLUTION


def tatweel(t):
    # BEGIN SOLUTION
    return t.replace("ـ", "")
    # END SOLUTION


def digits(t):
    # BEGIN SOLUTION
    return t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    # END SOLUTION


def punct(t):
    # BEGIN SOLUTION
    return " ".join(re.sub(r"[^\w\s]", " ", t).split())
    # END SOLUTION


def alef(t):
    # BEGIN SOLUTION
    return re.sub("[أإآٱ]", "ا", t)
    # END SOLUTION


def maqsura(t):
    # BEGIN SOLUTION
    return t.replace("ى", "ي")
    # END SOLUTION


def ta(t):
    # BEGIN SOLUTION
    return t.replace("ة", "ه")
    # END SOLUTION


# %%
TESTS = {"diacritics": ("ابَي", "ابي"), "tatweel": ("للـاطفال", "للاطفال"), "digits": ("١٢٨٨", "1288"),
         "punct": ("نعم، شكرا.", "نعم شكرا"), "alef": ("أبي إلى", "ابي الى"), "maqsura": ("على", "علي"), "ta": ("جولة", "جوله")}
FALLBACK = {"diacritics": lambda t: re.sub("[ً-ْٰ]", "", t), "tatweel": lambda t: t.replace("ـ", ""),
            "digits": lambda t: t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")),
            "punct": lambda t: " ".join(re.sub(r"[^\w\s]", " ", t).split()), "alef": lambda t: re.sub("[أإآٱ]", "ا", t),
            "maqsura": lambda t: t.replace("ى", "ي"), "ta": lambda t: t.replace("ة", "ه")}
RULES = {}
for name, (src, want) in TESTS.items():
    fn = globals()[name]
    try:
        ok = fn(src) == want
    except NotImplementedError:
        fn, ok = FALLBACK[name], None
    RULES[name] = fn
    print(f"{name:10s}", "✅" if ok else ("✏️ not done yet: using the reference" if ok is None else "❌ " + fn(src)))
U.check(all(RULES[n](s) == w for n, (s, w) in TESTS.items()), "every rule passes its example")

# %% [markdown]
# ## 2 · Three rule sets (7')
#
# ✏️ **Exercise** · `normalise(text, names)` applies the named rules in order (always lower-casing and squeezing
# spaces). Then compute the corpus WER of both recognisers under three sets:
# `none` = [], `light` = diacritics, tatweel, digits, punct, and `full` = light plus alef, maqsura, ta.

# %%
SETS = {"none": [], "light": ["diacritics", "tatweel", "digits", "punct"],
        "full": ["diacritics", "tatweel", "digits", "punct", "alef", "maqsura", "ta"]}


def normalise(text, names):
    # BEGIN SOLUTION
    t = unicodedata.normalize("NFKC", text).lower()
    for n in names:
        t = RULES[n](t)
    return " ".join(t.split())
    # END SOLUTION


def wer_under(names, r):
    return jiwer.wer([normalise(x, names) for x in REFS], [normalise(x, names) for x in HYPS[r]])


# %%
try:
    normalise("x", [])
except NotImplementedError:
    def normalise(text, names):
        t = unicodedata.normalize("NFKC", text).lower()
        for n in names:
            t = RULES[n](t)
        return " ".join(t.split())
table = pd.DataFrame({s: {U.ASR_MODELS[r]: round(wer_under(names, r), 3) for r in ("A", "B")} for s, names in SETS.items()})
print(table.to_string())
U.check(abs(table.loc[U.ASR_MODELS["B"], "full"] - U.wer(REFS, HYPS["B"], "full")) < 0.002, "full rules agree with the course reference")

# %% [markdown]
# ## 3 · Which rule moved the rate (5')
#
# ✏️ **Exercise** · Starting from `none`, add one rule at a time (in the order of `full`) and record recogniser B's WER
# after each. Which rule cut the most? Does the ranking of A and B change, and under which set?

# %%
def ablation(r="B"):
    rows, names = [], []
    # BEGIN SOLUTION
    rows.append({"after": "nothing", "wer": round(wer_under([], r), 3)})
    for n in SETS["full"]:
        names.append(n)
        rows.append({"after": "+ " + n, "wer": round(wer_under(names, r), 3)})
    # END SOLUTION
    return pd.DataFrame(rows)


# %%
try:
    steps = ablation("B")
except NotImplementedError:
    steps = pd.DataFrame([{"after": "+ " + "+".join(SETS["full"][:k]) if k else "nothing", "wer": round(wer_under(SETS["full"][:k], "B"), 3)}
                          for k in range(len(SETS["full"]) + 1)])
steps["cut"] = (-steps.wer.diff()).round(3)
print(steps.to_string(index=False))
better = {s: min(("A", "B"), key=lambda r: wer_under(SETS[s], r)) for s in SETS}
print("better recogniser under each set:", {s: U.ASR_MODELS[r] for s, r in better.items()})
U.check(better["none"] != better["full"], "the ranking changes between raw text and full normalisation")

# %% [markdown]
# 🔍 **Look at** the order: the rules that remove spelling variation (digits, diacritics, hamza on alef) carry most of B's
# "errors". None of them is something a caller hears. A report that does not state its rules cannot be compared with
# anyone else's.

# %% [markdown]
# ## 4 · The rules file (3')
#
# ✏️ **Exercise** · Save `normalisation_rules.json` with the rule set you will report (name, the rules in order, one
# line per rule saying what it does) and the WER of both recognisers under it.

# %%
DESCRIBE = {"diacritics": "remove short vowels, shadda, sukun (U+064B to U+0652, U+0670)", "tatweel": "remove U+0640",
            "digits": "Arabic-Indic digits to Western digits", "punct": "punctuation to spaces",
            "alef": "أ إ آ ٱ to ا", "maqsura": "final ى to ي", "ta": "ة to ه"}


def save_rules(set_name):
    # BEGIN SOLUTION
    doc = {"rule_set": set_name, "lowercase": True, "rules": [{"name": n, "does": DESCRIBE[n]} for n in SETS[set_name]],
           "wer": {U.ASR_MODELS[r]: round(wer_under(SETS[set_name], r), 3) for r in ("A", "B")}, "clips": len(clips)}
    path = U.artifacts("D2_2") / "normalisation_rules.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return path
    # END SOLUTION


# %%
try:
    path = save_rules("full")
except NotImplementedError:
    path = U.artifacts("D2_2") / "normalisation_rules.json"
    path.write_text(json.dumps({"rule_set": "full", "rules": SETS["full"]}, ensure_ascii=False), encoding="utf-8")
print(path.read_text(encoding="utf-8")[:400])
U.check(path.exists(), "rules file saved")

# %% [markdown]
# ## ✱ Stretch · A rule that hides a real error
#
# The `ta` rule merges ة and ه, and `maqsura` merges ى and ي. Find pairs in the references whose words become equal
# after the full rules but differ before: each is a place where a real recognition error would now be forgiven.

# %%
# BEGIN SOLUTION
vocab = sorted({w for r in REFS for w in r.split()} | {"علي", "على", "جوله", "جولة", "مره", "مرة"})
seen = {}
for w in vocab:
    seen.setdefault(normalise(w, SETS["full"]), set()).add(w)
print([sorted(v) for v in seen.values() if len(v) > 1])
# على (on) and علي (the name Ali) merge: "the booking on X" and "the booking of Ali" now score the same.
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Under raw text which recogniser wins, and under the full rules?
# 2. Which single rule cut B's error rate most?
# 3. Name one rule you would not apply when the transcript feeds a booking, and why.
#
# <details><summary>Answers</summary>
#
# 1. A on raw text (0.213 against 0.517 on the full set); B under the full rules (0.089 against 0.160).
# 2. Read the `cut` column; on the full set it is the diacritics rule, followed by digits and alef.
# 3. Merging ى and ي can hide the difference between على (on) and علي (Ali): for names, keep it in a second score.
# </details>
#
# **Carry forward.** `artifacts/D2_2/normalisation_rules.json`; the course's reference rules are `trails.normalise`.
