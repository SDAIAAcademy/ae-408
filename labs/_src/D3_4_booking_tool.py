# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 3.4 · A confirmed booking tool
#
# Day 3 · Session 4 (Tool calls during speech) · 25 min.
#
# The provided Rahhal books as soon as it has a site, a date and a party size. On a phone line, what it "has" is what
# the recogniser heard. You write the booking tool with its checks, switch the agent to confirm the key fields aloud
# before it books, run six scripted calls to prove that nothing is booked without a yes, and measure what the tool
# adds to the time to first audio.
#
# **Reference state.** `rahhal.py` (the agent, the store, the modelled clock) and six scripted calls in this notebook,
# written as the recogniser heard them. No model is called.
#
# **Tasks**
# - [ ] 1 · The booking tool and its argument checks (5')
# - [ ] 2 · Confirm site, date and party size aloud before the call (8')
# - [ ] 3 · Six scripted calls: no booking without a yes (6')
# - [ ] 4 · Measure the added time and fill the gap (6')
# - [ ] ✱ Stretch · Make a retried booking safe with an idempotency key

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

import datetime as dt

import pandas as pd

import rahhal as R
import trails as U

CALLS = [
    {"id": "K1", "intended": ("HT-03", "2026-12-03", 7),
     "heard": ["I would like to book Palm Fort on 2026-12-03 for 7 people", "yes book it"]},
    {"id": "K2", "intended": ("HT-07", "2026-12-11", 4),  # the recogniser heard 14 for 11
     "heard": ["أبي أحجز جولة في شعب النقوش يوم 2026-12-14 لعدد 4 أشخاص", "لا، يوم 2026-12-11", "نعم احجز"]},
    {"id": "K3", "intended": ("HT-05", "2026-12-20", 3),
     "heard": ["I want to visit Falcon Ridge", "on 2026-12-20", "for 3 people", "yes"]},
    {"id": "K4", "intended": ("HT-10", "2026-12-06", 5),  # the 5th is nearly full
     "heard": ["أبي أحجز في بستان العين يوم 2026-12-05 لعدد 5 أشخاص", "نعم احجز", "يوم 2026-12-06", "نعم احجز"]},
    {"id": "K5", "intended": ("HT-06", "2026-12-09", 5),  # the recogniser heard 6 for 5
     "heard": ["Book Clay Village on 2026-12-09 for 6 people", "no, for 5 people", "yes"]},
    {"id": "K6", "intended": ("HT-11", "2026-12-20", 2),
     "heard": ["Book Caravan Road on 2026-11-20 for 2 people", "yes", "on 2026-12-20", "yes"]},
]
print(len(CALLS), "scripted calls; today on the line is", R.TODAY)

# %% [markdown]
# ## 1 · The booking tool (5')
#
# ✏️ **Exercise** · `make_tool(store)` returns `book_visit(site_code, date, party_size, name)`, which raises
# `R.ToolError` with a sentence the agent can say when: the site is unknown; the date is not a valid date, is before
# today or more than 60 days ahead; the party is not 1 to 12; or the booking would take the site over its capacity of
# 20 visitors that day. Otherwise it calls `store.add(...)` and returns the reference.

# %%
def make_tool(store):
    def book_visit(site_code, date, party_size, name):
        # BEGIN SOLUTION
        if site_code not in R.SITES:
            raise R.ToolError("that site is not one of ours")
        try:
            d = dt.date.fromisoformat(date)
        except ValueError:
            raise R.ToolError("I did not get a valid date")
        if d < R.TODAY:
            raise R.ToolError("that date has passed")
        if (d - R.TODAY).days > 60:
            raise R.ToolError("we book up to 60 days ahead")
        if not 1 <= party_size <= 12:
            raise R.ToolError("a group can be 1 to 12 people")
        if store.booked(site_code, date) + party_size > R.CAPACITY:
            raise R.ToolError("that day is full for a group of that size")
        return store.add(site_code, date, party_size, name)
        # END SOLUTION
    return book_visit


