---
course: "Multimodal and Speech Systems Engineering"
code: "AE-408"
version: "2027.1.0"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ae-408/index.html"
---

# Multimodal and Speech Systems Engineering

هندسة الأنظمة متعددة الوسائط وأنظمة الكلام

AI Engineering Track · 4 teaching days + capstone day · 26 hours · Level 400

Build and evaluate applications that see, listen and speak in Arabic and English, and choose their design on measured quality, latency and cost

Participants build and evaluate applications that see, listen and speak, with Arabic as the main case. For the fictional Heritage Trails Authority they extract grounded fields from visitor and ranger photos with vision-language models, benchmark open-weight speech recognisers on dialects and code-switched speech, test synthesised read-back, and assemble a bilingual voice booking line with turn-taking, interruption and tool calls within a latency budget. They test it with simulated callers and choose between open-weight and hosted, cascaded and speech-to-speech designs on measured quality, latency and cost. Photos are public-domain or synthetic; calls use synthetic voices and public speech corpora.

**Who it is for:** Specialists. Engineers who have completed the level 300 core and the practicum, or can show equivalent work: an AI system they built, operated and defended in review.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

## The case study

**Heritage Trails Authority.** Heritage Trails Authority is a fictional authority that runs twelve heritage sites and trails, with a photo-reporting service for visitors and rangers (Lamha) and a bilingual voice line for booking guided visits (Rahhal). Participants extract grounded fields from 60 synthetic trail photos, benchmark two open-weight recognisers on 50 sliced clips, build and trace the booking line, test it with simulated callers and write the decision record; all photos, clips, traces and measurements are synthetic and generated with a fixed seed, and no real voice is used.

## The course

### Day 1: Seeing

Slides: https://sdaiaacademy.github.io/ae-408/slides/day1.md

