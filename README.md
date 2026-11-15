<!-- academy:title -->
# Multimodal and Speech Systems Engineering

هندسة الأنظمة متعددة الوسائط وأنظمة الكلام

AI Engineering Track · SDAIA Academy · AE-408 · Level 400

Build and evaluate applications that see, listen and speak in Arabic and English, and choose their design on measured quality, latency and cost

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

**Heritage Trails Authority** is a fictional authority that runs twelve heritage sites and trails. It has two services, both built in the labs: **Lamha** (لمحة), which turns visitor and ranger photos into incident records with boxes, and **Rahhal** (رحّال), a bilingual voice line for booking guided visits. The people of the case are Wedad Al-Omari (director of visitor services, owner of the booking line), Salem Al-Balawi (chief ranger, owner of the photo reports), Fayyad Al-Ghamdi (contact-centre platform engineer, owner of the budget of 1,200 ms to first audio), Ghusoun Al-Mutlaq (data protection officer) and Muhra Al-Dosari (AI engineer, the participant's role).

All data is synthetic and generated with a fixed seed by `labs/prepare_data.py`: 60 drawn trail photos (1280 by 960) with reference fields and boxes, 50 speech clips described by their reference transcripts and the recorded transcripts of two recognisers (written by an error model; no audio and no real voice), a listening test, latency traces, scripted calls, caller cards, a pool of test-set candidates and the measurements of two pipelines. Planted problems (markers too small to read, invented objects, instructions on signs, a recogniser ranking that flips under normalisation, a weak dialect on telephone audio, text on silence, a cut-in threshold, a caller who changes their mind) are each found by a named lab.

## How the course runs

Four teaching days of four 50-minute sessions, each with about 25 minutes of concepts and a 25-minute lab, then a capstone day. Every session ends its concepts with a checkpoint. The labs run on a laptop processor or in Google Colab, with or without keys: without keys they use the supplied inputs and a scripted stand-in model whose rules are written in `labs/trails.py`; with free keys they call free hosted open-weight models. Nothing downloads a model. AI policy: no AI assistance in the supervised check and in the Day 2 normalisation lab; in the other labs an assistant may give hints but does not write pipelines or scorers; anything goes in the capstone, which is defended live. See [`labs/README.md`](labs/README.md).

## Before Day 1 and after the course

Guided pre-work, about two hours:

- Set up the labs (Colab, or `uv sync` in `labs/`), run `uv run python prepare_data.py --check`, and open Lab 1.1 so that it runs to the end on the stand-in.
- Revisit the prerequisites the course builds on: structured outputs with a schema, a tool call, precision and recall, and a Wilson or bootstrap interval.
- Optional: create free OpenRouter and Groq keys to run the model-calling labs on hosted open-weight models.
- Before Day 4: read the consent and labelling sections of the SDAIA Deepfakes Guidelines.

Tracked follow-up task, within 30 days: meet one condition of your decision record (for example the 90th percentile of time to first audio under the budget) and send the new trace with its fingerprint.

## Assessment

- A supervised check without AI assistance: compute error rates under two normalisation rules and diagnose three failing inputs (20%).
- The capstone repository scored on the rubric below (60%).
- A live defence with a call or a photo the assessor supplies (20%).

Passing: 70% overall and at least 60% on the capstone rubric.

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | One question, three resolutions | [`D1_1_resolution_tokens.ipynb`](labs/D1_1_resolution_tokens.ipynb) |
| 1.2 | Day 1 · Session 2 | Validated incident fields | [`D1_2_incident_fields.ipynb`](labs/D1_2_incident_fields.ipynb) |
| 1.3 | Day 1 · Session 3 | Boxes and invented objects | [`D1_3_grounding_boxes.ipynb`](labs/D1_3_grounding_boxes.ipynb) |
| 1.4 | Day 1 · Session 4 | Signage and an injected instruction | [`D1_4_signage_injection.ipynb`](labs/D1_4_signage_injection.ipynb) |
| 2.1 | Day 2 · Session 1 | Two recognisers, 50 clips | [`D2_1_two_recognisers.ipynb`](labs/D2_1_two_recognisers.ipynb) |
| 2.2 | Day 2 · Session 2 | Rules before rates | [`D2_2_normalisation.ipynb`](labs/D2_2_normalisation.ipynb) |
| 2.3 | Day 2 · Session 3 | Slices with intervals | [`D2_3_dialect_slices.ipynb`](labs/D2_3_dialect_slices.ipynb) |
| 2.4 | Day 2 · Session 4 | Text on silence | [`D2_4_streaming_silence.ipynb`](labs/D2_4_streaming_silence.ipynb) |
| 3.1 | Day 3 · Session 1 | Read-back that callers understand | [`D3_1_readback.ipynb`](labs/D3_1_readback.ipynb) |
| 3.2 | Day 3 · Session 2 | Where the time goes | [`D3_2_latency_trace.ipynb`](labs/D3_2_latency_trace.ipynb) |
| 3.3 | Day 3 · Session 3 | Tune the end of a turn | [`D3_3_end_of_turn.ipynb`](labs/D3_3_end_of_turn.ipynb) |
| 3.4 | Day 3 · Session 4 | A confirmed booking tool | [`D3_4_booking_tool.ipynb`](labs/D3_4_booking_tool.ipynb) |
| 4.1 | Day 4 · Session 1 | Sixty items with coverage | [`D4_1_test_set.ipynb`](labs/D4_1_test_set.ipynb) |
| 4.2 | Day 4 · Session 2 | Twenty simulated calls | [`D4_2_simulated_callers.ipynb`](labs/D4_2_simulated_callers.ipynb) |
| 4.3 | Day 4 · Session 3 | The decision record | [`D4_3_decision_record.ipynb`](labs/D4_3_decision_record.ipynb) |
| 4.4 | Day 4 · Session 4 | The data-handling note | [`D4_4_consent_note.ipynb`](labs/D4_4_consent_note.ipynb) |
<!-- /academy:labs -->

## Capstone

The Heritage Trails booking line and photo-reporting service, or an equivalent system, with test set, sliced evaluation, latency trace and decision record, in a public repository whose README reports measured results, defended live

**Submission:** A public GitHub repository with the image pipeline, the speech evaluation, the voice agent, the test set and its simulation, the latency traces and the decision record, whose README reports the measured results and links the script that reproduces them. Then a live defence: the participant runs the system on a call and a photo the assessor supplies and explains one failure from its log.

| Criterion | Weight |
|---|---|
| Image pipeline | 20 |
| Speech evaluation | 25 |
| Voice agent | 25 |
| Test set and simulation | 20 |
| Decision record | 10 |

The defence takes 10 minutes, with 5 minutes of questions.

## Prerequisites

- AE-301 Applied Natural Language Processing Engineering
- AE-303 Evaluation-Driven Development for Language Model Applications
- Has built a language model application with structured outputs and tool calls
- Computes precision, recall and an error rate with an interval

<!-- academy:tools -->
## Tools

Each line is a capability; the examples are interchangeable.

- **Vision-language model access:** an open-weight model such as Gemma 4 through a free hosted endpoint, a hosted model through a chat-completions style endpoint
- **Open-weight speech recognition:** Whisper-family models (whisper-large-v3, whisper-large-v3-turbo) on a free hosted endpoint, wav2vec-family encoders
- **Voice activity detection and diarisation:** Silero VAD, pyannote.audio, an energy detector in numpy (the labs)
- **Speech synthesis and speech-to-speech:** an open-weight text-to-speech model such as Orpheus, with a Saudi Arabic voice, any hosted real-time speech model
- **Voice agent framework:** Pipecat, LiveKit Agents
- **Error-rate scoring:** jiwer, a custom scorer with Arabic normalisation
- **Public data:** Mozilla Common Voice, public-domain image collections
- **Evaluation harness:** Inspect, pytest with custom scorers
<!-- /academy:tools -->

<!-- academy:sources -->
## Sources

### Models and services

- [Gemma 4 31B model card (visual token budgets)](https://huggingface.co/google/gemma-4-31b-it)
- [OpenRouter: models list](https://openrouter.ai/models)
- [Groq: speech to text](https://console.groq.com/docs/speech-to-text)
- [Groq: text to speech](https://console.groq.com/docs/text-to-speech)
- [Groq: rate limits](https://console.groq.com/docs/rate-limits)

### Libraries and frameworks

- [jiwer on PyPI](https://pypi.org/project/jiwer/)
- [Pipecat on PyPI](https://pypi.org/project/pipecat-ai/)
- [LiveKit Agents on PyPI](https://pypi.org/project/livekit-agents/)
- [Silero VAD on PyPI](https://pypi.org/project/silero-vad/)
- [pyannote.audio on PyPI](https://pypi.org/project/pyannote.audio/)
- [Inspect on PyPI](https://pypi.org/project/inspect-ai/)

### Evidence and data

- [Koenecke et al., Careless Whisper: Speech-to-Text Hallucination Harms (2024)](https://arxiv.org/abs/2402.08021)
- [OWASP Top 10 for LLM Applications 2025: LLM01 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [Mozilla Common Voice](https://commonvoice.mozilla.org/)

### National references

- [Personal Data Protection Law](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [Implementing Regulation of the Personal Data Protection Law](https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf)
- [SDAIA Deepfakes Guidelines](https://sdaia.gov.sa/en/SDAIA/about/Files/File0001.pdf)
- [SDAIA Generative AI Guideline for Government](https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf)
- [SDAIA Generative AI Guideline for Public](https://sdaia.gov.sa/en/SDAIA/about/Files/GenerativeAIPublicEN.pdf)
- [SDAIA AI Ethics Principles](https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf)
- [NDMO Data Classification Policy](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
<!-- /academy:sources -->

### National references

- Personal Data Protection Law and its implementing regulations: <https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf> and <https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf>
- SDAIA Deepfakes Guidelines: <https://sdaia.gov.sa/en/SDAIA/about/Files/File0001.pdf>
- SDAIA Generative AI Guidelines: <https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf> (government) and <https://sdaia.gov.sa/en/SDAIA/about/Files/GenerativeAIPublicEN.pdf> (public)
- SDAIA AI Ethics Principles: <https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf>
- NDMO Data Classification Policy: <https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf>
