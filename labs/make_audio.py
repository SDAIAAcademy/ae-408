# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
"""Synthesise the 50 clips of data/clips.jsonl with a hosted open-weight voice, so that Lab 2.1 can send real audio
to the hosted recognisers instead of replaying the recorded transcripts.

    GROQ_API_KEY=... uv run make_audio.py            # all clips into data/audio/
    GROQ_API_KEY=... uv run make_audio.py --limit 5  # the first five

Every voice is synthetic (HT_TTS_AR, by default the Saudi Arabic Orpheus voice on Groq). Clips marked "telephone"
are band-limited to 8 kHz and back, as a telephone line would. Synthetic speech in one voice does not carry real
dialect differences: the dialect slices of Lab 2.3 stay meaningful only on the recorded transcripts or on a public
corpus whose terms you have accepted (Mozilla Common Voice, downloaded by you from its official page). The free
plan's daily request limit for this voice is small: check your limits page before running all 50.
"""

from __future__ import annotations

import io
import json
import os
import sys
import time
import wave
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parent
OUT = LABS / "data" / "audio"


def to_telephone(samples: np.ndarray, rate: int) -> np.ndarray:
    """Down to 8 kHz and back up: a crude telephone band."""
    step = max(1, rate // 8000)
    low = samples[::step]
    return np.repeat(low, step)[: len(samples)]


def main(limit: int | None = None):
    try:
        from dotenv import load_dotenv
        load_dotenv(LABS / ".env")
    except Exception:
        pass
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        sys.exit("GROQ_API_KEY is not set: nothing to do (the labs replay the recorded transcripts without it)")
    from openai import OpenAI
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
    model = os.environ.get("HT_TTS_AR", "canopylabs/orpheus-arabic-saudi")
    voice = os.environ.get("HT_TTS_VOICE_AR")
    OUT.mkdir(parents=True, exist_ok=True)
    clips = [json.loads(l) for l in (LABS / "data" / "clips.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    for c in clips[:limit]:
        path = OUT / f"{c['clip_id']}.wav"
        if path.exists():
            continue
        kwargs = {"model": model, "input": c["reference"], "response_format": "wav"}
        if voice:
            kwargs["voice"] = voice
        for attempt in range(4):
            try:
                audio = client.audio.speech.create(**kwargs).read()
                break
            except Exception as e:  # rate limits on a free plan: wait and retry
                if attempt == 3:
                    raise
                print("retrying after", type(e).__name__)
                time.sleep(10 * (attempt + 1))
        with wave.open(io.BytesIO(audio)) as w:
            rate, width, ch = w.getframerate(), w.getsampwidth(), w.getnchannels()
            frames = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        if c["channel"] == "telephone":
            frames = to_telephone(frames, rate).astype(np.int16)
        with wave.open(str(path), "wb") as w:
            w.setnchannels(ch)
            w.setsampwidth(width)
            w.setframerate(rate)
            w.writeframes(frames.tobytes())
        print("wrote", path.name)


if __name__ == "__main__":
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    main(lim)
