<!-- academy:title -->
# Multimodal and Speech Systems Engineering

هندسة الأنظمة متعددة الوسائط وأنظمة الكلام

AI Engineering Track · SDAIA Academy · AE-408 · Level 400

REPLACE: one line under the title: what participants can do after the course

Participants build and evaluate applications that see, listen and speak, with Arabic as the main case. For the fictional Heritage Trails Authority they extract grounded fields from visitor and ranger photos with vision-language models, benchmark open-weight speech recognisers on dialects and code-switched speech, test synthesised read-back, and assemble a bilingual voice booking line with turn-taking, interruption and tool calls within a latency budget. They test it with simulated callers and choose between open-weight and hosted, cascaded and speech-to-speech designs on measured quality, latency and cost. Photos are public-domain or synthetic; calls use synthetic voices and public speech corpora.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

**Course page:** https://sdaiaacademy.github.io/ae-408/
<!-- /academy:title -->

## Outcomes

| | Outcomes | Level | Evidence |
|---|---|---|---|
| LO1 | Implement image applications with vision-language models that return validated structured fields grounded in the image, given 60 visitor and ranger photos with reference fields and boxes | Applied | an extraction pipeline with field accuracy and grounding scores on the test set |
| LO2 | Evaluate speech recognisers on Arabic dialects and code-switched speech with explicit normalisation rules, given two open-weight recognisers and a sliced set of public and synthetic clips | Performance | an error-rate report by dialect and channel with intervals and the normalisation rules used |
| LO3 | Build a bilingual voice agent that handles turn-taking, interruption and confirmed tool calls within a latency budget, given a booking tool and a budget for time to first audio | Performance | a running agent with per-stage latency traces from twenty scripted calls |
| LO4 | Diagnose failure modes specific to image and audio inputs, including invented objects, text produced on silence and instructions hidden in images, given seeded failing inputs for each modality | Performance | a failure log with causes and a mitigation tested for each mode |
| LO5 | Design a multimodal test set and an end-to-end evaluation with simulated callers, given the full booking and reporting system | Performance | a test set with a coverage table across modality, dialect and task, and graded results |
| LO6 | Decide between open-weight and hosted, cascaded and speech-to-speech designs on quality, latency and cost per call, given measured results for two pipelines | Performance | a one-page decision record with the measurements and a script that a reviewer re-runs to the same figures |

<!-- academy:units -->
## Units

