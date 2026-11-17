---
course: "Multimodal and Speech Systems Engineering"
code: "AE-408"
version: "2027.1.0"
deck: "day4"
day: 4
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ae-408/slides/day4.html"
---

# Multimodal and Speech Systems Engineering

## Day 4: Evaluating and choosing

Test sets, simulated callers, the decision record and the data-handling note

#### [day4#title] Evaluating and choosing

*SDAIA Academy · Multimodal and Speech Systems Engineering*

Day 4: Test sets, simulated callers, the decision record and the data-handling note

AI Engineering Track · 4 teaching days + capstone day · 4 sessions · 4 labs · AE-408

#### [day4#agenda] Evaluating and choosing

*Today*

- **Session 1 · Multimodal test sets**: A test set designed for coverage across modality, dialect and task, with its gaps stated
- **Session 2 · Simulated callers**: Simulated callers with goals and behaviours, graded on outcome and on transcript
- **Session 3 · Choosing by quality, latency and cost**: Open-weight or hosted, cascaded or speech-to-speech, decided on measured figures
- **Session 4 · Voice, faces and consent**: Recordings and photos as personal data, and the disclosure callers hear

#### [day4#review-day3] What did the booking turn cost?

*Review of Day 3*

**Question:** An ordinary turn reaches the caller in about 1,220 ms; the booking tool takes 900 ms. Rahhal says "one moment, I am booking that" at the normal time. When does the first audio of the booking turn arrive?

- A. At about the time of an ordinary turn; the result follows when the tool returns
- B. At about 2,100 ms, after the tool returns
- C. At about 320 ms, because the filler replaces the pipeline
- D. Only after the booking reference is known

### Session 1: Multimodal test sets

#### [day4#s1] Multimodal test sets

*Session 1*

- Define coverage targets across modality, dialect and task
- Select a stratified test set from a pool of candidates
- Report the coverage table and the gaps it leaves

#### [day4#random-set] A random test set copies the pool, including what the pool lacks

*Lab 4.1, a random 60 from the pool of 240*

- **4** southern callers in the random 60
- **2** Egyptian callers
- **3 / 17** seeded failures from the failure log

> **What goes wrong.** Day 2 showed southern callers worse served; a test set with four of them cannot tell whether a fix helped.

#### [day4#targets-first] Coverage targets state what the sign-off must be able to answer

*Write them before selecting*

| Column | Target in the 60 | Why |
| --- | --- | --- |
| Modality | exactly 40 audio, 20 image | both services signed off together |
| Dialect | at least 5 of each of six | the error-rate report by dialect |
| Channel | at least 15 telephone | Rahhal is a phone line |
| Code-switched | at least 6 | English words in Arabic calls |
| Seeded failures | at least 10 | every mode of the failure log tested |
| Task | 6 per audio task, 4 per image task | every task the services perform |

#### [day4#greedy-selection] Select the item that meets the most unmet targets, then fill at random

*Lab 4.1, step 3*

1. **1 · Score** count the unmet targets each item would meet
2. **2 · Take the best** within the modality quota
3. **3 · Repeat** until every target is met
4. **4 · Fill** the rest at random, with a seed

> **Result.** 60 distinct items, every one of the 19 targets met. The random 60 missed five.

#### [day4#coverage-table] The coverage table goes in the report beside every result

*Lab 4.1, the 40 audio items*

| Dialect | Telephone | Wideband | All |
| --- | --- | --- | --- |
| Najdi | 6 | 3 | 9 |
| Gulf | 5 | 2 | 7 |
| MSA | 5 | 2 | 7 |
| Hijazi | 4 | 2 | 6 |
| Egyptian | 3 | 3 | 6 |
| Southern | 2 | 3 | 5 |

#### [day4#gaps] Six dialect and task cells have fewer than three items in the whole pool

*What no selection can fix*

| Dialect | Task | Items in pool |
| --- | --- | --- |
| Southern | book a visit | 1 |
| Southern | cancel | 1 |
| Egyptian | cancel | 1 |
| Egyptian | book a visit | 2 |
| Egyptian | change | 2 |
| Egyptian | enquiry | 2 |

- **A gap is a data request.** Name it in the report and ask for recordings. Never fill a cell by copying items from a neighbouring one.

#### [day4#hold-out] Keep ten items that nobody tunes on

*Lab 4.1 stretch*