- **Session 1: How a vision-language model sees**
  - Explain how an image becomes visual tokens and what resolution costs
  - Measure tokens, latency and accuracy for one question at three resolutions
  - Choose the cheapest resolution that meets an accuracy target
  - [Lab 1.1: One question, three resolutions (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D1_1_resolution_tokens.ipynb)
- **Session 2: Structured extraction from photos**
  - Write a schema whose fields and enums catch wrong extractions
  - Validate and repair a model reply once before giving up
  - Compare two models on field accuracy, cost and latency
  - [Lab 1.2: Validated incident fields (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D1_2_incident_fields.ipynb)
- **Session 3: Grounding answers in pixels**
  - Compute intersection over union and match boxes to references
  - Report box precision and recall at a stated threshold
  - Probe for invented objects on scenes that do not contain them
  - [Lab 1.3: Boxes and invented objects (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D1_3_grounding_boxes.ipynb)
- **Session 4: Arabic text and hidden instructions**
  - Compute character error rate for Arabic text read from images
  - Explain how an instruction hidden in an image reaches the model
  - Test a mitigation against an injected instruction and log the result
  - [Lab 1.4: Signage and an injected instruction (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D1_4_signage_injection.ipynb)

### Day 2: Listening

Slides: https://sdaiaacademy.github.io/ae-408/slides/day2.md

- **Session 1: From waveform to text**
  - Describe the path from waveform to features to text in two recogniser families
  - Compute word error rate from an alignment of substitutions, deletions and insertions
  - Explain why corpus error rate differs from the mean of clip error rates
  - [Lab 2.1: Two recognisers, 50 clips (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D2_1_two_recognisers.ipynb)
- **Session 2: Normalisation decides the error rate**
  - Write explicit Arabic normalisation rules for diacritics, letter variants and numerals
  - Recompute error rates under each rule set and explain the change
  - Spot a rule that hides a real recognition error
  - [Lab 2.2: Rules before rates (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D2_2_normalisation.ipynb)
- **Session 3: Dialects and code-switching**
  - Slice error rates by dialect, channel and code-switching
  - Add clip-level bootstrap intervals to each slice
  - Decide which slice differences are real given their size
  - [Lab 2.3: Slices with intervals (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D2_3_dialect_slices.ipynb)
- **Session 4: Streaming and silence**
  - Detect speech frames with an energy-based voice activity detector
  - Stream segments to a recogniser and measure when text arrives
  - Catch and suppress text produced on silent segments
  - [Lab 2.4: Text on silence (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D2_4_streaming_silence.ipynb)

### Day 3: Speaking

Slides: https://sdaiaacademy.github.io/ae-408/slides/day3.md

- **Session 1: Synthesis and read-back**
  - Write spoken forms of dates, party sizes and booking codes in Arabic and English
  - Chunk a booking code so that it can be heard and repeated
  - Score a listening test by category with intervals
  - [Lab 3.1: Read-back that callers understand (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D3_1_readback.ipynb)
- **Session 2: Cascaded versus speech-to-speech**
  - Trace per-stage latency of a cascaded voice agent
  - Compute time to first audio at the median and the 90th percentile
  - Compare a cascaded and a speech-to-speech design on the same calls
  - [Lab 3.2: Where the time goes (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D3_2_latency_trace.ipynb)
- **Session 3: Turn-taking and interruption**
  - Explain end-of-turn detection by silence and by content
  - Count false cut-ins and late or missed turns for a threshold
  - Handle a caller who interrupts the agent
  - [Lab 3.3: Tune the end of a turn (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D3_3_end_of_turn.ipynb)
- **Session 4: Tool calls during speech**
  - Confirm key booking fields aloud before a write
  - Measure the latency a tool call adds to a turn
  - Mask a slow tool with a short spoken line without misleading the caller
  - [Lab 3.4: A confirmed booking tool (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D3_4_booking_tool.ipynb)

### Day 4: Evaluating and choosing

Slides: https://sdaiaacademy.github.io/ae-408/slides/day4.md

- **Session 1: Multimodal test sets**
  - Define coverage targets across modality, dialect and task
  - Select a stratified test set from a pool of candidates
  - Report the coverage table and the gaps it leaves
  - [Lab 4.1: Sixty items with coverage (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D4_1_test_set.ipynb)
- **Session 2: Simulated callers**
  - Write simulated callers with a goal, a dialect and a behaviour
  - Grade a call on its outcome in the booking store
  - Separate task failures from transcript errors
  - [Lab 4.2: Twenty simulated calls (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D4_2_simulated_callers.ipynb)
- **Session 3: Choosing by quality, latency and cost**
  - Compute cost per call for a self-hosted and a hosted pipeline
  - Compare pipelines on quality, latency and cost with their uncertainty
  - Write a decision record that a reviewer re-runs to the same figures
  - [Lab 4.3: The decision record (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D4_3_decision_record.ipynb)
- **Session 4: Voice, faces and consent**
  - Classify recordings, transcripts and photos and set their retention
  - Minimise what is stored: blur faces and redact transcripts
  - Write the synthetic-voice disclosure and test when callers hear it
  - [Lab 4.4: The data-handling note (25 min)](https://sdaiaacademy.github.io/ae-408/labs/D4_4_consent_note.ipynb)

### Capstone: Capstone project presentations

Slides: https://sdaiaacademy.github.io/ae-408/slides/capstone.md

## Capstone

The Heritage Trails booking line and photo-reporting service, or an equivalent system, with test set, sliced evaluation, latency trace and decision record, in a public repository whose README reports measured results, defended live

**What you submit:** A public GitHub repository with the image pipeline, the speech evaluation, the voice agent, the test set and its simulation, the latency traces and the decision record, whose README reports the measured results and links the script that reproduces them. Then a live defence: the participant runs the system on a call and a photo the assessor supplies and explains one failure from its log.

**Rubric:**

- Image pipeline: 20%
- Speech evaluation: 25%
- Voice agent: 25%
- Test set and simulation: 20%
- Decision record: 10%

## Outcomes

- **LO1** Implement image applications with vision-language models that return validated structured fields grounded in the image, given 60 visitor and ranger photos with reference fields and boxes (Applied) Evidence: an extraction pipeline with field accuracy and grounding scores on the test set
- **LO2** Evaluate speech recognisers on Arabic dialects and code-switched speech with explicit normalisation rules, given two open-weight recognisers and a sliced set of public and synthetic clips (Performance) Evidence: an error-rate report by dialect and channel with intervals and the normalisation rules used
- **LO3** Build a bilingual voice agent that handles turn-taking, interruption and confirmed tool calls within a latency budget, given a booking tool and a budget for time to first audio (Performance) Evidence: a running agent with per-stage latency traces from twenty scripted calls
- **LO4** Diagnose failure modes specific to image and audio inputs, including invented objects, text produced on silence and instructions hidden in images, given seeded failing inputs for each modality (Performance) Evidence: a failure log with causes and a mitigation tested for each mode
- **LO5** Design a multimodal test set and an end-to-end evaluation with simulated callers, given the full booking and reporting system (Performance) Evidence: a test set with a coverage table across modality, dialect and task, and graded results
- **LO6** Decide between open-weight and hosted, cascaded and speech-to-speech designs on quality, latency and cost per call, given measured results for two pipelines (Performance) Evidence: a one-page decision record with the measurements and a script that a reviewer re-runs to the same figures

## Tools

- **Vision-language model access:** an open-weight model such as Gemma 4 through a free hosted endpoint, a hosted model through a chat-completions style endpoint
- **Open-weight speech recognition:** Whisper-family models (whisper-large-v3, whisper-large-v3-turbo) on a free hosted endpoint, wav2vec-family encoders
- **Voice activity detection and diarisation:** Silero VAD, pyannote.audio, an energy detector in numpy (the labs)
- **Speech synthesis and speech-to-speech:** an open-weight text-to-speech model such as Orpheus, with a Saudi Arabic voice, any hosted real-time speech model
- **Voice agent framework:** Pipecat, LiveKit Agents
- **Error-rate scoring:** jiwer, a custom scorer with Arabic normalisation
- **Public data:** Mozilla Common Voice, public-domain image collections
- **Evaluation harness:** Inspect, pytest with custom scorers

## Prerequisites

- AE-301 Applied Natural Language Processing Engineering
- AE-303 Evaluation-Driven Development for Language Model Applications
- Has built a language model application with structured outputs and tool calls
- Computes precision, recall and an error rate with an interval
- Setup: a laptop CPU with uv, or Google Colab. Every lab runs without a key on supplied inputs and a scripted stand-in; free keys for OpenRouter and Groq let the model-calling labs use hosted open-weight models. Nothing downloads a model. See labs/README.md.

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

---

SDAIA Academy · AI Engineering Track · Multimodal and Speech Systems Engineering

Course version 2027.1.0 · engine 1.0.0 · built 2026-11-15 · commit c687f48
