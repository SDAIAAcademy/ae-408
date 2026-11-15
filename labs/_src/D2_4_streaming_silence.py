# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 2.4 · Text on silence
#
# Day 2 · Session 4 (Streaming and silence) · 25 min.
#
# A booking call has long silences: the caller looks for a date, a child talks in the background, the line hums. A
# recogniser fed a silent stretch can still write text, and that text reaches the booking agent as if the caller had
# said it. You build an energy-based voice activity detector, stream only speech to the recogniser, catch the text it
# writes on silence, and count the difference.
#
# **Reference state.** `U.synthetic_call()`: 38 seconds of synthetic audio at 16 kHz with six utterances (their times
# are in `U.UTTERANCES`), quiet line noise and a hum. No voice is recorded or imitated. The recogniser is the course's
# streaming stand-in `U.recognise_segment(start_s, end_s)`.
#
# **Tasks**
# - [ ] 1 · An energy detector over 20 ms frames (8')
# - [ ] 2 · Stream speech segments and time the partial results (6')
# - [ ] 3 · Catch text produced on silent segments (7')
# - [ ] 4 · Count before and after the gate (4')
# - [ ] ✱ Stretch · Tune the hangover and see what it does to cut-off words

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

import numpy as np
import pandas as pd

import trails as U

x, sr = U.synthetic_call()
FRAME = int(0.02 * sr)
print(f"{len(x) / sr:.1f} s at {sr} Hz; utterances:", [(s, e) for s, e, _ in U.UTTERANCES], "| hum:", U.HUM)

# %% [markdown]
# ## The naive pipeline, for comparison
#
# Cut the call into fixed 2.5-second windows and send every window. This is what a first prototype does.

# %%
naive = []
for s in np.arange(0, len(x) / sr, 2.5):
    r = U.recognise_segment(float(s), float(min(s + 2.5, len(x) / sr)))
    naive.append({"start": float(s), "end": float(s) + 2.5, **r})
naive = pd.DataFrame(naive)
print(naive[["start", "end", "text", "no_speech_prob"]].to_string(index=False))

# %% [markdown]
# ## 1 · An energy detector (8')
#
# ✏️ **Exercise** · `vad(x, sr)`:
# 1. cut `x` into 20 ms frames and compute each frame's energy in decibels, `20 * log10(rms + 1e-9)`;
# 2. estimate the noise floor as the 20th percentile of frame energies, and mark a frame as speech when it is more
#    than `margin_db` above the floor;
# 3. keep a frame as speech for `hangover_ms` after the last speech frame (syllables have short dips);
# 4. merge runs of speech frames into segments `(start_s, end_s)` and drop segments shorter than 150 ms.

# %%
def vad(x, sr, margin_db=18.0, hangover_ms=200):
    # BEGIN SOLUTION
    n = len(x) // FRAME
    frames = x[: n * FRAME].reshape(n, FRAME)
    db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    floor = np.percentile(db, 20)
    active = db > floor + margin_db
    hang = int(hangover_ms / 20)
    keep, left = np.zeros(n, bool), 0
    for i, a in enumerate(active):
        left = hang if a else max(0, left - 1)
        keep[i] = a or left > 0
    segs, start = [], None
    for i, k in enumerate(np.append(keep, False)):
        if k and start is None:
            start = i
        elif not k and start is not None:
            if (i - start) * 0.02 >= 0.15:
                segs.append((round(start * 0.02, 2), round(i * 0.02, 2)))
            start = None
    return segs
    # END SOLUTION


# %%
def _vad_ref(x, sr, margin_db=18.0, hangover_ms=200):
    n = len(x) // FRAME
    db = 20 * np.log10(np.sqrt((x[: n * FRAME].reshape(n, FRAME) ** 2).mean(axis=1)) + 1e-9)
    act = db > np.percentile(db, 20) + margin_db
    keep, left = np.zeros(n, bool), 0
    for i, a in enumerate(act):
        left = int(hangover_ms / 20) if a else max(0, left - 1)
        keep[i] = a or left > 0
    segs, st = [], None
    for i, k in enumerate(np.append(keep, False)):
        if k and st is None:
            st = i
        elif not k and st is not None:
            if (i - st) * 0.02 >= 0.15:
                segs.append((round(st * 0.02, 2), round(i * 0.02, 2)))
            st = None
    return segs


try:
    segments = vad(x, sr)
except NotImplementedError:
    vad = _vad_ref
    segments = vad(x, sr)
print(len(segments), "segments:", segments)
on_hum = [s for s in segments if s[1] > U.HUM[0] and s[0] < U.HUM[1]]
U.check(len(segments) == len(U.UTTERANCES) and not on_hum, "one segment per utterance and none on the hum")

# %% [markdown]
# ## 2 · Stream the segments (6')
#
# In a streaming pipeline the recogniser gets each segment as soon as the detector closes it, so the time a caller
# waits for text is the detector's closing delay (the hangover) plus the recogniser's latency.
#
# ✏️ **Exercise** · For each segment call `U.recognise_segment(start, end)` and keep one row with `start`, `end`,
# `text`, `no_speech_prob` and `text_after_ms`: the time from the end of the speech to the text arriving.

# %%
def stream(segments, hangover_ms=200):
    rows = []
    # BEGIN SOLUTION
    for s, e in segments:
        r = U.recognise_segment(s, e)
        rows.append({"start": s, "end": e, "text": r["text"], "no_speech_prob": r["no_speech_prob"],
                     "text_after_ms": round(hangover_ms + r["latency_ms"])})
    # END SOLUTION
    return pd.DataFrame(rows)