- Every threshold and rule of Day 3 was tuned on data you looked at; the hold-out is the check that it was not tuned to those items alone.
- Stratify it too: a plain random 10 from the 60 held **no seeded failure**; one per modality on purpose gives two.
- Look at the hold-out **once**, at the end, and report the result whatever it is.

#### [day4#checkpoint-1] What do you do with this cell?

*Checkpoint*

**Question:** Your 60-item test set must report task success for southern callers booking a visit. The whole pool holds one such recording. What goes in the report?

- A. Task success for that group: 1/1, 100%
- B. Five Najdi booking calls relabelled as southern
- C. The cell as a named gap, with a request for recordings, and no rate for it
- D. Nothing: leave southern booking calls out of the coverage table

#### [day4#lab-4-1] Sixty items with coverage

Lab 4.1 · 25 min

Build a 60-item test set across image, audio and dialects from a pool of candidates, with a coverage table and its gaps.

[D4_1_test_set.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D4_1_test_set.ipynb)

- [ ] Read the pool of 240 candidates (4 min)
- [ ] Write the coverage targets (6 min)
- [ ] Select 60 items stratified by the targets (8 min)
- [ ] The coverage table and its gaps (7 min)
- [ ] ✱ Stretch: Hold out ten items that nobody tunes on

### Session 2: Simulated callers

#### [day4#s2] Simulated callers

*Session 2*

- Write simulated callers with a goal, a dialect and a behaviour
- Grade a call on its outcome in the booking store
- Separate task failures from transcript errors

#### [day4#caller-card] A card gives a caller a goal, a dialect and a way of behaving

*A simulated caller*

```json
// file: data/callers.jsonl
{"caller_id": "SC04",
 "language": "en", "dialect": "southern",
 "behaviour": "cooperative",
 "goal": {"site_code": "HT-06",
          "date": "2026-12-20",
          "party_size": 6},
 "change_to": null}
```

- **Six behaviours.** cooperative, long pauses, mumbles, code-switches, interrupts, changes their mind.
- **Through the recogniser.** Every caller turn passes through a stand-in recogniser with errors by dialect: what Rahhal hears is not what the card says.

#### [day4#grade-the-store] Grade the booking in the store, not what Rahhal said

*What counts as success*

- **What Rahhal said.** "Booked. Your reference is HTB-1437." True that a booking exists; silent about which one.
- **What the store holds.** Exactly one booking for the caller, matching site, date and party of the final goal, after any change of mind.

> **Reasons, not just pass or fail:** no booking, duplicate, wrong site, wrong date, wrong party.

#### [day4#simulation-results] Fourteen of twenty callers got the booking they confirmed

*Lab 4.2, the release candidate*

**14 / 20** task success, 95% interval 0.48 to 0.85

| Behaviour | Calls | Failed |
| --- | --- | --- |
| changes their mind | 3 | 3 |
| cooperative | 7 | 2 |
| mumbles | 2 | 1 |
| code-switches | 3 | 0 |
| interrupts | 3 | 0 |
| long pauses | 2 | 0 |

#### [day4#transcript-or-task] The recogniser's errors were caught; the agent lost the correction

*Separate the recogniser from the agent*

- **0.022** transcript WER over all caller turns, said against heard
- **0.053** for southern callers, the highest

- heard: Clay Village on 2026-12-23 for 6 people
- Rahhal: To confirm: Clay Village, on 2026-12-23, for 6. Shall I book?
- heard: no, on 2026-12-20
- Rahhal: To confirm: Clay Village, on 2026-12-20, for 6. Shall I book?
- heard: yes book it
- store: HT-06, 2026-12-23, 6

#### [day4#after-the-fix] Twenty of twenty, and still only a lower bound of 0.84

*The same twenty callers, after the fix*

- The fix: book with the slots the caller **last confirmed**.
- Re-run the **same** cards: a change that fixes one caller can break another.
- 20/20 has a 95% interval of 0.84 to 1.00: twenty scripts cannot show the line is ready.
- Keep the cards as a **regression suite**: every future change runs them.
- The same run writes the **per-stage latency trace** of the twenty calls: p90 2,086 ms.

#### [day4#checkpoint-2] Whose error is it?

*Checkpoint*

**Question:** A caller says the 20th; the recogniser hears the 23rd; Rahhal reads back the 23rd; the caller says "no, the 20th"; Rahhal reads back the 20th; the caller says yes. The store holds the 23rd. What do you log?

- A. A recogniser error on southern dates
- B. A caller error: they said yes to the wrong date
- C. A tool error: the booking tool stored the wrong date
- D. An agent error: the tool was called with the first-heard date, not the confirmed one

