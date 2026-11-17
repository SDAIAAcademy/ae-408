---
course: "Multimodal and Speech Systems Engineering"
code: "AE-408"
version: "2027.1.0"
deck: "day3"
day: 3
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ae-408/slides/day3.html"
---

# Multimodal and Speech Systems Engineering

## Day 3: Speaking

A bilingual voice booking line with read-back, turn-taking and tool calls in a latency budget

#### [day3#title] Speaking

*SDAIA Academy · Multimodal and Speech Systems Engineering*

Day 3: A bilingual voice booking line with read-back, turn-taking and tool calls in a latency budget

AI Engineering Track · 4 teaching days + capstone day · 4 sessions · 4 labs · AE-408

#### [day3#agenda] Speaking

*Today*

- **Session 1 · Synthesis and read-back**: Speaking names, numbers, dates and booking codes so that callers hear them right
- **Session 2 · Cascaded versus speech-to-speech**: Where the time to first audio goes in a cascaded agent, and what a speech-to-speech session changes
- **Session 3 · Turn-taking and interruption**: When the caller has finished, when to stop talking, and the trade between cut-ins and slow replies
- **Session 4 · Tool calls during speech**: Confirm the key fields aloud, then call the booking tool, and keep the line from going silent

#### [day3#review-day2] What do you write under the slice?

*Review of Day 2*

**Question:** Telephone clips: WER 0.133 with a 95% interval of 0.085 to 0.186. All clips: 0.089, interval 0.060 to 0.120. What does the report say about telephone callers?

- A. Telephone callers are clearly worse served
- B. Telephone callers are served the same as everyone
- C. Not shown worse on these clips; the slice needs more clips to decide
- D. Nothing: a slice under half of the clips cannot be reported

### Session 1: Synthesis and read-back

#### [day3#s1] Synthesis and read-back

*Session 1*

- Write spoken forms of dates, party sizes and booking codes in Arabic and English
- Chunk a booking code so that it can be heard and repeated
- Score a listening test by category with intervals

#### [day3#spoken-forms] Write what the caller should hear, not what the database holds

*What the voice is given*

| Field | Stored | English, spoken | Arabic, spoken |
| --- | --- | --- | --- |
| Date | 2026-12-03 | Thursday the third of December | الخميس ثلاثة ديسمبر |
| Party | 7 | seven people | سبعة أشخاص |
| Party | 2 | two people | شخصين |
| Party | 12 | twelve people | اثنا عشر شخصا |
| Year | 2027-01-02 | Saturday the second of January 2027 | السبت اثنين يناير 2027 |

> **What goes wrong.** A voice handed "2026-12-03" may read it as a number, a year, or digit by digit, and a different voice may choose differently.

#### [day3#chunk-the-code] Chunk a code the way people repeat phone numbers

*The booking code*

1. **Stored** HTB-4821
2. **Letters** H, T, B
3. **Digit pairs** four eight, two one
4. **Arabic** إتش، تي، بي، أربعة ثمانية، اثنين واحد

Each digit is said on its own: "forty-eight twenty-one" makes the caller translate back to digits.

#### [day3#length-rule] Keep a confirmation short enough to hold in memory

*Lab 3.1, three confirmations*

| Code | English (s) | Arabic (s) |
| --- | --- | --- |
| HTB-4821 | 9.93 | 11.04 |
| HTB-1590 | 10.71 | 10.96 |
| HTB-3007 | 10.64 | 10.48 |

> **The course's rule:** at most 12 seconds, with the code last so it is freshest when the caller writes it down.

#### [day3#listening-test] Read-back fixed dates and numbers; names did not clearly move

*Lab 3.1, 32 answers per cell*

| Category | Raw | Read-back | 95% interval, read-back | Shown better? |
| --- | --- | --- | --- | --- |
| Dates | 16/32 | 31/32 | 0.84 to 0.99 | yes |
| Numbers | 16/32 | 32/32 | 0.89 to 1.00 | yes |
| Names | 29/32 | 31/32 | 0.84 to 0.99 | no |

"Raw" is the stored form handed to the voice; "read-back" is the spoken form.

#### [day3#checkpoint-1] Which read-back?

*Checkpoint*

**Question:** Rahhal must confirm booking HTB-1590 for twelve people on 2026-12-11. Which line goes to the voice?