# %%
try:
    streamed = stream(segments)
except NotImplementedError:
    streamed = pd.DataFrame([{"start": s, "end": e, **U.recognise_segment(s, e)} for s, e in segments])
    streamed["text_after_ms"] = 200 + streamed.latency_ms
print(streamed.to_string(index=False))
print("median time from end of speech to text:", streamed.text_after_ms.median(), "ms")

# %% [markdown]
# ## 3 · Catch text on silence (7')
#
# Text on silence has two signatures: the detector found no speech there, and the recogniser itself reports a high
# probability of no speech. Neither is enough alone: on the hum the recogniser's probability is only 0.42.
#
# ✏️ **Exercise** · `on_silence(row)` returns True when a row's text was produced on silence: the row's window
# overlaps no detected speech segment, **or** its `no_speech_prob` is above 0.6. Apply it to the naive windows and
# to an extra set of windows that cover only the gaps between your segments.

# %%
def overlaps_speech(start, end, segments):
    return any(min(end, e) - max(start, s) > 0.1 for s, e in segments)


def on_silence(row, segments):
    # BEGIN SOLUTION
    return bool(row["text"]) and (not overlaps_speech(row["start"], row["end"], segments) or row["no_speech_prob"] > 0.6)
    # END SOLUTION


# %%
try:
    on_silence({"text": "", "start": 0, "end": 1, "no_speech_prob": 0.9}, segments)
except NotImplementedError:
    on_silence = lambda row, seg: bool(row["text"]) and (not overlaps_speech(row["start"], row["end"], seg) or row["no_speech_prob"] > 0.6)
edges = [0.0] + [t for s in segments for t in s] + [len(x) / sr]
gaps = pd.DataFrame([{"start": a, "end": b, **U.recognise_segment(a, b)} for a, b in zip(edges[::2], edges[1::2]) if b - a > 0.5])
gaps["on_silence"] = [on_silence(r, segments) for _, r in gaps.iterrows()]
naive["on_silence"] = [on_silence(r, segments) for _, r in naive.iterrows()]
print("gaps sent to the recogniser:\n", gaps[["start", "end", "text", "no_speech_prob", "on_silence"]].to_string(index=False))
U.check(gaps[gaps.text != ""].on_silence.all(), "every text written in a gap is caught")

# %% [markdown]
# ## 4 · Before and after the gate (4')
#
# ✏️ **Exercise** · Count, for the naive windows and for the gated pipeline (VAD segments only, then the
# `no_speech_prob` check), how many texts reach the agent that were produced on silence, and how many utterance words
# were lost. Write one line for the failure log: mode, cause, mitigation, result.

# %%
def words_of(df):
    return sum(len(t.split()) for t in df.text)


# BEGIN SOLUTION
gated = streamed[streamed.no_speech_prob <= 0.6]
naive_bad = int(naive.on_silence.sum())
gated_bad = int(sum(on_silence(r, segments) for _, r in gated.iterrows()))
ref_words = sum(len(t.split()) for _, _, t in U.UTTERANCES)
print(f"texts on silence reaching the agent: naive {naive_bad}, gated {gated_bad}")
REF_TEXT = " ".join(t for _, _, t in U.UTTERANCES)
print(f"WER of everything the agent receives: naive {U.wer([REF_TEXT], [" ".join(naive.text)]):.3f}, "
      f"gated {U.wer([REF_TEXT], [" ".join(gated.text)]):.3f}")
log = {"mode": "text produced on silence", "cause": "fixed windows send silence and hum to the recogniser",
       "mitigation": "energy VAD with 200 ms hangover; drop text with no_speech_prob > 0.6",
       "result": f"{naive_bad} -> {gated_bad} texts on silence"}
print(log)
# END SOLUTION

# %% [markdown]
# 🔍 **Look at** the naive window that covered the hum: the recogniser was only 42% sure there was no speech. A
# threshold on its probability alone would have let that text through; the detector did not.

# %% [markdown]
# ## ✱ Stretch · The hangover
#
# Run the detector with hangover 0, 100, 200 and 400 ms. Count segments and the WER of the text the agent receives.
# Why does 0 ms break the utterances, and what does 400 ms cost the caller?

# %%
# BEGIN SOLUTION
for h in (0, 100, 200, 400):
    seg = vad(x, sr, hangover_ms=h)
    got = stream(seg, h)
    wer = U.wer([" ".join(t for _, _, t in U.UTTERANCES)], [" ".join(got.text)])
    print(f"hangover {h:3d} ms: {len(seg):2d} segments, WER {wer:.3f}, median text after {got.text_after_ms.median():.0f} ms")
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why does a recogniser write text on a silent stretch at all?
# 2. Why was the probability check not enough on the hum?
# 3. What does the hangover trade?
#
# <details><summary>Answers</summary>
#
# 1. It is trained to turn audio into text and has no reliable way to say "nothing"; whole invented phrases have been
#    reported around long non-vocal stretches (Koenecke et al., 2024). The pipeline has to supply the "nothing".
# 2. The hum is not silence to the recogniser: it reported 0.42, below any sensible threshold.
# 3. Words cut at syllable dips (too short) against a later end of turn (too long).
# </details>
#
# **Carry forward.** The detector is the first stage of the voice agent of Day 3; its hangover is Lab 3.3's subject.