#### [day4#lab-4-2] Twenty simulated calls

Lab 4.2 · 25 min

Run 20 simulated calls against a provided agent and grade task success from the booking store and transcript errors from the recogniser.

[D4_2_simulated_callers.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D4_2_simulated_callers.ipynb)

- [ ] Read the 20 caller cards (3 min)
- [ ] Run the calls against the agent (8 min)
- [ ] Grade task success from the booking store (7 min)
- [ ] Transcript errors, and failures by behaviour (7 min)
- [ ] ✱ Stretch: Let a hosted model play the caller from the same card

### Session 3: Choosing by quality, latency and cost

#### [day4#s3] Choosing by quality, latency and cost

*Session 3*

- Compute cost per call for a self-hosted and a hosted pipeline
- Compare pipelines on quality, latency and cost with their uncertainty
- Write a decision record that a reviewer re-runs to the same figures

#### [day4#two-pipelines] Two designs measured on the same calls

*Lab 4.3, 60 test calls each*

|  | Cascaded, open-weight | Hosted speech-to-speech |
| --- | --- | --- |
| How it is paid for | one rented node, 14,500 SAR a month, plus 0.02 SAR a minute | 0.95 SAR a minute |
| Task success | 51/60 | 54/60 |
| WER | 0.164 | no transcript |
| Time to first audio, p50 / p90 | 980 / 1,690 ms | 560 / 890 ms |

> **The prices are illustrative,** supplied by the case study. Use your own quotes in a real decision.

#### [day4#cost-per-call] At 18,000 calls a month the cascade costs under a third as much per call

*Lab 4.3, step 2*

- **0.87 SAR** cascaded, per call: 14,500 / 18,000 + 0.02 × 3.2
- **3.04 SAR** hosted, per call: 0.95 × 3.2
- **4,872** calls a month where the two cost the same

#### [day4#volume-curve] The cheaper design depends on the volume you plan for

*Lab 4.3 stretch, cost per call by volume*

| Item | Value |
| --- | --- |
| 3,000 calls | 4.90 against 3.04: hosted |
| 5,000 calls | 2.96 against 3.04: cascaded |
| 18,000 calls | 0.87 against 3.04: cascaded |
| 90,000 calls | 0.39 (two nodes) against 3.04 |

Bars show the cascaded cost per call; the hosted cost is 3.04 at every volume.

#### [day4#quality-not-shown] Task success is not shown to differ; latency is

*Lab 4.3, step 3*

| Pipeline | Task success | 95% interval | p90 (ms) | p90 within 1,200? |
| --- | --- | --- | --- | --- |
| Cascaded | 51/60 | 0.74 to 0.92 | 1,690 | no |
| Hosted | 54/60 | 0.80 to 0.95 | 890 | yes |

> **So the choice is latency against cost and control,** not quality against cost.

#### [day4#decision-record] A decision record says what was chosen, why, and what would change it

*One page*

- **The lab's example.** Cascaded for the pilot, on condition that its p90 is brought under 1,200 ms before launch: success not shown to differ, under a third of the cost, a transcript for dialect slices and argument checks, audio on a node the authority controls.
- **What would change it.** p90 still over budget after the Day 3 fixes; volume under about 4,900 calls a month; a larger test showing a difference in success.

#### [day4#fingerprint] A fingerprint lets a reviewer check the figures without trusting them

*Re-run to the same figures*

```python
# file: Lab 4.3
def fingerprint(raw, table):
    data = raw + table.to_csv()
    return sha256(data.encode()).hexdigest()[:16]

# Fingerprint: a0c892e8bf47525f
```

- The SHA-256 of the input file and the decision table.
- A reviewer re-runs the notebook: the same fingerprint, or a difference to explain.
- Line endings are normalised first, so Windows and Colab agree.

#### [day4#checkpoint-3] Which sentence belongs in the record?

*Checkpoint*

**Question:** Cascaded: 51/60 calls succeed, 0.87 SAR a call, p90 1,690 ms. Hosted: 54/60, 3.04 SAR a call, p90 890 ms. The intervals on success overlap. Which reason is sound?

- A. Hosted, because it succeeds on more calls
- B. Success is not shown to differ, so the choice rests on latency against cost
- C. Cascaded, because it is cheaper and nothing else differs
- D. Hosted, because per-minute pricing is always cheaper than a node

#### [day4#lab-4-3] The decision record

