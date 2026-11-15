# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 2.1 · Two recognisers, 50 clips
#
# Day 2 · Session 1 (From waveform to text) · 25 min.
#
# Wedad Al-Omari has to choose the recogniser behind Rahhal. You run two open-weight Whisper-family recognisers on 50
# booking clips (or replay their recorded transcripts), write word error rate from your own alignment, check it
# against jiwer, and see why a corpus figure and an average of clip figures disagree.
#
# **Reference state.** `data/clips.jsonl`: 50 synthetic clips with dialect, channel, code-switching, the reference
# transcript and the recorded transcripts of `whisper-large-v3` (A) and `whisper-large-v3-turbo` (B). The recorded
# transcripts were written by the course's error model, not by the recognisers: the README says how.
#
# **Tasks**
# - [ ] 1 · Load the clips and their references (4')
# - [ ] 2 · Transcribe with two recognisers, or replay (6')
# - [ ] 3 · Word error rate from your own alignment, checked with jiwer (8')
# - [ ] 4 · Corpus against mean error rate, and the worst clips (7')
# - [ ] ✱ Stretch · Character error rate beside word error rate for the same clips

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
import pandas as pd

import trails as U

print("speech path:", "hosted" if U.hosted("speech") else "recorded transcripts (stand-in)")

# %% [markdown]
# ## 1 · The clips (4')
#
# ✏️ **Exercise** · Load the clips into a DataFrame `clips` with `clip_id`, `dialect`, `channel`, `code_switched`,
# `seconds` and `reference`. Print how many clips there are per dialect and per channel.

# %%
def load():
    # BEGIN SOLUTION
    df = pd.DataFrame(U.clips())
    return df[["clip_id", "dialect", "channel", "code_switched", "seconds", "reference"]]
    # END SOLUTION


# %%
try:
    clips = load()
except NotImplementedError:
    clips = pd.DataFrame(U.clips())[["clip_id", "dialect", "channel", "code_switched", "seconds", "reference"]]
clips = clips.head(U.pick(50, 20))
print(pd.crosstab(clips.dialect, clips.channel))
print("code-switched:", int(clips.code_switched.sum()), "| total audio:", round(clips.seconds.sum() / 60, 1), "min")
U.check(len(clips) == U.pick(50, 20), "all clips loaded")

# %% [markdown]
# ## 2 · Two recognisers (6')
#
# `U.transcribe(clip, "A")` returns a `Reply` whose `text` is the transcript and `latency_ms` the time it took. With a
# Groq key and `HT_PROVIDER=hosted`, it sends `data/audio/<clip>.wav` when `make_audio.py` has written it; otherwise it
# replays the recorded transcript.
#
# ✏️ **Exercise** · Add columns `hyp_A`, `hyp_B`, `ms_A` and `ms_B` to `clips`.

# %%
def run_both(clips):
    # BEGIN SOLUTION
    by_id = {c["clip_id"]: c for c in U.clips()}
    for r in ("A", "B"):
        replies = [U.transcribe(by_id[i], r) for i in clips.clip_id]
        clips[f"hyp_{r}"] = [x.text for x in replies]
        clips[f"ms_{r}"] = [x.latency_ms for x in replies]
    return clips
    # END SOLUTION


# %%
try:
    clips = run_both(clips)
except NotImplementedError:
    by_id = {c["clip_id"]: c for c in U.clips()}
    for r in ("A", "B"):
        clips[f"hyp_{r}"] = [U.transcribe(by_id[i], r).text for i in clips.clip_id]
        clips[f"ms_{r}"] = [U.transcribe(by_id[i], r).latency_ms for i in clips.clip_id]
for _, r in clips.head(3).iterrows():
    print(r.clip_id, r.dialect, "\n  ref:", r.reference, "\n  A:  ", r.hyp_A, "\n  B:  ", r.hyp_B)
print("median latency A/B (ms):", clips.ms_A.median(), clips.ms_B.median())

# %% [markdown]
# ## 3 · Word error rate from your own alignment (8')
#
# WER = (substitutions + deletions + insertions) / words in the reference, from the alignment with the fewest edits.
#
# ✏️ **Exercise** · `align(ref_words, hyp_words)` returns `(S, D, I)`: fill a dynamic-programming table of edit
# costs, then walk back from the corner and count each kind of edit. Check your counts against
# `jiwer.process_words` on every clip of recogniser A.

# %%
def align(ref, hyp):
    # BEGIN SOLUTION
    n, m = len(ref), len(hyp)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]))
    i, j, S, D, I = n, m, 0, 0, 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]):
            S += ref[i - 1] != hyp[j - 1]
            i, j = i - 1, j - 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            D += 1
            i -= 1
        else:
            I += 1
            j -= 1
    return S, D, I
    # END SOLUTION


