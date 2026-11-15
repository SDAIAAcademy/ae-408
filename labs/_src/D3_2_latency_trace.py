# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 3.2 · Where the time goes
#
# Day 3 · Session 2 (Cascaded versus speech-to-speech) · 25 min.
#
# Fayyad Al-Ghamdi owns one number: **1,200 ms** from the end of the caller's speech to the first audio of the reply.
# You read the per-stage trace of 20 turns of the cascaded Rahhal (detector, recogniser, language model, synthesis,
# network), compute time to first audio at the median and the 90th percentile, compare it with the traces of a
# hosted speech-to-speech session, and measure what streaming the first sentence to the voice would save.
#
# **Reference state.** `data/traces/cascaded.jsonl` (one event per stage per turn, times in ms from the end of the
# caller's speech) and `data/traces/speech_to_speech.jsonl` (time to first audio per turn). Both are synthetic.
#
# **Tasks**
# - [ ] 1 · Read the traces into stages (5')
# - [ ] 2 · Per-stage time and time to first audio, median and 90th percentile (8')
# - [ ] 3 · The same for the speech-to-speech traces (6')
# - [ ] 4 · What streaming the first sentence would save (6')
# - [ ] ✱ Stretch · Allocate the budget of 1,200 ms across stages and test it

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

events = pd.DataFrame(U.jsonl("traces/cascaded.jsonl"))
s2s = pd.DataFrame(U.jsonl("traces/speech_to_speech.jsonl"))
BUDGET = U.BUDGET_TTFA_MS
print(len(events), "events over", events.turn.nunique(), "turns; budget", BUDGET, "ms")
print(events[events.turn == 1].to_string(index=False))

# %% [markdown]
# ## 1 · One row per turn (5')
#
# ✏️ **Exercise** · Pivot the events into `turns`: one row per turn, one column per stage holding its **duration**
# (`end_ms - start_ms`), plus `ttfa` (the end of the `network` stage: the moment audio reaches the caller), `tool`
# (the turn had a `tool_call` event) and `streamed` (synthesis started at the end of the first sentence, not of the
# full reply).

# %%
def per_turn(events):
    # BEGIN SOLUTION
    ev = events.assign(dur=events.end_ms - events.start_ms)
    t = ev.pivot_table(index="turn", columns="stage", values="dur", aggfunc="sum").fillna(0)
    ends = events.pivot_table(index="turn", columns="stage", values="end_ms", aggfunc="max")
    starts = events.pivot_table(index="turn", columns="stage", values="start_ms", aggfunc="min")
    t["ttfa"] = ends["network"]
    t["tool"] = t.get("tool_call", 0) > 0
    t["streamed"] = starts["tts_first_audio"] == ends["llm_first_sentence"]
    return t
    # END SOLUTION


# %%
def _per_turn_ref(events):
    ev = events.assign(dur=events.end_ms - events.start_ms)
    t = ev.pivot_table(index="turn", columns="stage", values="dur", aggfunc="sum").fillna(0)
    ends = events.pivot_table(index="turn", columns="stage", values="end_ms", aggfunc="max")
    starts = events.pivot_table(index="turn", columns="stage", values="start_ms", aggfunc="min")
    t["ttfa"], t["tool"] = ends["network"], t.get("tool_call", 0) > 0
    t["streamed"] = starts["tts_first_audio"] == ends["llm_first_sentence"]
    return t


try:
    turns = per_turn(events)
except NotImplementedError:
    turns = _per_turn_ref(events)
print(turns[["endpoint", "asr_final", "llm_first_token", "tts_first_audio", "network", "ttfa", "tool", "streamed"]].head(8).to_string())
U.check(len(turns) == 20 and turns.ttfa.min() > 0, "one row per turn with a time to first audio")

# %% [markdown]
# ## 2 · Per stage, median and 90th percentile (8')
#
# ✏️ **Exercise** · A table with the median and the 90th percentile of each stage that lies on the path to the first
# audio (`endpoint`, `asr_final`, `llm_first_token`, `tts_first_audio`, `network`) and of `ttfa`. Then: how many turns
# are over the budget, and what do they have in common?

# %%
PATH = ["endpoint", "asr_final", "llm_first_token", "tts_first_audio", "network", "ttfa"]


def stage_table(turns):
    # BEGIN SOLUTION
    return pd.DataFrame({"p50": turns[PATH].median(), "p90": turns[PATH].quantile(0.9)}).round(0)
    # END SOLUTION


# %%
try:
    stages = stage_table(turns)
except NotImplementedError:
    stages = pd.DataFrame({"p50": turns[PATH].median(), "p90": turns[PATH].quantile(0.9)}).round(0)
print(stages.to_string())
over = turns[turns.ttfa > BUDGET]
print(f"\n{len(over)} of 20 turns over {BUDGET} ms;", "tool turns among them:", int(over.tool.sum()),
      "| not streamed:", int((~over.streamed).sum()))