# %%
def _make_tool_ref(store):
    def book_visit(site_code, date, party_size, name):
        d = dt.date.fromisoformat(date)
        if site_code not in R.SITES or d < R.TODAY or (d - R.TODAY).days > 60 or not 1 <= party_size <= 12:
            raise R.ToolError("that booking is not possible")
        if store.booked(site_code, date) + party_size > R.CAPACITY:
            raise R.ToolError("that day is full for a group of that size")
        return store.add(site_code, date, party_size, name)
    return book_visit


def fresh_store():
    s = R.Store()
    s.add("HT-10", "2026-12-05", 18, "earlier group")  # planted: the 5th at Spring Garden is nearly full
    return s


try:
    make_tool(fresh_store())("HT-01", "2026-12-02", 2, "test")
except NotImplementedError:
    make_tool = _make_tool_ref
s = fresh_store()
tool = make_tool(s)
errors = []
for args in [("HT-99", "2026-12-02", 2), ("HT-01", "2026-11-20", 2), ("HT-01", "2026-12-02", 14), ("HT-10", "2026-12-05", 5)]:
    try:
        tool(*args, "test")
        errors.append(None)
    except R.ToolError as e:
        errors.append(str(e))
print(errors)
U.check(all(errors), "the tool refuses an unknown site, a past date, a party of 14 and a full day")

# %% [markdown]
# ## 2 · Confirm before the call (8')
#
# Two policies are built into `R.Rahhal`: `book_when_full` (the provided starting point) and `confirm_then_book`, which
# reads the slots back and books only after a yes, and reads them back again after any change.
#
# ✏️ **Exercise** · Write `run(call, policy, filler=False)` that creates a store with `fresh_store()`, an agent with
# your tool and the policy, sends each heard turn to `agent.respond`, and returns the store, the agent and the
# replies. Run K2 with both policies and print the conversation.

# %%
def run(call, policy, filler=False):
    # BEGIN SOLUTION
    store = fresh_store()
    agent = R.Rahhal(book_tool=make_tool(store), policy=policy, filler=filler)
    agent.name = call["id"]
    replies = []
    for heard in call["heard"]:
        if agent.booked_ref:
            break
        replies.append(agent.respond(heard))
    return store, agent, replies
    # END SOLUTION


# %%
def _run_ref(call, policy, filler=False):
    store = fresh_store()
    agent = R.Rahhal(book_tool=make_tool(store), policy=policy, filler=filler)
    agent.name, replies = call["id"], []
    for heard in call["heard"]:
        if agent.booked_ref:
            break
        replies.append(agent.respond(heard))
    return store, agent, replies


try:
    run(CALLS[0], "confirm_then_book")
except NotImplementedError:
    run = _run_ref
for policy in ("book_when_full", "confirm_then_book"):
    _, _, replies = run(CALLS[1], policy)
    print(policy)
    for heard, reply in zip(CALLS[1]["heard"], replies):
        print("   caller:", heard, "\n   Rahhal:", reply)

# %% [markdown]
# ## 3 · Six calls, graded (6')
#
# ✏️ **Exercise** · Run all six calls with both policies. A call **passes** when the store holds exactly one new
# booking and it matches `intended`. Count, per policy, the passes and the bookings made with a wrong field.

# %%
def grade(store, call):
    new = [b for b in store.bookings if b["name"] == call["id"]]
    return len(new) == 1 and (new[0]["site_code"], new[0]["date"], new[0]["party_size"]) == call["intended"], new


def grade_all(policy):
    rows = []
    # BEGIN SOLUTION
    for call in CALLS:
        store, agent, replies = run(call, policy)
        ok, new = grade(store, call)
        rows.append({"call": call["id"], "policy": policy, "pass": ok, "bookings": len(new),
                     "wrong_booking": bool(new) and not ok, "turns": len(replies)})
    # END SOLUTION
    return pd.DataFrame(rows)


# %%
try:
    graded = pd.concat([grade_all("book_when_full"), grade_all("confirm_then_book")])
