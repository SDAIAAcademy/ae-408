---
course: "Multimodal and Speech Systems Engineering"
code: "AE-408"
version: "2027.1.0"
deck: "day2"
day: 2
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ae-408/slides/day2.html"
---

# Multimodal and Speech Systems Engineering

## Day 2: Listening

Speech recognition measured by dialect, channel and code-switching, with explicit normalisation

#### [day2#title] Listening

*SDAIA Academy · Multimodal and Speech Systems Engineering*

Day 2: Speech recognition measured by dialect, channel and code-switching, with explicit normalisation

AI Engineering Track · 4 teaching days + capstone day · 4 sessions · 4 labs · AE-408

#### [day2#agenda] Listening

*Today*

- **Session 1 · From waveform to text**: How recognisers turn audio into words, and how word error rate counts their mistakes
- **Session 2 · Normalisation decides the error rate**: Arabic normalisation rules, written down, change the numbers and the ranking
- **Session 3 · Dialects and code-switching**: Error rates by slice with intervals, so weaker service for some speakers is visible
- **Session 4 · Streaming and silence**: Streaming recognition with voice activity detection, and the text a recogniser writes on silence

#### [day2#review-day1] Which failure is this?

*Review of Day 1*

**Question:** On a photo of an empty trail, Lamha returns a box labelled litter with high confidence. The reference has no litter. What do you log?

- A. A localisation error: the box missed the litter
- B. A resolution problem: the photo was sent too small
- C. A prompt injection through the image
- D. An invented object, to be measured with probes on clean scenes

### Session 1: From waveform to text

#### [day2#s1] From waveform to text

*Session 1*

- Describe the path from waveform to features to text in two recogniser families
- Compute word error rate from an alignment of substitutions, deletions and insertions
- Explain why corpus error rate differs from the mean of clip error rates

#### [day2#waveform-to-text] A recogniser turns a waveform into features, then features into text

*What a recogniser does*

1. **1 · Sample** 16,000 values a second; a telephone line keeps 8,000
2. **2 · Features** a log-mel spectrogram: energy by pitch band, every 10 ms
3. **3 · Encoder** turns the frames into vectors
4. **4 · Text** a decoder writes tokens, or a classifier labels each frame

> **Telephone audio** loses the upper half of the band. Sounds that differ there are the first to be confused.

#### [day2#recogniser-families] Encoder-decoder recognisers write text; encoder-only recognisers label frames

*Two families you will meet*

|  | Encoder-decoder (Whisper family) | Encoder with a frame classifier (wav2vec family) |
| --- | --- | --- |
| **Output** | tokens, written like a language model | a letter or a blank for every frame |
| **Strength** | punctuation, numbers, many languages in one model | fast, streams naturally, cannot invent long phrases |
| **Typical failure** | fluent text that was never said, especially on silence | misspelled words, no punctuation |
| **In the labs** | whisper-large-v3 and whisper-large-v3-turbo, hosted | named for the capstone |

#### [day2#word-error-rate] Word error rate counts the cheapest set of edits from reference to transcript

*Counting mistakes*

- reference: أبي ألغي الحجز رقم 1288 على قلعة النخيل
- recogniser A: اب الغي الحجز رقم 1284 على قلعه النخيل

Prompt for Definition:

```text
WER = (S + D + I) / N, from the alignment with the fewest edits
```

Here four substitutions over eight words: 0.5. Only one of them, the booking number, changes the booking.

#### [day2#corpus-or-mean] Report the corpus rate: every word counts once

*Two ways to add up*

- **Corpus WER.** All edits over all reference words. A long clip weighs more, because it has more words to get wrong.
- **Mean of clip WERs.** Each clip weighs the same. Two errors in a four-word clip add 0.5; in a twenty-word clip, 0.1.

In Lab 2.1 the two agree to the third decimal (0.213 and 0.214 for A), because the clips have similar lengths. On real calls they do not: say which one you report.

#### [day2#raw-ranking] On raw text, recogniser A looks more than twice as good as B

*Lab 2.1, 50 clips, raw text*

| Recogniser | WER | S | D | I | CER |
| --- | --- | --- | --- | --- | --- |
| whisper-large-v3 (A) | 0.213 | 82 | 10 | 9 | 0.076 |
| whisper-large-v3-turbo (B) | 0.517 | 235 | 8 | 2 | 0.159 |

> **Almost all of B's errors are substitutions.** Before trusting this ranking, read what the substitutions are.