- A. "Friday the eleventh of December, for twelve people. Your code is H, T, B, one five, nine zero."
- B. "2026-12-11, 12 people. Your code is HTB-1590."
- C. "Friday the eleventh of December, for twelve people. Your code is H T B fifteen ninety."
- D. "Your code is H, T, B, one five, nine zero, I repeat, H, T, B, one five, nine zero, for Friday the eleventh, the eleventh, of December, for twelve, twelve people."

#### [day3#lab-3-1] Read-back that callers understand

Lab 3.1 · 25 min

Turn booking confirmations into spoken Arabic and English, synthesise them, and score a short listening test on names, numbers and dates.

[D3_1_readback.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D3_1_readback.ipynb)

- [ ] Spoken forms of dates, numbers and codes in two languages (10 min)
- [ ] Chunk the booking code for the ear (4 min)
- [ ] Synthesise and check the spoken length (4 min)
- [ ] Listening-test accuracy by category, with intervals (7 min)
- [ ] ✱ Stretch: Spell an unusual name letter by letter and test it again

### Session 2: Cascaded versus speech-to-speech

#### [day3#s2] Cascaded versus speech-to-speech

*Session 2*

- Trace per-stage latency of a cascaded voice agent
- Compute time to first audio at the median and the 90th percentile
- Compare a cascaded and a speech-to-speech design on the same calls

#### [day3#two-designs] A cascade passes text between three models; speech-to-speech is one model

*Two ways to build a voice agent*

- **Cascaded.** Detector, recogniser, language model, voice. Every stage can be measured, swapped and checked, and there is a transcript of what the caller said.
- **Speech-to-speech.** Audio in, audio out, with its own turn detection. Fewer hand-offs and usually a faster first audio; the stages are hidden inside one model.

> **Rahhal today** is cascaded on hosted open-weight models. Lab 3.2 compares it with traces of a hosted speech-to-speech session.

#### [day3#ttfa-stages] Time to first audio adds every stage on the path to the first sound

*The number that callers feel*

1. **Endpoint** sure the caller stopped
2. **Recogniser** final text
3. **Model** first sentence
4. **Voice** first audio chunk
5. **Network** to the phone

> **Budget: 1,200 ms** from the end of the caller's speech, held at the 90th percentile.

#### [day3#stage-table] The median turn is over budget, and the tail is twice the budget

*Lab 3.2, 20 turns of the cascade*

| Stage | p50 (ms) | p90 (ms) |
| --- | --- | --- |
| Endpoint | 474 | 504 |
| Recogniser final | 128 | 186 |
| Model first token | 301 | 1,438 |
| Voice first audio | 140 | 164 |
| Network | 54 | 74 |
| Time to first audio | 1,552 | 2,628 |

#### [day3#over-budget] Two causes stand out among the slow turns: waiting for the whole reply, and tools

*Lab 3.2, the turns over 1,200 ms*

- **15 / 20** turns over the budget
- **7** of them waited for the full reply before the voice started
- **4** of them called a tool before speaking

#### [day3#stream-first-sentence] Starting the voice on the first sentence takes 324 ms off the median

*Lab 3.2, step 4*

|  | p50 (ms) | p90 (ms) | Within budget |
| --- | --- | --- | --- |
| As traced | 1,552 | 2,628 | 5/20 |
| Every turn streamed | 1,228 | 2,362 | 9/20 |

> **Still over at the 90th percentile.** The tool turns and the endpoint remain.

#### [day3#s2s-comparison] On these traces, speech-to-speech is faster at both ends

*Lab 3.2, step 3*

| Design | p50 (ms) | p90 (ms) | Within budget | p50 tool turns |
| --- | --- | --- | --- | --- |
| Cascaded | 1,552 | 2,628 | 25% | 2,508 |
| Speech-to-speech | 562 | 1,248 | 85% | 1,266 |

Both trace sets are synthetic. The shape is typical; the numbers are not a benchmark of any product.

#### [day3#what-you-lose] Speech-to-speech gives up the text you evaluated yesterday

*The other side of the trade*

- No separate transcript to **slice by dialect** and channel, as in Lab 2.3.
- No text to **check before a tool call**: the booking arguments come out of one model.
- One vendor's voice, turn detection and model, **changed together**.
- Usually **priced per minute of audio**, which Lab 4.3 compares.

#### [day3#checkpoint-2] What do you fix first?

*Checkpoint*

**Question:** A cascade has a median time to first audio of 1,550 ms. In seven of twenty turns the voice starts only after the model has written the whole reply. What change do you make first?

- A. Swap the recogniser for a faster one
- B. Move the servers closer to the callers
- C. Switch to a smaller language model
- D. Start the voice on the first sentence of the reply

