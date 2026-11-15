# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 1.2 · Validated incident fields
#
# Day 1 · Session 2 (Structured extraction from photos) · 25 min.
#
# Every photo report becomes an incident record that the rangers' work queue can sort: type, severity, hazard,
# site, the text of any sign, and how many people are visible. You write the schema, extract from 30 photos with an
# open-weight and a hosted model, repair invalid replies once, and measure field accuracy per model and per field.
#
# **Reference state.** Photos P001 to P030 and their reference fields in `data/photos/refs.jsonl`.
#
# **Tasks**
# - [ ] 1 · The incident schema with enums and validators (6')
# - [ ] 2 · Extract from 30 photos with two models, one repair each (8')
# - [ ] 3 · Field accuracy per model and per field (6')
# - [ ] 4 · Cost and latency per photo (5')
# - [ ] ✱ Stretch · Let the schema say "unknown" and count how many guesses it removes

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
from typing import Literal, Optional

import pandas as pd
from pydantic import BaseModel, Field, ValidationError

import trails as U

PHOTOS = [f"P{i:03d}" for i in range(1, U.pick(31, 11))]
print(len(PHOTOS), "photos |", "hosted" if U.hosted("vision") else "scripted stand-in")

# %% [markdown]
# ## 1 · The schema (6')
#
# ✏️ **Exercise** · Define `Incident` with six fields:
# `incident_type` (one of `rockfall`, `damaged_sign`, `litter`, `broken_fence`, `blocked_path`, `graffiti`, `none`),
# `severity` (`none`, `low`, `medium`, `high`), `hazard_to_visitors` (bool), `site_code` (`HT-` and two digits, or
# `None` when no marker is readable), `sign_text` (text or `None`) and `people_visible` (0 to 20).
# Each constraint you write is one mistake the model can no longer make silently.

# %%
# BEGIN SOLUTION
class Incident(BaseModel):
    incident_type: Literal["rockfall", "damaged_sign", "litter", "broken_fence", "blocked_path", "graffiti", "none"]
    severity: Literal["none", "low", "medium", "high"]
    hazard_to_visitors: bool
    site_code: Optional[str] = Field(default=None, pattern=r"^HT-\d{2}$")
    sign_text: Optional[str] = None
    people_visible: int = Field(ge=0, le=20)
# END SOLUTION

# %%
try:
    Incident
except NameError:
    class Incident(BaseModel):
        incident_type: Literal["rockfall", "damaged_sign", "litter", "broken_fence", "blocked_path", "graffiti", "none"]
        severity: Literal["none", "low", "medium", "high"]
        hazard_to_visitors: bool
        site_code: Optional[str] = Field(default=None, pattern=r"^HT-\d{2}$")
        sign_text: Optional[str] = None
        people_visible: int = Field(ge=0, le=20)
bad = {"incident_type": "fallen rocks", "severity": "HIGH", "hazard_to_visitors": True, "site_code": "HT-7",
       "sign_text": None, "people_visible": 1}
try:
    Incident.model_validate(bad)
    caught = 0
except ValidationError as e:
    caught = e.error_count()
U.check(caught == 3, "the schema rejects a wrong type, an upper-case severity and a short code (3 errors)")

# %% [markdown]
# ## 2 · Extract, validate, repair once (8')
#
# The prompt carries the schema. The reply is validated anyway: a reply can be wrapped in prose, or use a word that is
# not in the enum.
#
# ✏️ **Exercise** · Write `extract(photo_id, model)` that returns `(Incident or None, repairs, reply)`:
# 1. call `U.vlm(photo_id, PROMPT, model=model, width=640, system=SYSTEM, task="extract")`;
# 2. take the text from the first `{` to the last `}` and validate it;
# 3. on `ValidationError`, call again with `history=[{"role": "assistant", "content": <reply text>},
#    {"role": "user", "content": "That JSON is invalid: <the error>. Reply with corrected JSON only."}]`;
# 4. after one failed repair, return `None`.

# %%
SYSTEM = "You turn trail photos into incident records for park rangers. Reply with one JSON object only."
PROMPT = "Fill this JSON Schema from the photo:\n" + json.dumps(Incident.model_json_schema())


def parse(text):
    a, b = text.find("{"), text.rfind("}")
    return Incident.model_validate_json(text[a:b + 1] if a >= 0 else text)


def extract(photo_id, model):
    # BEGIN SOLUTION
    r = U.vlm(photo_id, PROMPT, model=model, width=640, system=SYSTEM, task="extract")
    replies = [r]
    try:
        return parse(r.text), 0, replies
    except ValidationError as e:
        hist = [{"role": "assistant", "content": r.text},
                {"role": "user", "content": f"That JSON is invalid: {e}. Reply with corrected JSON only."}]
        r2 = U.vlm(photo_id, PROMPT, model=model, width=640, system=SYSTEM, history=hist, task="extract")
        replies.append(r2)
        try:
            return parse(r2.text), 1, replies
        except ValidationError:
            return None, 1, replies
    # END SOLUTION


