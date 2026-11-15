# Multimodal and Speech Systems Engineering: labs

Sixteen notebooks, one per session, on the Heritage Trails case: Lamha (photo reports from visitors and rangers) and
Rahhal (the bilingual booking line). Every notebook starts from a supplied reference state and has a solution in
`solutions/`. All photos, clips, traces and measurements are synthetic and generated with a fixed seed; no real voice
is used.

## Quick start

- **Google Colab:** open a notebook from the table; its first cell clones this repository and installs
  `requirements-colab.txt`.
- **Locally:** install [uv](https://docs.astral.sh/uv/), then from `labs/` run `uv sync` and `uv run jupyter lab`.
  Python 3.12. A laptop CPU is enough: no model is downloaded.

Every notebook runs **without any key**. The model calls then go to a scripted stand-in that returns recorded or
generated answers, and each lab says so in its output. With free keys (below) the vision, speech and voice calls go to
hosted open-weight models instead.

| Unit | Session | Notebook | Calls a model when a key is set |
|---|---|---|---|
| Day 1 | Session 1 · How a vision-language model sees | [`D1_1_resolution_tokens.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D1_1_resolution_tokens.ipynb) | vision |
| Day 1 | Session 2 · Structured extraction from photos | [`D1_2_incident_fields.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D1_2_incident_fields.ipynb) | vision |
| Day 1 | Session 3 · Grounding answers in pixels | [`D1_3_grounding_boxes.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D1_3_grounding_boxes.ipynb) | vision |
| Day 1 | Session 4 · Arabic text and hidden instructions | [`D1_4_signage_injection.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D1_4_signage_injection.ipynb) | vision |
| Day 2 | Session 1 · From waveform to text | [`D2_1_two_recognisers.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D2_1_two_recognisers.ipynb) | speech, if audio was generated |
| Day 2 | Session 2 · Normalisation decides the error rate | [`D2_2_normalisation.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D2_2_normalisation.ipynb) | none (AI-off lab) |
| Day 2 | Session 3 · Dialects and code-switching | [`D2_3_dialect_slices.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D2_3_dialect_slices.ipynb) | none: recorded transcripts |
| Day 2 | Session 4 · Streaming and silence | [`D2_4_streaming_silence.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D2_4_streaming_silence.ipynb) | none: a scripted recogniser |
| Day 3 | Session 1 · Synthesis and read-back | [`D3_1_readback.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D3_1_readback.ipynb) | voice |
| Day 3 | Session 2 · Cascaded versus speech-to-speech | [`D3_2_latency_trace.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D3_2_latency_trace.ipynb) | none: supplied traces |
| Day 3 | Session 3 · Turn-taking and interruption | [`D3_3_end_of_turn.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D3_3_end_of_turn.ipynb) | none: scripted calls |
| Day 3 | Session 4 · Tool calls during speech | [`D3_4_booking_tool.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D3_4_booking_tool.ipynb) | none: scripted agent |
| Day 4 | Session 1 · Multimodal test sets | [`D4_1_test_set.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D4_1_test_set.ipynb) | none |
| Day 4 | Session 2 · Simulated callers | [`D4_2_simulated_callers.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D4_2_simulated_callers.ipynb) | none (stretch: a hosted caller) |
| Day 4 | Session 3 · Choosing by quality, latency and cost | [`D4_3_decision_record.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D4_3_decision_record.ipynb) | none: supplied measurements |
| Day 4 | Session 4 · Voice, faces and consent | [`D4_4_consent_note.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D4_4_consent_note.ipynb) | voice (length of the disclosure) |

## Models and keys

Copy `.env.example` to `.env`, set `HT_PROVIDER=hosted` and add the free keys you have. Only free tiers are used.

| Kind | Default model | Served by | Key |
|---|---|---|---|
| Vision, open-weight | `google/gemma-4-26b-a4b-it:free` | OpenRouter | `OPENROUTER_API_KEY` |
| Vision, hosted comparison | `nvidia/nemotron-3.5-super-vl:free` | OpenRouter | `OPENROUTER_API_KEY` |
| Speech recognition A and B | `whisper-large-v3`, `whisper-large-v3-turbo` | Groq | `GROQ_API_KEY` |
| Voice, Arabic and English | `canopylabs/orpheus-arabic-saudi`, `canopylabs/orpheus-v1-english` | Groq | `GROQ_API_KEY` |

Free model lists change: if a default is withdrawn, set another free model in `.env` (`HT_VLM_OPEN`, `HT_VLM_HOSTED`,
`HT_ASR_A`, `HT_ASR_B`, `HT_TTS_AR`, `HT_TTS_EN`). A result that differs from the stand-in is not an error: each
check that depends on a model reports what your model did instead of failing.

The recognisers of Day 2 need audio. `uv run python make_audio.py` (with a Groq key) synthesises the 50 clips into
`data/audio/`, which git ignores. The audio is one synthetic voice, so it does not carry dialect differences: the
dialect slices of Lab 2.3 always use the recorded transcripts.

## Running fast

`HT_QUICK=1` runs every notebook on a small sample (a few photos, clips or turns) for a check in about a minute.
Results in quick mode are not the ones on the slides.

## Files

| File | What it is |
|---|---|
| `trails.py` | Shared helpers: photos, the vision stand-in, box matching, transcripts, normalisation, WER, Wilson intervals, synthesis |
| `rahhal.py` | The booking line: the store, the scripted agent with its modelled clock, the simulated callers |
| `prepare_data.py` | Writes everything in `data/` from seed 408 |
| `make_audio.py` | Optional: synthesises the clips with a Groq key |
| `data/` | Photos with reference fields and boxes, clips with recorded transcripts, traces, scripted calls, caller cards, the test pool, pipeline measurements, transcript samples |
| `solutions/` | Every notebook completed and run; `answer_key.md` lists the key results |

The notebooks are generated from the percent-format sources in `_src/` by `_tools/py2nb.py`
(`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions. Edit the sources, not the notebooks.
