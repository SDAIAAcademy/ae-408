# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 4.3 · The decision record
#
# Day 4 · Session 3 (Choosing by quality, latency and cost) · 25 min.
#
# Wedad must choose Rahhal's production design: the **cascaded** pipeline on open-weight models on one rented node, or
# a **hosted speech-to-speech** model billed per minute. Both were run on the same 60 test calls. You compute cost per
# call and the break-even volume, put quality, latency and cost in one table with intervals, and write a one-page
# decision record with a fingerprint that a reviewer re-runs to the same figures.
#
# **Reference state.** `data/pipelines.json`: measured results for the two pipelines on 60 calls, and the case study's
# prices and volume. **The prices are illustrative**, supplied by the case study; they are not vendor prices.
#
# **Tasks**
# - [ ] 1 · Load the measured results (4')
# - [ ] 2 · Cost per call and the break-even volume (7')
# - [ ] 3 · Quality, latency and cost in one table (6')
# - [ ] 4 · The decision record and its fingerprint (8')
# - [ ] ✱ Stretch · Vary the call volume and find where the decision changes

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

import hashlib
import json

import pandas as pd

import trails as U

RAW = (U.DATA / "pipelines.json").read_text(encoding="utf-8").replace("\r\n", "\n")  # same text on every platform
P = json.loads(RAW)
print(P["note"])
print(json.dumps(P["pipelines"]["cascaded_open_weight"], indent=1)[:400])

# %% [markdown]
# ## 1 · Load (4')
#
# ✏️ **Exercise** · Put both pipelines in a table, one row each: `fixed_per_month`, `per_minute`, `passed`, `n`,
# `wer_overall`, `ttfa_p50`, `ttfa_p90`.

# %%
def load(p):
    # BEGIN SOLUTION
    rows = {}
    for name, x in p["pipelines"].items():
        rows[name] = {"fixed_per_month": x["fixed_per_month"], "per_minute": x["per_minute"],
                      "passed": x["task_success"]["passed"], "n": x["task_success"]["n"],
                      "wer_overall": x["wer_overall"], "ttfa_p50": x["ttfa_ms"]["p50"], "ttfa_p90": x["ttfa_ms"]["p90"]}
    return pd.DataFrame(rows).T
    # END SOLUTION


# %%
try:
    T = load(P)
except NotImplementedError:
    T = pd.DataFrame({k: {"fixed_per_month": x["fixed_per_month"], "per_minute": x["per_minute"],
                          "passed": x["task_success"]["passed"], "n": x["task_success"]["n"],
                          "wer_overall": x["wer_overall"], "ttfa_p50": x["ttfa_ms"]["p50"], "ttfa_p90": x["ttfa_ms"]["p90"]}
                      for k, x in P["pipelines"].items()}).T
print(T.to_string())

# %% [markdown]
# ## 2 · Cost per call and break-even (7')
#
# Cost per call = fixed per month / calls per month + price per minute × minutes per call.
#
# ✏️ **Exercise** · Compute the monthly cost and the cost per call of each pipeline at the case study's volume, and the
# volume at which the two cost the same per call.

# %%
CALLS, MINUTES = P["calls_per_month"], P["minutes_per_call"]


def cost_per_call(row, calls=CALLS):
    # BEGIN SOLUTION
    return row["fixed_per_month"] / calls + row["per_minute"] * MINUTES
    # END SOLUTION


def break_even(a, b):
    # BEGIN SOLUTION
    # fixed_a / N + m_a = fixed_b / N + m_b  ->  N = (fixed_a - fixed_b) / (m_b - m_a), with m = per_minute * MINUTES
    return (a["fixed_per_month"] - b["fixed_per_month"]) / ((b["per_minute"] - a["per_minute"]) * MINUTES)
    # END SOLUTION


# %%
try:
    T["cost_per_call"] = [round(cost_per_call(r), 3) for _, r in T.iterrows()]
    be = break_even(T.loc["cascaded_open_weight"], T.loc["hosted_speech_to_speech"])
except NotImplementedError:
    T["cost_per_call"] = [round(r.fixed_per_month / CALLS + r.per_minute * MINUTES, 3) for _, r in T.iterrows()]
    a, b = T.loc["cascaded_open_weight"], T.loc["hosted_speech_to_speech"]
    be = (a.fixed_per_month - b.fixed_per_month) / ((b.per_minute - a.per_minute) * MINUTES)
T["cost_per_month"] = (T.cost_per_call * CALLS).round(0)
print(T[["cost_per_call", "cost_per_month"]].to_string())
print(f"break-even: {be:,.0f} calls a month")
U.check(abs(T.loc["cascaded_open_weight", "cost_per_call"] - (14500 / 18000 + 0.064)) < 0.01 and 4000 < be < 6000,
        "cost per call and break-even computed from the supplied prices")

# %% [markdown]
# ## 3 · One table (6')
#
# ✏️ **Exercise** · One row per pipeline: task success with its Wilson interval, WER (or "no transcript"), time to
# first audio at p50 and p90 with "within budget" for p90, and cost per call. Then answer: is the difference in task
# success shown?

# %%
def decision_table(T):
    # BEGIN SOLUTION
    rows = []
    for name, r in T.iterrows():
        lo, hi = U.wilson(int(r.passed), int(r.n))
        rows.append({"pipeline": name, "task_success": f"{int(r.passed)}/{int(r.n)}", "interval": f"{lo:.2f} to {hi:.2f}",
                     "wer": "no transcript" if pd.isna(r.wer_overall) else f"{r.wer_overall:.3f}",
                     "ttfa_p50_ms": int(r.ttfa_p50), "ttfa_p90_ms": int(r.ttfa_p90),
                     "p90_within_budget": bool(r.ttfa_p90 <= U.BUDGET_TTFA_MS), "sar_per_call": round(r.cost_per_call, 2)})
    return pd.DataFrame(rows).set_index("pipeline")
    # END SOLUTION