#### [day3#lab-3-2] Where the time goes

Lab 3.2 · 25 min

Trace per-stage latency of a cascaded agent over 20 turns and compare time to first audio with provided traces of a speech-to-speech session.

[D3_2_latency_trace.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D3_2_latency_trace.ipynb)

- [ ] Read the traces into stages (5 min)
- [ ] Per-stage time and time to first audio, median and 90th percentile (8 min)
- [ ] The same for the speech-to-speech traces (6 min)
- [ ] What streaming the first sentence would save (6 min)
- [ ] ✱ Stretch: Allocate the budget of 1,200 ms across stages and test it

### Session 3: Turn-taking and interruption

#### [day3#s3] Turn-taking and interruption

*Session 3*

- Explain end-of-turn detection by silence and by content
- Count false cut-ins and late or missed turns for a threshold
- Handle a caller who interrupts the agent

#### [day3#end-of-turn] Every millisecond spent waiting for silence is added to the reply

*Has the caller finished?*

- The pipeline after the endpoint takes **620 ms** on Rahhal's clock.
- So the silence threshold can be at most **580 ms** before every reply is late.
- Callers pause **up to 1,096 ms** inside a turn, longest before a number or a date.

- caller: can I change · the date to
- pause: a long silence while the caller thinks
- caller: the eleventh

> **What goes wrong.** A threshold short enough for the budget is shorter than the pauses inside turns: Rahhal cuts in.

#### [day3#threshold-sweep] On silence alone, the best threshold gets half the turns right

*Lab 3.3, 48 caller turns*

| Item | Value |
| --- | --- |
| 300 ms | 11 ok · 37 cut-ins |
| 400 ms | 21 ok · 27 cut-ins |
| 500 ms | 24 ok · 24 cut-ins |
| 600 ms | 0 ok · 24 late |
| 900 ms | 0 ok · 9 missed |

#### [day3#hold-rule] Wait longer only when the words say the caller is mid-phrase

*Use what was said, not only the silence*

```python
# file: Lab 3.3
HOLD_WORDS = {"for", "on", "to", "and",
              "لعدد", "يوم", "على", "في", "و"}

def hold(text_before):
    last = text_before.split()[-1]
    return 600 if last in HOLD_WORDS else 0
```

- **24 → 32** turns right out of 48 at 500 ms
- **24 → 16** cut-ins

#### [day3#barge-in] Stop for an interruption; keep talking through "mm"

*When the caller talks over Rahhal*

- **Backchannel.** "mm", "aha", إيه: 120 to 250 ms. The caller is listening. Stopping here makes the agent stutter.
- **Interruption.** "No, the eleventh": 600 ms or more. Stop within 300 ms, and listen.

> **Lab 3.3 stretch.** Stop after 260 ms of continuous caller speech: no false stops on the backchannels, every interruption handled within 300 ms.

#### [day3#checkpoint-3] Why not just wait longer?

*Checkpoint*

**Question:** Rahhal cuts in on callers who pause before a date. The pipeline after the endpoint takes 620 ms and the budget is 1,200 ms. A colleague proposes raising the silence threshold from 500 to 900 ms for every turn. What happens?

- A. Fewer cut-ins and no other change
- B. Fewer cut-ins, but every reply is late and some callers give up and speak again
- C. Faster replies, because the recogniser gets more audio
- D. Rahhal stops reacting when the caller interrupts

#### [day3#lab-3-3] Tune the end of a turn

Lab 3.3 · 25 min

Tune end-of-turn detection on scripted calls and count false cut-ins and missed turns for each threshold.

[D3_3_end_of_turn.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D3_3_end_of_turn.ipynb)

- [ ] Replay the scripted calls frame by frame (5 min)
- [ ] An end-of-turn rule on silence (7 min)
- [ ] Sweep the threshold: cut-ins against late turns (8 min)
- [ ] Hold the turn when the caller is mid-number (5 min)
- [ ] ✱ Stretch: Stop the agent within 300 ms when the caller talks over it

### Session 4: Tool calls during speech

#### [day3#s4] Tool calls during speech

*Session 4*

- Confirm key booking fields aloud before a write
- Measure the latency a tool call adds to a turn
- Mask a slow tool with a short spoken line without misleading the caller

#### [day3#heard-not-said] An agent that books on what it heard books what the recogniser got wrong

*Lab 3.4, call K2*