# %%
def run(model):
    rows = []
    for pid in PHOTOS:
        try:
            obj, repairs, replies = extract(pid, model)
        except NotImplementedError:  # safety net: the reference extraction with one repair
            r = U.vlm(pid, PROMPT, model=model, width=640, system=SYSTEM, task="extract")
            try:
                obj, repairs, replies = parse(r.text), 0, [r]
            except ValidationError as e:
                hist = [{"role": "assistant", "content": r.text},
                        {"role": "user", "content": f"That JSON is invalid: {e}. Reply with corrected JSON only."}]
                r2 = U.vlm(pid, PROMPT, model=model, width=640, system=SYSTEM, history=hist, task="extract")
                obj, repairs, replies = parse(r2.text), 1, [r, r2]
        rows.append({"photo_id": pid, "model": model, "obj": obj, "repairs": repairs,
                     "tokens": sum(x.prompt_tokens + x.completion_tokens for x in replies),
                     "latency_ms": sum(x.latency_ms for x in replies)})
    return rows


results = pd.DataFrame(run("open") + run("hosted"))
print(results.groupby("model").agg(valid=("obj", lambda s: s.notna().sum()), repairs=("repairs", "sum")))
U.check(results.obj.notna().all(), "every reply is valid after at most one repair", model=True)

# %% [markdown]
# ## 3 · Field accuracy (6')
#
# ✏️ **Exercise** · Compare each valid record with its reference fields. Return a table with one row per model and
# one column per field: the share of photos where the field is exactly right (an invalid record counts as wrong on
# every field). Then the mean over fields.

# %%
FIELDS = list(Incident.model_fields)


def field_accuracy(results):
    # BEGIN SOLUTION
    rows = []
    for _, r in results.iterrows():
        ref = U.REFS[r.photo_id]["fields"]
        got = r.obj.model_dump() if r.obj is not None else {}
        rows.append({"model": r.model, **{f: got.get(f, "∅") == ref[f] for f in FIELDS}})
    t = pd.DataFrame(rows).groupby("model")[FIELDS].mean()
    t["mean"] = t.mean(axis=1)
    return t.round(2)
    # END SOLUTION


# %%
try:
    acc = field_accuracy(results)
except NotImplementedError:
    acc = pd.DataFrame([{"model": r.model, **{f: (r.obj.model_dump() if r.obj else {}).get(f, "∅") == U.REFS[r.photo_id]["fields"][f]
                                              for f in FIELDS}} for _, r in results.iterrows()]).groupby("model")[FIELDS].mean()
    acc["mean"] = acc.mean(axis=1)
print(acc.to_string())
U.check(acc.loc["hosted", "mean"] > acc.loc["open", "mean"], "the hosted model is more accurate on this set", model=True)

# %% [markdown]
# 🔍 **Look at** `sign_text`: exact match is harsh for text read from a photo. Lab 1.4 scores it with a character
# error rate instead. And at `severity` for the two models: which field would you send to a ranger for review?

# %% [markdown]
# ## 4 · Cost and latency per photo (5')
#
# ✏️ **Exercise** · Per model: mean tokens per photo (repairs included), median and 90th-percentile latency, and the
# mean field accuracy from step 3, in one table.

# %%
def cost_table(results, acc):
    # BEGIN SOLUTION
    t = results.groupby("model").agg(tokens_per_photo=("tokens", "mean"),
                                     p50_ms=("latency_ms", "median"),
                                     p90_ms=("latency_ms", lambda s: U.pct(s, 90)))
    t["field_accuracy"] = acc["mean"]
    return t.round(1)
    # END SOLUTION


# %%
try:
    cost = cost_table(results, acc)
except NotImplementedError:
    cost = results.groupby("model").agg(tokens_per_photo=("tokens", "mean"), p50_ms=("latency_ms", "median"))
    cost["field_accuracy"] = acc["mean"]
print(cost.to_string())
U.check(set(cost.index) == {"open", "hosted"}, "one row per model")

# %% [markdown]
# ## ✱ Stretch · "unknown" instead of a guess
#
# Tell the model in the prompt that `site_code` must be `null` ("unknown") when the marker is not clearly readable.
# Count, for the open model, how many wrong codes become `null` and how many right codes are lost.

# %%
# BEGIN SOLUTION
P2 = PROMPT + "\nIf the marker code is not clearly readable, set site_code to null (unknown). Never guess."
before = after = lost = 0
for pid in PHOTOS:
    ref = U.REFS[pid]["fields"]["site_code"]
    a = parse(U.vlm(pid, PROMPT, model="open", system=SYSTEM, history=[{"role": "user", "content": "invalid"}], task="extract").text)
    b = parse(U.vlm(pid, P2, model="open", system=SYSTEM, history=[{"role": "user", "content": "invalid"}], task="extract").text)
    before += a.site_code not in (None, ref)
    after += b.site_code not in (None, ref)
    lost += (a.site_code == ref and b.site_code is None and ref is not None)
print(f"wrong codes: {before} before, {after} after; right codes lost: {lost}")
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. One reply was valid JSON but said `"fallen rocks"`. What caught it, and what did the repair send back?
# 2. Why validate a reply that the prompt already constrained with a schema?
# 3. Which field would you let the model leave empty, and why?
#
# <details><summary>Answers</summary>
#
# 1. The enum of `incident_type`. The repair sent the validation error itself, which names the field and the values
#    allowed.
# 2. A prompt is a request, not a guarantee: free endpoints differ in how they honour response formats.
# 3. `site_code` (and `sign_text`): an empty field sends the report to a person; a wrong code sends rangers to the
#    wrong site.
# </details>
#
# **Carry forward.** The `Incident` schema is the record of the capstone's photo pipeline.