U.check(stages.loc["ttfa", "p90"] > BUDGET, "the 90th percentile breaks the budget")

# %% [markdown]
# 🔍 **Look at** the endpoint row: the largest single share of the median turn is spent **waiting to be sure the
# caller has finished**, before any model runs. Lab 3.3 is about that wait.

# %% [markdown]
# ## 3 · Speech-to-speech (6')
#
# A speech-to-speech model hears audio and answers with audio: no separate recogniser or voice, and its own end-of-turn
# detection. The provided traces give only its time to first audio per turn.
#
# ✏️ **Exercise** · Compare the two designs on median, 90th percentile and the share of turns within budget, overall
# and on the four tool turns.

# %%
def compare(turns, s2s):
    # BEGIN SOLUTION
    rows = {}
    for name, v, tool in (("cascaded", turns.ttfa, turns.tool), ("speech_to_speech", s2s.first_audio_ms, s2s.tool)):
        rows[name] = {"p50": v.median(), "p90": v.quantile(0.9), "within_budget": (v <= BUDGET).mean(),
                      "p50_tool_turns": v[tool.to_numpy()].median()}
    return pd.DataFrame(rows).T.round(2)
    # END SOLUTION


# %%
try:
    cmp = compare(turns, s2s)
except NotImplementedError:
    cmp = pd.DataFrame({"cascaded": {"p50": turns.ttfa.median(), "p90": turns.ttfa.quantile(0.9)},
                        "speech_to_speech": {"p50": s2s.first_audio_ms.median(), "p90": s2s.first_audio_ms.quantile(0.9)}}).T
print(cmp.to_string())
U.check(cmp.loc["speech_to_speech", "p90"] < cmp.loc["cascaded", "p90"], "speech-to-speech is faster at the 90th percentile")

# %% [markdown]
# ## 4 · Stream the first sentence (6')
#
# In seven turns the voice waited for the **whole** reply before speaking. If it starts on the first sentence, the
# first audio arrives at `llm_first_sentence` end + `tts_first_audio` + `network`.
#
# ✏️ **Exercise** · Recompute `ttfa` for those turns as if they streamed, and report the new median, 90th percentile
# and turns within budget.

# %%
def streamed_ttfa(turns, events):
    # BEGIN SOLUTION
    ends = events.pivot_table(index="turn", columns="stage", values="end_ms", aggfunc="max")
    alt = ends["llm_first_sentence"] + turns["tts_first_audio"] + turns["network"]
    return turns.ttfa.where(turns.streamed, alt)
    # END SOLUTION


# %%
try:
    new = streamed_ttfa(turns, events)
except NotImplementedError:
    ends = events.pivot_table(index="turn", columns="stage", values="end_ms", aggfunc="max")
    new = turns.ttfa.where(turns.streamed, ends["llm_first_sentence"] + turns["tts_first_audio"] + turns["network"])
print(f"before: p50 {turns.ttfa.median():.0f}, p90 {turns.ttfa.quantile(0.9):.0f}, within budget {(turns.ttfa <= BUDGET).sum()}/20")
print(f"after:  p50 {new.median():.0f}, p90 {new.quantile(0.9):.0f}, within budget {(new <= BUDGET).sum()}/20")
U.check(new.quantile(0.9) < turns.ttfa.quantile(0.9), "streaming the first sentence lowers the 90th percentile")
turns.assign(ttfa_streamed=new).to_csv(U.artifacts("D3_2") / "latency_by_turn.csv")

# %% [markdown]
# ## ✱ Stretch · A budget per stage
#
# Split 1,200 ms across the five stages so that the median turn fits, write the split down, and count how many turns
# break each stage's share. Which stage would you work on first?

# %%
# BEGIN SOLUTION
share = {"endpoint": 520, "asr_final": 180, "llm_first_token": 280, "tts_first_audio": 150, "network": 70}
print("total", sum(share.values()), "ms")
print({k: int((turns[k] > v).sum()) for k, v in share.items()})
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Which stage takes the largest share of the median turn, and what is it waiting for?
# 2. Why is the 90th percentile, not the median, the number to hold against the budget?
# 3. Speech-to-speech is faster here. Name one thing you lose by choosing it.
#
# <details><summary>Answers</summary>
#
# 1. The endpoint: the wait to be sure the caller has stopped (Lab 3.3).
# 2. One reply in ten feels broken to a caller whatever the median; the tail is the experience people remember.
# 3. The transcript and the separate recogniser you evaluated on Day 2: slicing by dialect and checking the text
#    before a tool call need a transcript the design may not give you.
# </details>
#
# **Carry forward.** `artifacts/D3_2/latency_by_turn.csv` is the latency trace of the capstone; Lab 4.3 weighs the
# two designs on cost as well.