#### [day2#checkpoint-1] How does this count?

*Checkpoint*

**Question:** Reference: "five people on Thursday" (4 words). Transcript: "five people Thursday please". What is the WER?

- A. 0.25: one word is missing
- B. 0.5: one deletion and one insertion over four words
- C. 0.4: two edits over five words
- D. 0.75: three words are out of place

#### [day2#lab-2-1] Two recognisers, 50 clips

Lab 2.1 · 25 min

Run two open-weight recognisers on 50 clips (or replay their recorded transcripts) and compute word error rates with your own alignment and with jiwer.

[D2_1_two_recognisers.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D2_1_two_recognisers.ipynb)

- [ ] Load the clips and their references (4 min)
- [ ] Transcribe with two recognisers, or replay (6 min)
- [ ] Word error rate from your own alignment, checked with jiwer (8 min)
- [ ] Corpus against mean error rate, and the worst clips (7 min)
- [ ] ✱ Stretch: Character error rate beside word error rate for the same clips

### Session 2: Normalisation decides the error rate

#### [day2#s2] Normalisation decides the error rate

*Session 2*

- Write explicit Arabic normalisation rules for diacritics, letter variants and numerals
- Recompute error rates under each rule set and explain the change
- Spot a rule that hides a real recognition error

#### [day2#one-word-many-spellings] The same spoken word has several correct spellings

*Why Arabic needs rules first*

| Variation | Written | Also written | Heard the same? |
| --- | --- | --- | --- |
| Diacritics | ابي | ابَي | yes |
| Hamza on alef | أبي | ابي | yes |
| Ta marbuta | جولة | جوله | yes |
| Alef maqsura | على | علي | usually, not always |
| Digits | 1288 | ١٢٨٨ | yes |
| Tatweel | للاطفال | للـاطفال | yes |

#### [day2#rules-as-code] Write each rule as a function, test it, and name the set you report

*Rules you can cite*

```python
# file: Lab 2.2
def diacritics(t):
    return re.sub("[ً-ْٰ]", "", t)

def alef(t):
    return re.sub("[أإآٱ]", "ا", t)

SETS = {
  "none":  [],
  "light": ["diacritics", "tatweel", "digits", "punct"],
  "full":  [*light, "alef", "maqsura", "ta"]}
```

- **Light.** Removes what is never a different word: marks, stretching, digit forms, punctuation.
- **Full.** Also merges letter variants. Fairer to spelling, but it can merge two real words.

#### [day2#ranking-flips] Under the full rules the ranking flips

*Lab 2.2, 50 clips*

| Rule set | whisper-large-v3 (A) | whisper-large-v3-turbo (B) | Better |
| --- | --- | --- | --- |
| none | 0.213 | 0.517 | A |
| light | 0.213 | 0.264 | A |
| full | 0.160 | 0.089 | B |

> **A WER without its rules is not a result.** The same transcripts support either choice.

#### [day2#which-rule-moved] Diacritics alone took a third off B's error rate

*Recogniser B, one rule at a time*

| Item | Value |
| --- | --- |
| + diacritics | −0.186 |
| + alef | −0.083 |
| + maqsura | −0.059 |
| + tatweel | −0.042 |
| + ta | −0.033 |
| + digits | −0.025 |

From 0.517 with no rules to 0.089 with all seven. Punctuation changed nothing: the transcripts had none.

#### [day2#rules-can-hide-errors] A rule that forgives spelling can also forgive a wrong word

*The cost of the full rules*

- **Merged by the full rules.** على and علي; أبغى and أبغي; جولة and جوله.
- **What to do.** Report the full-rule WER, and a second score on the slots that drive a booking (names, numbers, dates) without the letter rules.

#### [day2#checkpoint-2] Which number goes in the report?

*Checkpoint*

**Question:** A vendor quotes a word error rate of 0.09 for Arabic. Your raw measurement of the same model on your clips is 0.52. What do you ask first?

- A. Which model version they used
- B. Whether they used more clips than you
- C. Which normalisation rules they applied before counting
- D. Whether they measured characters instead of words

#### [day2#lab-2-2] Rules before rates

Lab 2.2 · 25 min

Apply three sets of Arabic normalisation rules to supplied transcripts, recompute the error rates and see the ranking of the two recognisers change. AI off.

[D2_2_normalisation.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D2_2_normalisation.ipynb)

