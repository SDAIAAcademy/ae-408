# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 3.3 · Tune the end of a turn
#
# Day 3 · Session 3 (Turn-taking and interruption) · 25 min.
#
# Rahhal decides the caller has finished when it hears enough silence. Too little, and it talks over a caller who
# paused before a number; too much, and the reply is late and the caller says "hello?". You replay twelve scripted
# calls, count false cut-ins and late or missed turns for each silence threshold, and add a rule that holds the turn
# when the caller stopped mid-phrase.
#
# **Reference state.** `data/turn_calls.json`: 12 calls of 4 caller turns, each turn a list of spoken chunks with the
# pause after each one and the caller's patience. Synthetic. The pipeline after the endpoint takes 620 ms
# (recogniser, model, voice, network: `rahhal.STAGES`).
#
# **Tasks**
# - [ ] 1 · Replay the scripted calls frame by frame (5')
# - [ ] 2 · An end-of-turn rule on silence (7')
# - [ ] 3 · Sweep the threshold: cut-ins against late turns (8')
# - [ ] 4 · Hold the turn when the caller is mid-number (5')
# - [ ] ✱ Stretch · Stop the agent within 300 ms when the caller talks over it

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

import rahhal as R
import trails as U

CALLS = json.loads((U.DATA / "turn_calls.json").read_text(encoding="utf-8"))
AFTER_ENDPOINT = R.STAGES["asr"] + R.STAGES["llm_first_token"] + R.STAGES["tts_first_audio"] + R.STAGES["network"]
BUDGET = U.BUDGET_TTFA_MS
print(len(CALLS), "calls,", sum(len(c["turns"]) for c in CALLS), "turns; after the endpoint:", AFTER_ENDPOINT, "ms")
print(json.dumps(CALLS[0]["turns"][0], ensure_ascii=False))

# %% [markdown]
# ## 1 · Frames of silence (5')
#
# ✏️ **Exercise** · `silences(turn)` returns the list of silent stretches inside a turn as `(ms, text_before)`: one
# per pause between chunks, with the text spoken so far. The final silence (after the last chunk) is not in the list:
# the caller has finished there.

# %%
def silences(turn):
    # BEGIN SOLUTION
    out, said = [], []
    for ch in turn["chunks"][:-1]:
        said.append(ch["text"])
        out.append((ch["pause_after_ms"], " ".join(said)))
    return out
    # END SOLUTION


# %%
def _silences_ref(turn):
    out, said = [], []
    for ch in turn["chunks"][:-1]:
        said.append(ch["text"])
        out.append((ch["pause_after_ms"], " ".join(said)))
    return out


try:
    silences(CALLS[0]["turns"][0])
except NotImplementedError:
    silences = _silences_ref
pauses = [p for c in CALLS for t in c["turns"] for p, _ in silences(t)]
print(len(pauses), "pauses inside turns; longest", max(pauses), "ms")
U.check(len(pauses) == sum(len(t["chunks"]) - 1 for c in CALLS for t in c["turns"]), "one silence per pause inside a turn")

# %% [markdown]
# ## 2 · The rule on silence (7')
#
# ✏️ **Exercise** · `judge(turn, threshold_ms, hold=None)` classifies one caller turn:
# - **cut-in** when any pause inside the turn is at least the threshold (the agent starts talking over the caller);
# - otherwise **missed** when `threshold + AFTER_ENDPOINT` exceeds the caller's `patience_ms` (they speak again);
# - otherwise **late** when `threshold + AFTER_ENDPOINT` exceeds the budget of 1,200 ms;
# - otherwise **ok**.
#
# `hold` is a function `(text_before) -> extra_ms` used in step 4; without it, the threshold is the same for every pause.

# %%
def judge(turn, threshold_ms, hold=None):
    # BEGIN SOLUTION
    for ms, before in silences(turn):
        need = threshold_ms + (hold(before) if hold else 0)
        if ms >= need:
            return "cut-in"
    reply = threshold_ms + AFTER_ENDPOINT
    if reply > turn["patience_ms"]:
        return "missed"
    if reply > BUDGET:
        return "late"
    return "ok"
    # END SOLUTION


# %%
def _judge_ref(turn, threshold_ms, hold=None):
    for ms, before in silences(turn):
        if ms >= threshold_ms + (hold(before) if hold else 0):
            return "cut-in"
    reply = threshold_ms + AFTER_ENDPOINT
    return "missed" if reply > turn["patience_ms"] else ("late" if reply > BUDGET else "ok")


try:
    judge(CALLS[0]["turns"][0], 500)
except NotImplementedError:
    judge = _judge_ref
print({th: pd.Series([judge(t, th) for c in CALLS for t in c["turns"]]).value_counts().to_dict() for th in (500, 900)})

# %% [markdown]
# ## 3 · Sweep the threshold (8')
#
# ✏️ **Exercise** · For thresholds from 300 to 1,200 ms in steps of 100, count the four outcomes over all 48 turns.
# Which threshold gives the most `ok` turns, and what does it still get wrong?

