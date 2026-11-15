# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 4.2 · Twenty simulated callers
#
# Day 4 · Session 2 (Simulated callers) · 25 min.
#
# Fayyad has a release candidate of Rahhal. Before any visitor phones it, you run 20 simulated callers against it:
# each card has a goal (site, date, party size), a language, a dialect and a behaviour (cooperative, long pauses,
# mumbles, code-switches, interrupts, changes their mind). You grade every call **from the booking store**, not from
# what Rahhal said, measure how much the recogniser got wrong on the way, and group the failures by behaviour.
#
# **Reference state.** `data/callers.jsonl` (20 cards), `rahhal.run_call` (plays a card against an agent through the
# stand-in recogniser `rahhal.hear`), and the release candidate below. Nothing calls a model.
#
# **Tasks**
# - [ ] 1 · Read the caller cards (3')
# - [ ] 2 · Run the twenty calls (8')
# - [ ] 3 · Grade each call from the booking store (7')
# - [ ] 4 · Transcript errors, and failures by behaviour (7')
# - [ ] ✱ Stretch · Let a hosted model play the caller

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


def release_candidate(store):
    """Rahhal as Fayyad handed it over: confirmation on, a booking tool with a capacity check."""
    def book_visit(site_code, date, party_size, name):
        if store.booked(site_code, date) + party_size > R.CAPACITY:
            raise R.ToolError("that day is full for a group of that size")
        return store.add(site_code, date, party_size, name)
    return R.Rahhal(book_tool=book_visit, policy="confirm_then_book", stale_confirmation=True)


CARDS = R.cards()
print(len(CARDS), "caller cards")
print(json.dumps(CARDS[0], ensure_ascii=False))

# %% [markdown]
# ## 1 · The cards (3')
#
# ✏️ **Exercise** · Put the cards in a table with `caller_id`, `language`, `dialect`, `behaviour` and whether the card
# changes its mind (`change_to`), and count the cards per behaviour.

# %%
def card_table(cards):
    # BEGIN SOLUTION
    return pd.DataFrame([{"caller_id": c["caller_id"], "language": c["language"], "dialect": c["dialect"],
                          "behaviour": c["behaviour"], "changes": c["change_to"] is not None} for c in cards])
    # END SOLUTION


# %%
try:
    cards = card_table(CARDS)
except NotImplementedError:
    cards = pd.DataFrame([{"caller_id": c["caller_id"], "language": c["language"], "dialect": c["dialect"],
                           "behaviour": c["behaviour"], "changes": c["change_to"] is not None} for c in CARDS])
print(cards.behaviour.value_counts().to_string())
print(pd.crosstab(cards.dialect, cards.language).to_string())

# %% [markdown]
# ## 2 · Run the calls (8')
#
# ✏️ **Exercise** · For each card: a fresh `R.Store()`, `agent = release_candidate(store)`, then
# `R.run_call(card, agent)`. Keep the store and the result of every call. Print one full call, turn by turn, with what
# the caller said, what the recogniser heard and what Rahhal answered.

# %%
def run_all(make_agent):
    runs = []
    # BEGIN SOLUTION
    for card in CARDS:
        store = R.Store()
        result = R.run_call(card, make_agent(store))
        runs.append({"card": card, "store": store, "result": result})
    # END SOLUTION
    return runs


# %%
def _run_all_ref(make_agent):
    out = []
    for card in CARDS:
        store = R.Store()
        out.append({"card": card, "store": store, "result": R.run_call(card, make_agent(store))})
    return out


try:
    runs = run_all(release_candidate)
    assert runs
except (NotImplementedError, AssertionError):
    run_all = _run_all_ref
    runs = run_all(release_candidate)
show = next(r for r in runs if r["card"]["caller_id"] == "SC04")
for t in show["result"]["turns"]:
    print("said: ", t["said"], "\nheard:", t["heard"], "\nagent:", t["agent"], "\n")

# %% [markdown]
# ## 3 · Grade from the store (7')
#
# What Rahhal **said** is not evidence: an agent can announce a booking it did not make, or make one it did not
# announce. A call passes when the store holds exactly one booking for the caller, and it matches the caller's final
# goal (after any change of mind: `result["goal"]`).
#
# ✏️ **Exercise** · Write `grade(run)` returning `passed`, `reason` (`ok`, `no booking`, `wrong date`, `wrong party`,
# `wrong site`, `duplicate`) and `turns`.

# %%
def grade(run):
    # BEGIN SOLUTION
    goal, mine = run["result"]["goal"], [b for b in run["store"].bookings if b["name"] == run["card"]["caller_id"]]
    turns = len(run["result"]["turns"])
    if not mine:
        return {"passed": False, "reason": "no booking", "turns": turns}
    if len(mine) > 1:
        return {"passed": False, "reason": "duplicate", "turns": turns}
    b = mine[0]
    for field, reason in (("site_code", "wrong site"), ("date", "wrong date"), ("party_size", "wrong party")):
        if b[field] != goal[field]:
            return {"passed": False, "reason": reason, "turns": turns}
    return {"passed": True, "reason": "ok", "turns": turns}
    # END SOLUTION