- [ ] Write the rules: diacritics, alef, ta marbuta, alef maqsura, tatweel, digits (10 min)
- [ ] Recompute error rates under three rule sets (7 min)
- [ ] Which rule moved the rate, and the ranking (5 min)
- [ ] Save the rules file the report will cite (3 min)
- [ ] ✱ Stretch: Find a pair of words the rules merge that mean different things

### Session 3: Dialects and code-switching

#### [day2#s3] Dialects and code-switching

*Session 3*

- Slice error rates by dialect, channel and code-switching
- Add clip-level bootstrap intervals to each slice
- Decide which slice differences are real given their size

#### [day2#one-rate-hides-callers] One error rate for the whole line hides the callers it fails

*Who gets worse service*

- **Dialect.** Najdi, Hijazi, Gulf, Southern, Modern Standard Arabic, and Egyptian visitors.
- **Channel.** Wideband app audio against an 8 kHz telephone line.
- **Code-switching.** Arabic with English words: booking, guide, family ticket, confirm.

> **The responsible-use rule of this course:** error rates are reported by dialect, so weaker service for some speakers is visible before launch.

#### [day2#resample-clips] Resample clips, not words: words of one clip share a speaker and a line

*Intervals that are honest about dependence*

```python
# file: Lab 2.3
rng = np.random.default_rng(408)
idx = rng.integers(0, n, size=(reps, n))
rates = edits[idx].sum(1) / words[idx].sum(1)
lo, hi = np.percentile(rates, [2.5, 97.5])
```

- **Each draw.** n clips with replacement; the slice's corpus rate on that draw.
- **Word resampling.** Treats 474 words as independent: an interval far too narrow.

#### [day2#southern-is-worse] Southern speakers are shown worse; the rest cannot be told apart yet

*Lab 2.3, recogniser B, full rules*

| Slice | n | WER | 95% interval | Verdict |
| --- | --- | --- | --- | --- |
| Southern | 8 | 0.219 | 0.145 to 0.309 | worse |
| Telephone | 22 | 0.133 | 0.085 to 0.186 | not shown worse |
| Code-switched | 14 | 0.128 | 0.058 to 0.211 | not shown worse |
| Hijazi | 10 | 0.095 | 0.034 to 0.162 | not shown worse |
| Egyptian | 6 | 0.054 | 0 to 0.135 | not shown worse |

Overall 0.089. A slice is "worse" when its whole interval lies above the overall rate.

#### [day2#minimum-size] Below a minimum size, a slice says only that you need more clips

*When to say nothing*

- Set the minimum before you look: here six clips.
- Crossing dialect with channel leaves 3 of 12 cells with six or more clips.
- Southern on the telephone: six clips, 0.232. The cell is small but points the same way as both of its margins.
- Ask for clips where the cells are empty; Day 4's test set is built for that.

**3 / 12** dialect by channel cells with at least six clips, Lab 2.3 stretch

#### [day2#code-switched-words] Code-switched words fail in a way the rules cannot fix

*English inside Arabic*

- caller said: أبي أسوي booking في قلعة النخيل
- transcript: أبي أسوي بوكنق في قلعة النخيل

- **Transliterated.** The English word comes back in Arabic letters. No Arabic rule maps it back.
- **Options.** A mapping list for the service's own English words, the language hint left unset, or both scored.

#### [day2#checkpoint-3] What do you write about this slice?

*Checkpoint*

**Question:** Telephone callers: WER 0.133, 95% interval 0.085 to 0.186, 22 clips. Overall WER 0.089. What does the report say?

- A. Telephone callers get worse service
- B. Telephone callers get the same service as others
- C. Nothing: the slice is too small to report
- D. Higher, but not shown worse: the interval reaches the overall rate; more telephone clips are needed

#### [day2#lab-2-3] Slices with intervals

Lab 2.3 · 25 min

Slice error rates by dialect, channel and code-switched speech, add bootstrap intervals and flag the slices that are worse than the whole set.

[D2_3_dialect_slices.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D2_3_dialect_slices.ipynb)

- [ ] Error rate per dialect, channel and code-switching (7 min)
- [ ] A clip-level bootstrap interval per slice (10 min)
- [ ] Flag the slices that are worse, with a minimum size (5 min)
- [ ] The report table (3 min)
- [ ] ✱ Stretch: Cross dialect with channel and read what the small cells can say

### Session 4: Streaming and silence

#### [day2#s4] Streaming and silence

*Session 4*