| Unit | Title | Sessions | Slides |
|---|---|---|---|
| Day 1 | Seeing | How a vision-language model sees; Structured extraction from photos; Grounding answers in pixels; Arabic text and hidden instructions | [`slides/day1.html`](slides/day1.html) |
| Day 2 | Listening | From waveform to text; Normalisation decides the error rate; Dialects and code-switching; Streaming and silence | [`slides/day2.html`](slides/day2.html) |
| Day 3 | Speaking | Synthesis and read-back; Cascaded versus speech-to-speech; Turn-taking and interruption; Tool calls during speech | [`slides/day3.html`](slides/day3.html) |
| Day 4 | Evaluating and choosing | Multimodal test sets; Simulated callers; Choosing by quality, latency and cost; Voice, faces and consent | [`slides/day4.html`](slides/day4.html) |
| Capstone | Capstone project presentations |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**REPLACE: the name of the fictional organisation every lab works on.** REPLACE: two sentences on the case study and its synthetic data

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Measure tokens, latency and accuracy for one question at three image resolutions | [`D1_1_measure_tokens_latency.ipynb`](labs/D1_1_measure_tokens_latency.ipynb) |
| 1.2 | Day 1 · Session 2 | Extract validated incident fields from 30 photos with an open-weight and a hosted model | [`D1_2_extract_validated_incident.ipynb`](labs/D1_2_extract_validated_incident.ipynb) |
| 1.3 | Day 1 · Session 3 | Score returned boxes against references and flag answers about objects that are not there | [`D1_3_score_returned_boxes.ipynb`](labs/D1_3_score_returned_boxes.ipynb) |
| 1.4 | Day 1 · Session 4 | Read Arabic signage images, compute character error rate and test an image carrying an injected instruction | [`D1_4_read_arabic_signage.ipynb`](labs/D1_4_read_arabic_signage.ipynb) |
| 2.1 | Day 2 · Session 1 | Run two open-weight recognisers on 50 clips and compute word error rates | [`D2_1_run_two_open.ipynb`](labs/D2_1_run_two_open.ipynb) |
| 2.2 | Day 2 · Session 2 | Apply Arabic normalisation rules to provided transcripts and recompute the error rates | [`D2_2_apply_arabic_normalisation.ipynb`](labs/D2_2_apply_arabic_normalisation.ipynb) |
| 2.3 | Day 2 · Session 3 | Slice error rates by dialect and by code-switched speech and add intervals | [`D2_3_slice_error_rates.ipynb`](labs/D2_3_slice_error_rates.ipynb) |
| 2.4 | Day 2 · Session 4 | Stream recognition with voice activity detection and catch text produced on silent segments | [`D2_4_stream_recognition_voice.ipynb`](labs/D2_4_stream_recognition_voice.ipynb) |
| 3.1 | Day 3 · Session 1 | Synthesise booking confirmations and run a short listening test on names, numbers and dates | [`D3_1_synthesise_booking_confirmations.ipynb`](labs/D3_1_synthesise_booking_confirmations.ipynb) |
| 3.2 | Day 3 · Session 2 | Trace per-stage latency of a cascaded agent and compare time to first audio with provided traces of a speech-to-speech session | [`D3_2_trace_per_stage.ipynb`](labs/D3_2_trace_per_stage.ipynb) |
| 3.3 | Day 3 · Session 3 | Tune end-of-turn detection on scripted calls and count false cut-ins and missed turns | [`D3_3_tune_end_turn.ipynb`](labs/D3_3_tune_end_turn.ipynb) |
| 3.4 | Day 3 · Session 4 | Add a booking tool to a provided agent that confirms key fields aloud and measure the added latency | [`D3_4_add_booking_tool.ipynb`](labs/D3_4_add_booking_tool.ipynb) |
| 4.1 | Day 4 · Session 1 | Build a 60-item test set across image, audio and dialects with a coverage table | [`D4_1_build_60_item.ipynb`](labs/D4_1_build_60_item.ipynb) |
| 4.2 | Day 4 · Session 2 | Run 20 simulated calls against a provided agent and grade task success and transcript errors | [`D4_2_run_20_simulated.ipynb`](labs/D4_2_run_20_simulated.ipynb) |
| 4.3 | Day 4 · Session 3 | Compare open-weight and hosted pipelines on provided measurements and draft the decision record | [`D4_3_compare_open_weight.ipynb`](labs/D4_3_compare_open_weight.ipynb) |
| 4.4 | Day 4 · Session 4 | Write the data-handling note for recordings and photos and the synthetic-voice disclosure callers hear | [`D4_4_write_data_handling.ipynb`](labs/D4_4_write_data_handling.ipynb) |
<!-- /academy:labs -->

## Capstone

The Heritage Trails booking line and photo-reporting service, or an equivalent system, with test set, sliced evaluation, latency trace and decision record, in a public repository whose README reports measured results, defended live

**Submission:** REPLACE: what participants submit and how: a public repository link, or a shared folder for a course without code

## Prerequisites

- AE-301 Applied Natural Language Processing Engineering
- AE-303 Evaluation-Driven Development for Language Model Applications
- Has built a language model application with structured outputs and tool calls
- Computes precision, recall and an error rate with an interval

<!-- academy:tools -->
## Tools

Each line is a capability; the examples are interchangeable.

- **Vision-language model access:** an open-weight model on a notebook GPU, a hosted model through a chat-completions style endpoint
- **Open-weight speech recognition:** Whisper-family models, wav2vec-family encoders
- **Voice activity detection and diarisation:** Silero VAD, pyannote.audio
- **Speech synthesis and speech-to-speech:** an open-weight text-to-speech model, any hosted real-time speech model
- **Voice agent framework:** Pipecat, LiveKit Agents
- **Error-rate scoring:** jiwer, a custom scorer with Arabic normalisation
- **Public data:** Mozilla Common Voice, public-domain image collections
- **Evaluation harness:** Inspect, pytest with custom scorers
<!-- /academy:tools -->

<!-- academy:sources -->
## Sources

- REPLACE: every source the course cites, with its address, in course.json under "sources"; this list is written from there
<!-- /academy:sources -->

### National references

- Personal Data Protection Law and its implementing regulations: REPLACE: the address of the official text
- SDAIA Deepfakes Guidelines: REPLACE: the address of the official text
- SDAIA Generative AI Guidelines: REPLACE: the address of the official text
- SDAIA AI Ethics Principles: REPLACE: the address of the official text
- NDMO Data Classification Policy: REPLACE: the address of the official text
