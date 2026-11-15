# Multimodal and Speech Systems Engineering: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository.
- Locally: clone the repository, then open the notebooks in `labs/` with Jupyter.

| Unit | Session | Notebook |
|---|---|---|
| Day 1 | Session 1 · How a vision-language model sees | [`D1_1_measure_tokens_latency.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D1_1_measure_tokens_latency.ipynb) |
| Day 1 | Session 2 · Structured extraction from photos | [`D1_2_extract_validated_incident.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D1_2_extract_validated_incident.ipynb) |
| Day 1 | Session 3 · Grounding answers in pixels | [`D1_3_score_returned_boxes.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D1_3_score_returned_boxes.ipynb) |
| Day 1 | Session 4 · Arabic text and hidden instructions | [`D1_4_read_arabic_signage.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D1_4_read_arabic_signage.ipynb) |
| Day 2 | Session 1 · From waveform to text | [`D2_1_run_two_open.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D2_1_run_two_open.ipynb) |
| Day 2 | Session 2 · Normalisation decides the error rate | [`D2_2_apply_arabic_normalisation.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D2_2_apply_arabic_normalisation.ipynb) |
| Day 2 | Session 3 · Dialects and code-switching | [`D2_3_slice_error_rates.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D2_3_slice_error_rates.ipynb) |
| Day 2 | Session 4 · Streaming and silence | [`D2_4_stream_recognition_voice.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D2_4_stream_recognition_voice.ipynb) |
| Day 3 | Session 1 · Synthesis and read-back | [`D3_1_synthesise_booking_confirmations.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D3_1_synthesise_booking_confirmations.ipynb) |
| Day 3 | Session 2 · Cascaded versus speech-to-speech | [`D3_2_trace_per_stage.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D3_2_trace_per_stage.ipynb) |
| Day 3 | Session 3 · Turn-taking and interruption | [`D3_3_tune_end_turn.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D3_3_tune_end_turn.ipynb) |
| Day 3 | Session 4 · Tool calls during speech | [`D3_4_add_booking_tool.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D3_4_add_booking_tool.ipynb) |
| Day 4 | Session 1 · Multimodal test sets | [`D4_1_build_60_item.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D4_1_build_60_item.ipynb) |
| Day 4 | Session 2 · Simulated callers | [`D4_2_run_20_simulated.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D4_2_run_20_simulated.ipynb) |
| Day 4 | Session 3 · Choosing by quality, latency and cost | [`D4_3_compare_open_weight.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D4_3_compare_open_weight.ipynb) |
| Day 4 | Session 4 · Voice, faces and consent | [`D4_4_write_data_handling.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ae-408/blob/main/labs/D4_4_write_data_handling.ipynb) |

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.