# %%
def sweep(hold=None):
    rows = []
    # BEGIN SOLUTION
    for th in range(300, 1201, 100):
        c = pd.Series([judge(t, th, hold) for call in CALLS for t in call["turns"]]).value_counts()
        rows.append({"threshold_ms": th, **{k: int(c.get(k, 0)) for k in ("ok", "cut-in", "late", "missed")}})
    # END SOLUTION
    return pd.DataFrame(rows)


# %%
def _sweep_ref(hold=None):
    rows = []
    for th in range(300, 1201, 100):
        c = pd.Series([judge(t, th, hold) for call in CALLS for t in call["turns"]]).value_counts()
        rows.append({"threshold_ms": th, **{k: int(c.get(k, 0)) for k in ("ok", "cut-in", "late", "missed")}})
    return pd.DataFrame(rows)


try:
    plain = sweep()
except NotImplementedError:
    sweep = _sweep_ref
    plain = sweep()
print(plain.to_string(index=False))
best = plain.loc[plain.ok.idxmax()]
print("best threshold on silence alone:", int(best.threshold_ms), "ms with", int(best.ok), "of 48 ok")
U.check(best.ok < 48, "no threshold on silence alone gets every turn right")

# %% [markdown]
# 🔍 **Look at** the trade: every 100 ms you add removes cut-ins and adds the same 100 ms to every reply. With a budget
# of 1,200 ms and 620 ms after the endpoint, the threshold cannot exceed 580 ms without making every turn late.

# %% [markdown]
# ## 4 · Hold the turn mid-phrase (5')
#
# Callers pause longest before the part they are thinking about: a number, a date, a name. The words before such a
# pause are telling: "for", "on", "the date to", "لعدد", "يوم", "على", "و".
#
# ✏️ **Exercise** · Write `hold(text_before)` that returns 600 extra milliseconds when the text so far ends with one of
# those words (`HOLD_WORDS`), or with a number that may continue, and 0 otherwise. Sweep again with it.

# %%
HOLD_WORDS = {"for", "on", "to", "the", "and", "uh", "لعدد", "يوم", "على", "في", "و", "يعني"}
NUMBER_WORDS = {"four", "eight", "أربعة", "ثمانية", "H", "T", "B"}


def hold(text_before):
    # BEGIN SOLUTION
    last = text_before.split()[-1]
    return 600 if last in HOLD_WORDS or last in NUMBER_WORDS else 0
    # END SOLUTION


# %%
try:
    hold("for")
except NotImplementedError:
    hold = lambda t: 600 if t.split()[-1] in HOLD_WORDS | NUMBER_WORDS else 0
held = sweep(hold)
both = plain[["threshold_ms", "ok", "cut-in"]].merge(held[["threshold_ms", "ok", "cut-in"]], on="threshold_ms",
                                                     suffixes=("_silence", "_with_hold"))
print(both.to_string(index=False))
b2 = held.loc[held.ok.idxmax()]
print("best with the hold rule:", int(b2.threshold_ms), "ms with", int(b2.ok), "of 48 ok")
U.check(b2.ok > best.ok, "holding the turn mid-phrase gets more turns right")
held.to_csv(U.artifacts("D3_3") / "threshold_sweep.csv", index=False)

# %% [markdown]
# ## ✱ Stretch · Barge-in
#
# While Rahhal speaks, the caller makes sounds: short backchannels ("mm", "aha", 120 to 250 ms) and real interruptions
# (600 ms or more). Rahhal should stop within 300 ms of a real interruption and keep talking over a backchannel. Find
# the length of continuous speech after which it should stop.

# %%
# BEGIN SOLUTION
sounds = [("backchannel", d) for d in (120, 140, 160, 180, 200, 220, 250)] + [("interrupt", d) for d in (600, 750, 900, 1200)]
for stop_after in (100, 200, 260, 300, 400):
    false_stops = sum(kind == "backchannel" and d >= stop_after for kind, d in sounds)
    slow = sum(kind == "interrupt" and stop_after + 40 > 300 for kind, d in sounds)  # 40 ms to stop the audio
    print(f"stop after {stop_after} ms: {false_stops} false stops on backchannels, {slow} interruptions handled too slowly")
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why can no single silence threshold get every turn right here?
# 2. The hold rule adds 600 ms only after some words. Why does that not make the other replies late?
# 3. In Arabic, which words in the data signal that the caller has not finished?
#
# <details><summary>Answers</summary>
#
# 1. Pauses inside turns (up to about 1,100 ms before numbers) are longer than the threshold the budget allows (580 ms).
# 2. The extra wait applies only where the text says the caller is mid-phrase; a turn that ends normally is answered at
#    the base threshold.
# 3. لعدد, يوم, على, في, و and يعني; the same idea as "for", "on" and "and".
# </details>
#
# **Carry forward.** The threshold and the hold words go into the capstone agent; `artifacts/D3_3/threshold_sweep.csv`
# is its evidence. A production line replaces the word list with a small end-of-turn model (Pipecat and LiveKit
# Agents both offer one).