# %%
def jiwer_counts(ref, hyp):
    o = jiwer.process_words(" ".join(ref), " ".join(hyp))
    return o.substitutions, o.deletions, o.insertions


try:
    align(["a"], ["a"])
except NotImplementedError:
    align = jiwer_counts
agree = 0
for r in ("A", "B"):
    counts = [align(ref.split(), hyp.split()) for ref, hyp in zip(clips.reference, clips[f"hyp_{r}"])]
    clips[f"S_{r}"], clips[f"D_{r}"], clips[f"I_{r}"] = zip(*counts)
    clips[f"N"] = [len(x.split()) for x in clips.reference]
    agree += sum(sum(c) == sum(jiwer_counts(ref.split(), hyp.split()))
                 for c, ref, hyp in zip(counts, clips.reference, clips[f"hyp_{r}"]))
U.check(agree == 2 * len(clips), "your edit counts total the same as jiwer on every clip")

# %% [markdown]
# ## 4 · Corpus against mean, and the worst clips (7')
#
# ✏️ **Exercise** · For each recogniser compute the **corpus WER** (all edits over all reference words) and the
# **mean of clip WERs**. Then list the five clips with the highest WER for recogniser A, with dialect and channel.

# %%
def summary(clips):
    # BEGIN SOLUTION
    rows = {}
    for r in ("A", "B"):
        edits = clips[f"S_{r}"] + clips[f"D_{r}"] + clips[f"I_{r}"]
        clips[f"wer_{r}"] = edits / clips.N
        rows[U.ASR_MODELS[r]] = {"corpus_wer": round(edits.sum() / clips.N.sum(), 3),
                                 "mean_clip_wer": round(clips[f"wer_{r}"].mean(), 3),
                                 "S": int(clips[f"S_{r}"].sum()), "D": int(clips[f"D_{r}"].sum()), "I": int(clips[f"I_{r}"].sum())}
    return pd.DataFrame(rows).T
    # END SOLUTION


# %%
try:
    table = summary(clips)
except NotImplementedError:
    for r in ("A", "B"):
        clips[f"wer_{r}"] = (clips[f"S_{r}"] + clips[f"D_{r}"] + clips[f"I_{r}"]) / clips.N
    table = pd.DataFrame({U.ASR_MODELS[r]: {"corpus_wer": round(((clips[f"S_{r}"] + clips[f"D_{r}"] + clips[f"I_{r}"]).sum() / clips.N.sum()), 3),
                                           "mean_clip_wer": round(clips[f"wer_{r}"].mean(), 3)} for r in ("A", "B")}).T
print(table.to_string())
print(clips.sort_values("wer_A", ascending=False).head(5)[["clip_id", "dialect", "channel", "code_switched", "N", "wer_A"]].round(3).to_string(index=False))
U.check(abs(table.iloc[0].corpus_wer - U.wer(clips.reference.tolist(), clips.hyp_A.tolist(), "none")) < 1e-3,
        "corpus WER of A agrees with jiwer on raw text")

# %% [markdown]
# 🔍 **Look at** recogniser B: its WER is far higher than A's on raw text. Open three of its transcripts beside the
# references: are those errors a listener would notice? Session 2 answers that.

# %% [markdown]
# ## ✱ Stretch · Character error rate beside WER
#
# Compute the corpus CER for both recognisers with `jiwer.cer` and compare the ranking with WER.

# %%
# BEGIN SOLUTION
for r in ("A", "B"):
    print(U.ASR_MODELS[r], "CER", round(jiwer.cer(clips.reference.tolist(), clips[f"hyp_{r}"].tolist()), 3),
          "| WER", table.iloc[0 if r == "A" else 1].corpus_wer)
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why can the corpus WER and the mean of clip WERs differ, and which one do you report?
# 2. A clip of 4 words with 2 errors and a clip of 20 words with 2 errors: what does each add to each figure?
# 3. Which of B's "errors" would a caller never hear?
#
# <details><summary>Answers</summary>
#
# 1. The mean weights every clip equally; the corpus figure weights every word. Report the corpus figure, and say so.
# 2. 0.5 and 0.1 to the mean of clips (equal weight); 2 and 2 edits out of 24 words to the corpus figure.
# 3. Diacritics, hamza on alef, Arabic-Indic digits: spelling, not hearing. Lab 2.2 writes the rules.
# </details>
#
# **Carry forward.** The transcripts are in `data/clips.jsonl`; Labs 2.2 and 2.3 start from them.