Lab 4.3 · 25 min

Compare open-weight and hosted pipelines on provided measurements, compute cost per call and draft a decision record that re-runs to the same figures.

[D4_3_decision_record.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D4_3_decision_record.ipynb)

- [ ] Load the measurements of two pipelines (4 min)
- [ ] Cost per call and the break-even volume (7 min)
- [ ] Quality, latency and cost in one table (6 min)
- [ ] The decision record and its fingerprint (8 min)
- [ ] ✱ Stretch: Change the call volume and see when the decision flips

### Session 4: Voice, faces and consent

#### [day4#s4] Voice, faces and consent

*Session 4*

- Classify recordings, transcripts and photos and set their retention
- Minimise what is stored: blur faces and redact transcripts
- Write the synthetic-voice disclosure and test when callers hear it

#### [day4#inventory] List what each service keeps, whether it identifies a person, and for how long

*Lab 4.4, step 1*

| Item | Personal? | Class | Keep (days) |
| --- | --- | --- | --- |
| Trail photo as uploaded | yes, faces: sensitive | confidential | 7 |
| Photo with faces blurred | no | restricted | 365 |
| Booking: name, phone, site, date, party | yes | confidential | 90 |
| Caller audio | yes, a voice: sensitive | confidential | 0 |
| Full transcript | yes | confidential | 30 |
| Redacted transcript | no | restricted | 365 |

#### [day4#blur-faces] Blur faces before storing, and test that the blur worked

*Lab 4.4, step 2*

- **24 / 60** photos show at least one face, 29 faces in all
- **100%** of faces with their pixel spread cut by more than half
- **0** pixels changed outside the face boxes

> **What goes wrong.** A blur that is never tested: a box drawn in the wrong coordinates leaves the face sharp and blurs a rock.

#### [day4#redaction] Redact identifiers, and keep what the service needs

*Lab 4.4, step 3*

- R01: my number is [PHONE] and I want to book Red Rock Path for four
- R04: رقم الهوية [ID] والحجز باسم الوالد
- R03: you can email me at [EMAIL] about the booking
- R06 · code kept: أبي ألغي الحجز رقم HTB-4821

Mobile numbers (05 and eight digits), ID numbers (ten digits starting 1 or 2) and email addresses. All ten sample lines clean.

#### [day4#disclosure] The first thing every caller hears says the voice is generated

*Lab 4.4, step 4*

**Arabic, 4.5 s (good example):** مسارات التراث. أنا رحّال، مساعد آلي بصوت مولّد.

**English, 4.9 s (good example):** This is Rahhal, an automated assistant with a generated voice.

> **The case study's rule:** first, in the caller's language, under 6 seconds, before any question about a name or a number.

#### [day4#checkpoint-4] Which control answers the officer?

*Checkpoint*

**Question:** Ghusoun asks how Lamha avoids keeping images of visitors who happen to be in a trail photo. Which answer is complete?

- A. Faces are blurred before storage, the blur is tested on every face box, and the original is deleted after seven days
- B. The terms of use tell visitors not to photograph people
- C. Only rangers can open the photos
- D. The model is told to ignore people when it extracts fields

#### [day4#lab-4-4] The data-handling note

Lab 4.4 · 25 min

Write the data-handling note for recordings and photos and the synthetic-voice disclosure callers hear, with tests for blurring, redaction and disclosure timing.

[D4_4_consent_note.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D4_4_consent_note.ipynb)

- [ ] Inventory and classification of what the service keeps (6 min)
- [ ] Blur faces in photos and check (7 min)
- [ ] Redact transcripts and set retention (6 min)
- [ ] The disclosure and when callers hear it (6 min)
- [ ] ✱ Stretch: A consent withdrawal that deletes a caller's personal records

#### [day4#wrap-up] What to carry into the capstone

*Day 4 · Three things to keep*

- **Coverage before scores.** Targets first, a coverage table beside every result, and gaps named as data requests.
- **Grade the outcome.** Simulated callers graded from the store, with transcript errors kept apart from task failures.
- **Decide on the record.** Cost per call at a stated volume, intervals on quality, a fingerprint, and a data-handling note.

#### [day4#next] Capstone: present the system you built and defend one failure

*Next · Capstone*

- A public repository: image pipeline, speech evaluation, voice agent, test set and simulation, traces and decision record.
- A README that reports the measured results and links the script that reproduces them.
- 10 minutes of presentation and 5 of questions, with a call and a photo the assessor supplies.