except NotImplementedError:
    graded = pd.concat([pd.DataFrame([{"call": c["id"], "policy": p, "pass": grade(run(c, p)[0], c)[0],
                                       "wrong_booking": bool(grade(run(c, p)[0], c)[1]) and not grade(run(c, p)[0], c)[0]}
                                      for c in CALLS]) for p in ("book_when_full", "confirm_then_book")])
print(graded.to_string(index=False))
summary = graded.groupby("policy")[["pass", "wrong_booking"]].sum()
print(summary)
U.check(summary.loc["confirm_then_book", "pass"] == 6 and summary.loc["confirm_then_book", "wrong_booking"] == 0,
        "with confirmation every call books the intended visit and nothing else")

# %% [markdown]
# ## 4 · The added time, and a filler (6')
#
# `agent.trace` holds the modelled clock of every turn: the stages, `tool_ms` and `ttfa_ms`. The booking tool takes
# 900 ms: on the booking turn the caller hears nothing until it returns.
#
# ✏️ **Exercise** · For K1 with confirmation, print `ttfa_ms` per turn without and with `filler=True` (Rahhal says
# "one moment, I am booking that" at the normal time and the result follows). Then decide: is the filler honest?

# %%
def ttfa_by_turn(call, filler):
    # BEGIN SOLUTION
    _, agent, _ = run(call, "confirm_then_book", filler=filler)
    return [(e["turn"], e["tool"], e["ttfa_ms"]) for e in agent.trace]
    # END SOLUTION


# %%
try:
    plain_t, fill_t = ttfa_by_turn(CALLS[0], False), ttfa_by_turn(CALLS[0], True)
except NotImplementedError:
    plain_t = [(e["turn"], e["tool"], e["ttfa_ms"]) for e in run(CALLS[0], "confirm_then_book")[1].trace]
    fill_t = [(e["turn"], e["tool"], e["ttfa_ms"]) for e in run(CALLS[0], "confirm_then_book", True)[1].trace]
print("without filler:", plain_t)
print("with filler:   ", fill_t)
booking_turn = [t for t in plain_t if t[1]][0]
booking_fill = [t for t in fill_t if t[1]][0]
ordinary = sum(R.STAGES.values()) + 120  # the slowest turn without a tool on this modelled clock
print(f"booking turn: {booking_turn[2]} ms without a filler, {booking_fill[2]} ms with one (ordinary turns up to {ordinary})")
U.check(booking_turn[2] > U.BUDGET_TTFA_MS + 500 and booking_fill[2] <= ordinary,
        "the tool adds its 900 ms to the silence; the filler brings the first audio back to an ordinary turn")

# %% [markdown]
# 🔍 **Look at** what the filler says. "One moment, I am booking that" is true; "Your booking is confirmed" before the
# tool returns is not, and K4 shows why: the 5th was full.

# %% [markdown]
# ## ✱ Stretch · A retry that does not book twice
#
# The booking call can time out after the store has written the booking. A retry would book twice. Give each
# confirmed booking an idempotency key (the call id and the confirmed slots) and show that two calls with the same key
# leave one booking.

# %%
# BEGIN SOLUTION
st = fresh_store()
key = "K1|HT-03|2026-12-03|7"
r1 = st.add("HT-03", "2026-12-03", 7, "K1", key=key)
r2 = st.add("HT-03", "2026-12-03", 7, "K1", key=key)
print(r1, r2, "| bookings for K1:", sum(b["name"] == "K1" for b in st.bookings))
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. In K2 the provided agent booked the 14th. Which field did the recogniser get wrong, and what caught it?
# 2. Why read the fields back before the tool call and not after?
# 3. When is a filler line dishonest?
#
# <details><summary>Answers</summary>
#
# 1. The date (11 heard as 14). The read-back: the caller heard the wrong date and said no.
# 2. After the call the booking exists; a correction then needs a cancellation, and the caller may hang up first.
# 3. When it claims a result the tool has not returned yet.
# </details>
#
# **Carry forward.** The confirmation policy and the tool are the core of the capstone agent; Lab 4.2 tests a version
# of this agent with simulated callers.