# %%
try:
    D = decision_table(T)
except NotImplementedError:
    D = pd.DataFrame([{"pipeline": k, "task_success": f"{int(r.passed)}/{int(r.n)}",
                       "interval": "{:.2f} to {:.2f}".format(*U.wilson(int(r.passed), int(r.n))),
                       "ttfa_p90_ms": int(r.ttfa_p90), "sar_per_call": round(r.cost_per_call, 2)} for k, r in T.iterrows()]).set_index("pipeline")
print(D.to_string())
a_lo, a_hi = U.wilson(51, 60)
b_lo, b_hi = U.wilson(54, 60)
shown = a_hi < b_lo or b_hi < a_lo
print("difference in task success shown:", shown)
U.check(not shown, "on 60 calls, task success is not shown to differ")

# %% [markdown]
# ## 4 · The decision record (8')
#
# ✏️ **Exercise** · Write `record(decision, reasons, conditions)` returning a Markdown page: the decision in one
# sentence, the table, the reasons, what would change the decision, and a **fingerprint**: the SHA-256 of the input
# file and of the table, so a reviewer who re-runs this notebook can show they got the same figures.

# %%
def fingerprint(raw, table):
    return hashlib.sha256((raw + table.to_csv()).encode("utf-8")).hexdigest()[:16]


def record(decision, reasons, conditions):
    # BEGIN SOLUTION
    lines = ["# Decision record: Rahhal's production pipeline", "", f"**Decision.** {decision}", "",
             "```\n" + D.to_string() + "\n```", "",
             f"Volume {CALLS:,} calls a month at {MINUTES} minutes; break-even {be:,.0f} calls a month. Prices are the case study's illustrative figures.",
             "", "**Reasons**", *[f"- {x}" for x in reasons], "", "**What would change it**", *[f"- {x}" for x in conditions], "",
             f"Fingerprint: `{fingerprint(RAW, D)}` (SHA-256 of data/pipelines.json and the table above, first 16 hex digits)."]
    return "\n".join(lines)
    # END SOLUTION


# %%
DECISION = ("Cascaded open-weight pipeline for the pilot, on condition that its 90th-percentile time to first audio "
            "is brought under 1,200 ms before launch.")
REASONS = ["Task success is not shown to differ on 60 calls (intervals overlap).",
           f"It costs {D.loc['cascaded_open_weight', 'sar_per_call']} SAR a call against "
           f"{D.loc['hosted_speech_to_speech', 'sar_per_call']} at 18,000 calls a month.",
           "It keeps a transcript, so the error rate can be reported by dialect and booking arguments checked.",
           "Audio is processed on a node the authority controls: one question fewer in the data protection review."]
CONDITIONS = ["p90 still above 1,200 ms after streaming and the hold rule (Day 3): reconsider the hosted design.",
              f"Volume below about {be:,.0f} calls a month: the hosted design becomes cheaper.",
              "A test set with more southern and Egyptian callers shows a difference in task success."]
try:
    page = record(DECISION, REASONS, CONDITIONS)
except NotImplementedError:
    page = "\n".join([f"Decision: {DECISION}", D.to_string(), f"Fingerprint: {fingerprint(RAW, D)}"])
print(page)
(U.artifacts("D4_3") / "decision_record.md").write_text(page, encoding="utf-8")
try:
    again = decision_table(T)
except NotImplementedError:
    again = D
U.check(fingerprint(RAW, again) == fingerprint(RAW, D),
        "the fingerprint is the same when the figures are recomputed")

# %% [markdown]
# 🔍 **Look at** the decision: it is one defensible reading of the table, not the answer. A team that weighs the 90th
# percentile above cost writes the opposite record from the same figures; what matters is that the record says why
# and what would change it.

# %% [markdown]
# ## ✱ Stretch · Vary the volume
#
# Cost per call for both pipelines at 3,000, 5,000, 18,000 and 60,000 calls a month. Above 60,000 the cascaded design
# needs a second node (`max_calls_per_month`): add a second fixed cost there.

# %%
# BEGIN SOLUTION
rows = []
for calls in (3000, 5000, 18000, 60000, 90000):
    nodes = -(-calls // P["pipelines"]["cascaded_open_weight"]["max_calls_per_month"])
    casc = nodes * T.loc["cascaded_open_weight", "fixed_per_month"] / calls + T.loc["cascaded_open_weight", "per_minute"] * MINUTES
    host = T.loc["hosted_speech_to_speech", "per_minute"] * MINUTES
    rows.append({"calls": calls, "nodes": nodes, "cascaded": round(casc, 2), "hosted": round(host, 2),
                 "cheaper": "cascaded" if casc < host else "hosted"})
print(pd.DataFrame(rows).to_string(index=False))
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. At what volume does the hosted design become cheaper per call, and why does it have no break-even above that?
# 2. Why is "51 of 60 against 54 of 60" not a reason to choose the hosted design?
# 3. What is the fingerprint for?
#
# <details><summary>Answers</summary>
#
# 1. Below about 4,900 calls a month. Its cost per call is constant (no fixed cost); the cascaded cost per call falls
#    as the fixed cost is spread over more calls.
# 2. The 95% intervals overlap: the test does not show a difference.
# 3. A reviewer re-runs the notebook and compares fingerprints: the same inputs and the same figures, or a reason why not.
# </details>
#
# **Carry forward.** `artifacts/D4_3/decision_record.md` is the capstone's decision record.