**Caller, as heard:** أبي أحجز جولة في شعب النقوش يوم 2026-12-14 لعدد 4 أشخاص

**Rahhal, booking at once (weak example):** تم الحجز، رقمه HTB-1408.

> **The caller said the 11th.** The booking exists before anyone could notice the 14th.

#### [day3#tool-checks] The booking tool checks its arguments and answers in a sentence the agent can say

*The tool defends itself*

```python
# file: Lab 3.4
def book_visit(site_code, date, party_size, name):
    if site_code not in SITES:
        raise ToolError("that site is not one of ours")
    if d < TODAY:
        raise ToolError("that date has passed")
    if not 1 <= party_size <= 12:
        raise ToolError("a group can be 1 to 12 people")
    if booked(site_code, date) + party_size > 20:
        raise ToolError("that day is full ...")
    return store.add(...)
```

- **Checks the model cannot skip.** A prompt can ask the model for valid arguments; only the tool can refuse invalid ones. The error text is written for the caller's ear.

#### [day3#confirm-then-book] Read the key fields back, book only after a yes, and confirm again after any change

*The confirmation policy*

1. **1 · Slots full** site, date, party
2. **2 · Read back** in the spoken forms of Session 1
3. **3 · Yes?** a no or a new value goes back to 2
4. **4 · Book** with the confirmed slots

> **Takeaway.** The tool is called with the slots the caller last said yes to, never with older ones.

#### [day3#six-calls] Confirmation turned two wrong bookings into two corrections

*Lab 3.4, six scripted calls*

| Policy | Intended booking | Wrong booking | Turns per call |
| --- | --- | --- | --- |
| Book when the slots are full | 4/6 | 2 | 1 to 3 |
| Confirm, then book | 6/6 | 0 | 2 to 4 |

The cost is one turn per call. The wrong bookings were K2 (the 14th for the 11th) and K5 (six people for five).

#### [day3#tool-latency] A 900 ms tool on the path adds 900 ms of silence; a true filler line hides it

*Lab 3.4, call K1, the booking turn*

- **1,220 ms** an ordinary turn
- **2,135 ms** the booking turn, silent until the tool returns
- **1,235 ms** the booking turn with a filler line

#### [day3#honest-filler] A filler says what is happening, never what has not happened yet

*What the filler may say*

**True (good example):** One moment, I am booking that. لحظة، أحجز لك الآن.

**Not yet true (weak example):** Your booking is confirmed. تم تأكيد حجزك.

> **K4 is why.** The 5th was full: the tool refused, and a filler that had already said "confirmed" would have been false.

#### [day3#checkpoint-4] Where does the confirmation go?

*Checkpoint*

**Question:** Rahhal has heard: Clay Village, 9 December, six people. The caller meant five. Which sequence prevents a wrong booking?

- A. Book, then read the booking back and cancel it if the caller objects
- B. Book at once: the tool refuses invalid party sizes
- C. Read back "Clay Village, Wednesday the ninth of December, six people", wait for a yes, and read back again after "no, five"
- D. Say "one moment, I am booking that" and book while the caller listens

#### [day3#lab-3-4] A confirmed booking tool

Lab 3.4 · 25 min

Add a booking tool to a provided agent that confirms the key fields aloud before it books, and measure the latency it adds.

[D3_4_booking_tool.ipynb](https://sdaiaacademy.github.io/ae-408/labs/D3_4_booking_tool.ipynb)

- [ ] The booking tool and its argument checks (5 min)
- [ ] Confirm site, date and party size aloud before the call (8 min)
- [ ] Six scripted calls: no booking without a yes (6 min)
- [ ] Measure the added time and fill the gap (6 min)
- [ ] ✱ Stretch: Make a retried booking safe with an idempotency key

#### [day3#wrap-up] What to carry into the capstone

*Day 3 · Three things to keep*

- **Speak for the ear.** Spoken forms, chunked codes, under 12 seconds, and a listening test by category.
- **Trace before tuning.** Per-stage times at the 90th percentile; stream the first sentence; hold the turn only mid-phrase.
- **Confirm before writing.** Read back, book on a yes with the last confirmed slots, and fill silence only with what is true.

#### [day3#next] Evaluating and choosing: test sets, simulated callers, cost and consent

*Tomorrow · Day 4*

- Keep today's artifacts: the latency trace and the threshold sweep feed the decision record.
- Think of one caller who would break Rahhal: the simulated callers of Lab 4.2 are built from such cards.
- Read the consent and labelling sections of the national Deepfakes Guidelines before Session 4.