# %%
def _grade_ref(run):
    goal, mine = run["result"]["goal"], [b for b in run["store"].bookings if b["name"] == run["card"]["caller_id"]]
    n = len(run["result"]["turns"])
    if len(mine) != 1:
        return {"passed": False, "reason": "no booking" if not mine else "duplicate", "turns": n}
    for f, why in (("site_code", "wrong site"), ("date", "wrong date"), ("party_size", "wrong party")):
        if mine[0][f] != goal[f]:
            return {"passed": False, "reason": why, "turns": n}
    return {"passed": True, "reason": "ok", "turns": n}


try:
    grade(runs[0])
except NotImplementedError:
    grade = _grade_ref
graded = pd.DataFrame([{"caller_id": r["card"]["caller_id"], **grade(r)} for r in runs]).merge(cards, on="caller_id")
k, n = int(graded.passed.sum()), len(graded)
lo, hi = U.wilson(k, n)
print(f"task success {k}/{n} (95% interval {lo:.2f} to {hi:.2f})")
print(graded[~graded.passed][["caller_id", "behaviour", "dialect", "reason", "turns"]].to_string(index=False))
U.check(k < n, "the release candidate fails some simulated callers")

# %% [markdown]
# ## 4 · Transcript errors and failures by behaviour (7')
#
# ✏️ **Exercise** · (a) The word error rate of what the recogniser heard against what the caller said, over all caller
# turns, overall and by dialect (`U.wer(refs, hyps)`, full rules). (b) Failures by behaviour. (c) Read one failing
# call: which slots did the tool receive, and which had the caller confirmed last?

# %%
def transcript_wer(runs):
    # BEGIN SOLUTION
    rows = [{"dialect": r["card"]["dialect"], "said": t["said"], "heard": t["heard"]}
            for r in runs for t in r["result"]["turns"]]
    df = pd.DataFrame(rows)
    by = {d: round(U.wer(list(g.said), list(g.heard)), 3) for d, g in df.groupby("dialect")}
    return round(U.wer(list(df.said), list(df.heard)), 3), by
    # END SOLUTION


# %%
try:
    overall, by_dialect = transcript_wer(runs)
except NotImplementedError:
    df = pd.DataFrame([{"dialect": r["card"]["dialect"], "said": t["said"], "heard": t["heard"]} for r in runs for t in r["result"]["turns"]])
    overall = round(U.wer(list(df.said), list(df.heard)), 3)
    by_dialect = {d: round(U.wer(list(g.said), list(g.heard)), 3) for d, g in df.groupby("dialect")}
print("transcript WER overall", overall, "| by dialect", by_dialect)
by_behaviour = graded.groupby("behaviour").agg(calls=("passed", "size"), failed=("passed", lambda s: int((~s).sum())))
print(by_behaviour.to_string())
fail = next(r for r in runs if not grade(r)["passed"])
print("\n", fail["card"]["caller_id"], "final goal", fail["result"]["goal"], "| booked",
      [(b["site_code"], b["date"], b["party_size"]) for b in fail["store"].bookings])
for t in fail["result"]["turns"]:
    print("   heard:", t["heard"], "| agent:", t["agent"])
graded.to_csv(U.artifacts("D4_2") / "graded_calls.csv", index=False)

# %% [markdown]
# 🔍 **Look at** the last read-back before each failing booking: Rahhal read the corrected date back, and the caller
# said yes to it, but the booking carries the date first heard. The bug is in the agent (`stale_confirmation`), not in
# the recogniser. Now fix it and run the same twenty callers again.

# %%
def fixed_candidate(store):
    agent = release_candidate(store)
    agent.stale_confirmation = False
    return agent


after = pd.DataFrame([{"caller_id": r["card"]["caller_id"], **grade(r)} for r in run_all(fixed_candidate)])
print("after the fix:", int(after.passed.sum()), "/", len(after))
U.check(after.passed.all(), "with the fix, every simulated caller gets the booking they confirmed")

# %% [markdown]
# ## ✱ Stretch · A hosted model as the caller
#
# The scripted callers say exactly what their card says. A language model playing the caller varies its wording and
# finds paths the script never takes. With `HT_PROVIDER=hosted` and a key, write a caller prompt from a card and let
# a free hosted model reply to Rahhal for up to eight turns; grade from the store as before.

# %%
# BEGIN SOLUTION
def card_prompt(card):
    g = card["goal"]
    site = R.SITES[g["site_code"]][1 if card["language"] == "ar" else 0]
    return (f"You are phoning a heritage site booking line. Speak {'Saudi Arabic' if card['language'] == 'ar' else 'English'} "
            f"in short phone turns. You want {site} on {g['date']} for {g['party_size']} people. "
            f"Behaviour: {card['behaviour']}. Say yes only if the read-back matches what you want.")


print(card_prompt(CARDS[3]))
if U.hosted("vision"):
    print("hosted caller: wire card_prompt into a chat model and loop with agent.respond (left to the participant)")
else:
    print("no hosted key: the stretch runs only the prompt here")
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why grade from the store rather than from Rahhal's last line?
# 2. Which behaviour failed, and was the recogniser to blame?
# 3. The fix passes 20 of 20. What does that not prove?
#
# <details><summary>Answers</summary>
#
# 1. The store is what the visitor will find on the day; the agent's words can claim a booking that does not exist or
#    match the wrong one.
# 2. Callers who changed or corrected the date. The recogniser's error was caught by the read-back; the booking still
#    used the first-heard slots.
# 3. That real callers behave like twenty scripts; the interval on 20 of 20 still reaches down to about 0.84.
# </details>
#
# **Carry forward.** `artifacts/D4_2/graded_calls.csv` is the capstone's end-to-end result.
