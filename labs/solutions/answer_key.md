# Answer key: key results of the solution runs

The figures below are what the solution notebooks print on the full data without any key (the scripted stand-in).
With hosted models the Day 1 figures, and the Day 2 figures of Lab 2.1 when audio was generated, will differ; the
method and the shape of the result are what to check. In quick mode (`HT_QUICK=1`) the figures differ too.

## Day 1 · Seeing

| Lab | Key result |
|---|---|
| 1.1 Resolution and tokens | Marker codes read: 20% at 320 px (118 tokens, 418 ms), 95% at 640 px (338 tokens, 533 ms), 100% at 1280 px (1,238 tokens, 1,026 ms). 640 px is the cheapest width that reaches 90%. |
| 1.2 Incident fields | Field accuracy 0.98 for the hosted model, 0.89 for the open-weight one; every reply valid after at most one repair. |
| 1.3 Grounding | Box precision and recall 0.900 / 0.850 (open) and 0.962 / 0.939 (hosted). Invented litter: 13.5% of photos without litter for the open model (33% on clean scenes), 5.8% for the hosted one. |
| 1.4 Signage and injection | Mean CER 0.122; by text height 14 px 0.281, 18 px 0.144, 22 px 0.064, 28 px 0. The injected instructions on P059 and P060 are flagged by the check on the record; no ordinary sign is flagged. |

## Day 2 · Listening

| Lab | Key result |
|---|---|
| 2.1 Two recognisers | Raw WER: A 0.213, B 0.517 (CER 0.076 and 0.159). Almost all of B's errors are substitutions. |
| 2.2 Normalisation | Full rules: A 0.160, B 0.089: the ranking flips. Diacritics alone take 0.186 off B. |
| 2.3 Dialect slices | Overall 0.089 [0.060, 0.120]; southern 0.219 [0.145, 0.309], shown worse; telephone 0.133 [0.085, 0.186], not shown worse. |
| 2.4 Streaming and silence | Texts on silence reaching the agent: 6 with fixed windows, 0 with the detector and the no-speech gate; WER of what the agent received 0.714 to 0. |

## Day 3 · Speaking

| Lab | Key result |
|---|---|
| 3.1 Read-back | Every confirmation under 12 s (9.9 to 11.0 s, estimated). Listening test, raw to read-back: dates 16/32 to 31/32, numbers 16/32 to 32/32 (both shown better), names 29/32 to 31/32 (not shown). |
| 3.2 Latency trace | Cascade p50 1,552 ms, p90 2,628 ms, 5 of 20 turns within 1,200 ms. Speech-to-speech p50 562, p90 1,248, 85% within. Streaming the first sentence: p50 1,228, p90 2,362, 9 of 20 within. |
| 3.3 End of turn | Silence alone: best 500 ms with 24 of 48 turns right (24 cut-ins). With the hold rule: 32 of 48 at 500 ms (16 cut-ins). Barge-in: stop after 260 ms. |
| 3.4 Booking tool | Book when full: 4 of 6 calls right, 2 wrong bookings (K2, K5). Confirm then book: 6 of 6, none wrong. Booking turn 2,135 ms in silence, 1,235 ms with a filler line. |

## Day 4 · Evaluating and choosing

| Lab | Key result |
|---|---|
| 4.1 Test set | A random 60 misses 5 of 19 targets (4 southern, 2 Egyptian, 3 seeded failures). The greedy selection meets all 19. Gaps in the pool: southern booking and cancelling (1 each), Egyptian booking, changing and enquiries (2 each), Egyptian cancelling (1). |
| 4.2 Simulated callers | Release candidate 14 of 20 [0.48, 0.85]; all six failures are wrong dates after a correction or a change of mind (SC04, SC06, SC07, SC10, SC15, SC16). Transcript WER 0.022 (southern 0.053). After the fix: 20 of 20. |
| 4.3 Decision record | Cost per call 0.87 SAR (cascaded) and 3.04 SAR (hosted) at 18,000 calls; break-even 4,872 calls a month. Task success 51/60 [0.74, 0.92] against 54/60 [0.80, 0.95]: not shown to differ. Fingerprint `a0c892e8bf47525f`. |
| 4.4 Consent note | 24 of 60 photos show faces (29 faces), all blurred with no change outside the boxes. Ten transcript lines redacted, HTB-4821 kept. Disclosure 4.5 s (Arabic) and 4.9 s (English), estimated. |

## Checkpoint answers in the decks

Every deck checkpoint carries its answer and the reason for each wrong option in the speaker notes and in the
"Why" callout shown after answering.