- Detect speech frames with an energy-based voice activity detector
- Stream segments to a recogniser and measure when text arrives
- Catch and suppress text produced on silent segments

#### [day2#streaming-pipeline] A live line sends audio in frames and must decide where speech starts and ends

*A call is not a file*

1. **1 · Frames** 20 ms of audio at a time
2. **2 · Detect** is this frame speech?
3. **3 · Segment** close a segment after a short hangover
4. **4 · Recognise** send the segment; text arrives

- **Voice activity detection.** Energy above a noise floor in the labs; a small neural detector (Silero VAD) in production.
- **Diarisation.** Who spoke when (pyannote.audio), for a call with two people on the caller's side.

#### [day2#energy-detector] Speech is energy well above the line's own noise

*The detector of Lab 2.4*

```python
# file: Lab 2.4
db = 20 * np.log10(rms(frames) + 1e-9)
floor = np.percentile(db, 20)
active = db > floor + 18     # decibels
# keep 200 ms after the last active frame
# merge runs; drop runs under 150 ms
```

| On the synthetic call | dB |
| --- | --- |
| Line noise (the floor) | −50 |
| Hum | −40 |
| Threshold | −32 |
| Speech peaks | −13 |

#### [day2#text-on-silence] Fed a silent stretch, a recogniser can write text nobody said

*The failure the detector prevents*

- 7.5 to 10.0 s: silence
- transcript: اشتركوا في القناة (no-speech 0.68)
- 20.0 to 22.5 s: a hum on the line
- transcript: Thank you. (no-speech 0.42)

- **Reported for Whisper.** About 1% of transcriptions held whole invented phrases, more often for speakers with long pauses.
- **Why it matters here.** Invented text reaches the booking agent as if the caller had said it.

#### [day2#two-signals-not-one] Gate on the detector and on the recogniser's no-speech probability

*Lab 2.4 result*

- **6 → 0** texts on silence reaching the agent, fixed windows against the gated stream
- **0.714 → 0** WER of everything the agent received
- **0.42** no-speech probability on the hum: a threshold alone lets it through

> **Failure log entry.** Mode: text on silence. Cause: silence and hum sent to the recogniser. Mitigation: detector plus probability gate. Result: 6 to 0 on the synthetic call.

#### [day2#hangover-trade] The hangover trades broken words against a later reply

*The detector's one design choice*

| Hangover | Segments | WER of the stream | Text arrives after speech ends |
| --- | --- | --- | --- |
| 0 ms | 48 | 2.76 | 172 ms |
| 100 ms | 6 | 0 | 358 ms |
| 200 ms | 6 | 0 | 462 ms |
| 400 ms | 6 | 0 | 672 ms |

Without a hangover, every dip between syllables closes a segment, and every fragment invites invented text.

#### [day2#checkpoint-4] Where do you stop text on silence?

*Checkpoint*

**Question:** Your gate drops text when the recogniser's no-speech probability is above 0.6. A hum on the line still produces "Thank you." with probability 0.42. What do you add?

- A. Lower the probability threshold to 0.4
- B. A voice activity detector, so that only detected speech is sent at all
- C. A larger recogniser
- D. A filter that deletes the phrase "Thank you."

#### [day2#lab-2-4] Text on silence

Lab 2.4 · 25 min

Stream a synthetic call through voice activity detection to a recogniser and catch the text it produces on silent segments.

[D2_4_streaming_silence.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D2_4_streaming_silence.ipynb)

- [ ] An energy detector over 20 ms frames (8 min)
- [ ] Stream speech segments and time the partial results (6 min)
- [ ] Catch text produced on silent segments (7 min)
- [ ] Count before and after the gate (4 min)
- [ ] ✱ Stretch: Tune the hangover and see what it does to cut-off words

#### [day2#wrap-up] What to carry into the capstone

*Day 2 · Three things to keep*

- **Rules before rates.** Write the normalisation as code, report the set, and score names and numbers separately.
- **Slices with intervals.** Resample clips, set a minimum size first, and write "not shown worse", never "the same".
- **Silence is an input.** Detect speech before recognising it, and gate on a second signal.

#### [day2#next] Speaking: read-back, latency, turn-taking and tool calls

*Tomorrow · Day 3*

- The budget is 1,200 ms from the end of the caller's speech to the first audio of the reply.
- Think of one number, one date and one name a caller must hear right.
- With a free Groq key, Lab 3.1 can synthesise the read-backs in a Saudi Arabic voice.
