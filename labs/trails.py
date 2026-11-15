"""Helpers for the AE-408 labs: the Heritage Trails Authority case.

    import trails as U

Two paths to every model the labs use:

- Hosted (HT_PROVIDER=hosted, with OPENROUTER_API_KEY for vision and GROQ_API_KEY for speech):
  free hosted open-weight models through OpenAI-style endpoints.
- The scripted stand-in (the default, no network): deterministic answers in the same formats,
  with behaviour set by fixed rules and a seed. It reads the `task` argument, where a real model
  reads the prompt. Numbers from a stand-in run show how the pipeline and the measurements behave,
  not how a real model performs. Every rule it follows is written below, so a trainer can explain it.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import math
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"

try:  # a local .env is optional
    from dotenv import load_dotenv
    load_dotenv(LABS / ".env")
except Exception:
    pass

QUICK = os.environ.get("HT_QUICK", "0") == "1"
PROVIDER = os.environ.get("HT_PROVIDER", "scripted")
VLM_MODELS = {"open": os.environ.get("HT_VLM_OPEN", "google/gemma-4-26b-a4b-it:free"),
              "hosted": os.environ.get("HT_VLM_HOSTED", "nvidia/nemotron-3.5-super-vl:free")}
ASR_MODELS = {"A": os.environ.get("HT_ASR_A", "whisper-large-v3"),
              "B": os.environ.get("HT_ASR_B", "whisper-large-v3-turbo")}
TTS_MODELS = {"ar": os.environ.get("HT_TTS_AR", "canopylabs/orpheus-arabic-saudi"),
              "en": os.environ.get("HT_TTS_EN", "canopylabs/orpheus-v1-english")}
TODAY = "2026-12-01"
BUDGET_TTFA_MS = 1200  # the line's budget for time to first audio, owned by Fayyad Al-Ghamdi

SITES = {
    "HT-01": ("Red Rock Path", "درب الصخور الحمراء"), "HT-02": ("Sidr Valley Trail", "مسار وادي السدر"),
    "HT-03": ("Palm Fort", "قلعة النخيل"), "HT-04": ("Old Well Walk", "ممشى البئر القديمة"),
    "HT-05": ("Falcon Ridge", "حافة الصقر"), "HT-06": ("Clay Village", "القرية الطينية"),
    "HT-07": ("Inscriptions Gorge", "شعب النقوش"), "HT-08": ("Acacia Plain", "سهل الطلح"),
    "HT-09": ("Watchtower Hill", "تل المرقب"), "HT-10": ("Spring Garden", "بستان العين"),
    "HT-11": ("Caravan Road", "طريق القوافل"), "HT-12": ("Juniper Terraces", "مدرجات العرعر"),
}


def pick(full, quick):
    """The small value in quick mode (HT_QUICK=1), the full one otherwise."""
    return quick if QUICK else full


def hosted(kind: str = "vision") -> bool:
    """True when the hosted path is on and the key for this kind of model is present."""
    if PROVIDER != "hosted":
        return False
    key = "OPENROUTER_API_KEY" if kind == "vision" else "GROQ_API_KEY"
    return bool(os.environ.get(key))


def check(ok: bool, what: str, model: bool = False):
    """A self-check. model=True marks a check on what a model did, not on your code: with a
    hosted model it prints a note instead of stopping the notebook."""
    if ok:
        print("✅ " + what)
    elif model and PROVIDER == "hosted":
        print("ℹ️ not so with this model: " + what + " (the stand-in run showed it; note what yours did)")
    else:
        raise AssertionError("❌ " + what)


def artifacts(lab: str) -> Path:
    """The folder a lab writes its outputs to (git ignores artifacts/)."""
    p = LABS / "artifacts" / lab
    p.mkdir(parents=True, exist_ok=True)
    return p


def _h(*parts) -> float:
    """A stable number in [0, 1) from any values: the stand-in's dice."""
    s = "|".join(str(p) for p in parts).encode("utf-8")
    return int(hashlib.sha256(s).hexdigest()[:12], 16) / 16 ** 12


def jsonl(name: str) -> list[dict]:
    return [json.loads(l) for l in (DATA / name).read_text(encoding="utf-8").splitlines() if l.strip()]


# ------------------------------------------------------------------ photos

def photo_refs() -> list[dict]:
    """The 60 photos' reference fields, boxes and faces (data/photos/refs.jsonl)."""
    return jsonl("photos/refs.jsonl")


REFS = {r["photo_id"]: r for r in photo_refs()}


def photo(photo_id: str, width: int = 640):
    """The photo as a Pillow image, resized to `width` pixels wide (aspect kept)."""
    from PIL import Image
    img = Image.open(DATA / "photos" / f"{photo_id}.png").convert("RGB")
    if width != img.width:
        img = img.resize((width, round(img.height * width / img.width)), Image.Resampling.LANCZOS)
    return img


def data_url(img) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@dataclass
class Reply:
    text: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    model: str
    extra: dict = field(default_factory=dict)


VLM_PROFILES = {
    # base latency, per input token, per output token (ms); reading threshold in pixels of text
    # height; error rates. A modelling choice for the stand-in, not a measurement of any model.
    "open": {"base": 280, "per_in": 0.55, "per_out": 18, "read_px": 9.5, "sev": 0.17, "type": 0.12,
             "box_sd": 0.08, "bad_box": 0.10, "miss": 0.08, "invent": 0.34, "people": 0.10, "fmt": 0.16},
    "hosted": {"base": 650, "per_in": 0.35, "per_out": 12, "read_px": 8.0, "sev": 0.07, "type": 0.05,
               "box_sd": 0.04, "bad_box": 0.04, "miss": 0.03, "invent": 0.10, "people": 0.05, "fmt": 0.04},
}
CONFUSE = {"0": "8", "8": "0", "1": "7", "7": "1", "6": "5", "5": "6", "3": "8", "2": "7", "9": "8", "4": "1"}
TYPE_CONFUSE = {"damaged_sign": "none", "graffiti": "none", "broken_fence": "blocked_path",
                "blocked_path": "broken_fence", "litter": "none", "rockfall": "blocked_path", "none": "litter"}
SEV_ORDER = ["none", "low", "medium", "high"]


def image_tokens(width: int, height: int) -> int:
    """The stand-in's rule: one visual token per 32 by 32 pixel patch. A modelling choice; a real
    endpoint reports its own count in usage.prompt_tokens."""
    return math.ceil(width / 32) * math.ceil(height / 32)


def _read_marker(ref, width, prof, model):
    code = ref["fields"]["site_code"]
    if code is None:
        return None
    eff = ref["marker_px"] * width / 640
    if eff >= prof["read_px"] or (eff >= prof["read_px"] * 0.75 and _h("mk", ref["photo_id"], width, model) < 0.4):
        return code
    d = code[-1]
    return code[:-1] + CONFUSE.get(d, d)


AR_OCR_SWAPS = [("ة", "ه"), ("ى", "ي"), ("ب", "ت"), ("ن", "ب"), ("ف", "ق"), ("ج", "ح"), ("ذ", "د"), ("ش", "س")]


def _read_sign(ref, width, model):
    text = ref["fields"]["sign_text"]
    if text is None:
        return None
    if ref["injected"]:
        return text
    eff = ref["sign_px"] * width / 640
    n_err = 0 if eff >= 24 else 1 if eff >= 20 else 3 if eff >= 16 else 6
    if model == "hosted":
        n_err = max(0, n_err - 1)
    chars = list(text)
    for k in range(n_err):
        u = _h("ocr", ref["photo_id"], width, model, k)
        cands = [i for i, ch in enumerate(chars) if any(ch == a for a, _ in AR_OCR_SWAPS)]
        if cands and u < 0.75:
            i = cands[int(u / 0.75 * len(cands)) % len(cands)]
            chars[i] = dict(AR_OCR_SWAPS)[chars[i]]
        else:
            i = int(u * len(chars)) % len(chars)
            if chars[i] != " ":
                del chars[i]
    return "".join(chars)


def _fields(ref, width, model, prof, mitigated, allow_unknown):
    pid = ref["photo_id"]
    f = dict(ref["fields"])
    if _h("type", pid, model) < prof["type"]:
        f["incident_type"] = TYPE_CONFUSE[f["incident_type"]]
    if _h("sev", pid, model) < prof["sev"]:
        i = SEV_ORDER.index(f["severity"])
        f["severity"] = SEV_ORDER[min(3, i + 1) if i < 2 else i - 1]
    if _h("ppl", pid, model) < prof["people"]:
        f["people_visible"] = max(0, f["people_visible"] + (1 if _h("ppl2", pid) < 0.5 else -1))
    code = _read_marker(ref, width, prof, model)
    if allow_unknown and code is not None and code != ref["fields"]["site_code"]:
        code = None  # an unsure reading becomes "unknown" when the schema allows it
    f["site_code"] = code
    f["sign_text"] = _read_sign(ref, width, model)
    inj = ref["injected"]
    follows = (inj == "ar" and model == "open") if mitigated else (inj is not None and (model == "open" or inj == "en"))
    if follows:
        f["severity"], f["hazard_to_visitors"] = "low", False
    return f


def _format(obj: dict, pid: str, model: str, prof: dict, repaired: bool) -> str:
    text = json.dumps(obj, ensure_ascii=False)
    if repaired:
        return text
    u = _h("fmt", pid, model)
    if u < prof["fmt"] * 0.6:
        return "Here is the record:\n```json\n" + text + "\n```"
    if u < prof["fmt"]:
        bad = dict(obj)
        bad["incident_type"] = {"rockfall": "fallen rocks", "litter": "rubbish"}.get(obj["incident_type"], obj["incident_type"].title())
        bad["severity"] = obj["severity"].upper()
        return json.dumps(bad, ensure_ascii=False)
    return text


def _boxes(ref, model, prof):
    pid = ref["photo_id"]
    out = []
    for k, o in enumerate(ref["objects"]):
        if _h("miss", pid, model, k) < prof["miss"]:
            continue
        x0, y0, x1, y1 = o["box"]
        w, h = x1 - x0, y1 - y0
        if _h("bad", pid, model, k) < prof["bad_box"]:
            dx, dy = 0.7 * w, 0.6 * h  # a box beside the object
        else:
            dx = (_h("dx", pid, model, k) - 0.5) * 2 * prof["box_sd"] * w
            dy = (_h("dy", pid, model, k) - 0.5) * 2 * prof["box_sd"] * h
        out.append({"label": o["label"], "box": [round(x0 + dx), round(y0 + dy), round(x1 + dx), round(y1 + dy)]})
    if ref["fields"]["incident_type"] == "none" and _h("inv", pid, model) < prof["invent"]:
        x = 250 + int(_h("ix", pid) * 150)
        out.append({"label": "litter", "box": [x, 380, x + 14, 400]})
    return out


def _probe(ref, label, model, prof):
    present = [o for o in ref["objects"] if o["label"] == label]
    if present:
        return {"present": True, "box": present[0]["box"]}
    clean = ref["fields"]["incident_type"] == "none"
    if _h("probe", ref["photo_id"], label, model) < prof["invent"] * (1.0 if clean else 0.4):
        x = 230 + int(_h("px", ref["photo_id"]) * 200)
        return {"present": True, "box": [x, 360, x + 16, 384]}
    return {"present": False, "box": None}


def _scripted_vlm(photo_id, prompt, model, width, system, history, task):
    ref = REFS[photo_id]
    prof = VLM_PROFILES[model]
    repaired = any("invalid" in (m.get("content") or "").lower() for m in history or [] if m.get("role") == "user")
    sys_l = (system or "").lower()
    mitigated = "data, not instructions" in sys_l or "not instructions" in sys_l
    allow_unknown = "unknown" in (prompt + " " + sys_l).lower()
    if task == "marker":
        text = _read_marker(ref, width, prof, model) or "no marker"
    elif task == "extract":
        text = _format(_fields(ref, width, model, prof, mitigated, allow_unknown), photo_id, model, prof, repaired)
    elif task == "objects":
        text = json.dumps(_boxes(ref, model, prof))
    elif task.startswith("probe:"):
        text = json.dumps(_probe(ref, task.split(":", 1)[1], model, prof))
    elif task == "read_sign":
        text = _read_sign(ref, width, model) or ""
    else:
        raise ValueError("unknown task " + task)
    height = round(480 * width / 640)
    p_tok = image_tokens(width, height) + math.ceil(len(prompt + (system or "")) / 4) + 8
    c_tok = math.ceil(len(text) / 3.5)
    lat = prof["base"] + prof["per_in"] * p_tok + prof["per_out"] * c_tok + 60 * _h("lat", photo_id, width, model, task)
    return Reply(text, p_tok, c_tok, round(lat, 1), "stand-in-" + model)


def _hosted_vlm(photo_id, prompt, model, width, system, history):
    from openai import OpenAI
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": [{"type": "text", "text": prompt},
                                             {"type": "image_url", "image_url": {"url": data_url(photo(photo_id, width))}}]})
    msgs += history or []
    for attempt in range(4):
        try:
            t0 = time.perf_counter()
            r = client.chat.completions.create(model=VLM_MODELS[model], messages=msgs, temperature=0)
            lat = (time.perf_counter() - t0) * 1000
            u = r.usage
            return Reply(r.choices[0].message.content or "", u.prompt_tokens if u else 0, u.completion_tokens if u else 0,
                         round(lat, 1), VLM_MODELS[model])
        except Exception as e:  # a busy free model answers 429: wait and retry
            if attempt == 3:
                raise
            print("retrying after", type(e).__name__)
            time.sleep(4 * (attempt + 1))


def vlm(photo_id: str, prompt: str, *, model: str = "open", width: int = 640, system: str | None = None,
        history: list | None = None, task: str = "extract") -> Reply:
    """Ask a vision-language model about one photo. model is "open" or "hosted" (VLM_MODELS).
    history holds later turns (for a repair). task tells the stand-in what is asked: "marker",
    "extract", "objects", "probe:<label>" or "read_sign"; a hosted model reads the prompt instead."""
    if hosted("vision"):
        return _hosted_vlm(photo_id, prompt, model, width, system, history)
    return _scripted_vlm(photo_id, prompt, model, width, system, history, task)


def iou(a, b) -> float:
    """Intersection over union of two boxes [x0, y0, x1, y1] (the reference version)."""
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


# ------------------------------------------------------------------ speech: clips and error rates

def clips() -> list[dict]:
    """The 50 clips: dialect, channel, code-switching, reference, and two recorded transcripts."""
    return jsonl("clips.jsonl")


def transcribe(clip: dict, recogniser: str = "A") -> Reply:
    """Transcribe one clip with recogniser A or B (ASR_MODELS). Hosted: sends data/audio/<clip>.wav
    to the endpoint when that file exists (make_audio.py writes it). Stand-in: replays the
    recorded transcript, with a latency of 0.06 s per second of audio plus 180 ms."""
    model = ASR_MODELS[recogniser]
    wav = DATA / "audio" / f"{clip['clip_id']}.wav"
    if hosted("speech") and wav.exists():
        from openai import OpenAI
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"])
        t0 = time.perf_counter()
        with open(wav, "rb") as fh:
            r = client.audio.transcriptions.create(model=model, file=fh, language="ar")
        return Reply(r.text, 0, 0, round((time.perf_counter() - t0) * 1000, 1), model)
    key = "whisper-large-v3" if recogniser == "A" else "whisper-large-v3-turbo"
    return Reply(clip[key], 0, 0, round(180 + 60 * clip["seconds"] + 40 * _h("asr", clip["clip_id"], recogniser), 1),
                 "recorded-" + key)


DIACRITICS = re.compile("[ؐ-ًؚ-ٰٟۖ-ۭ]")
PUNCT = re.compile(r"[^\w\s]", re.UNICODE)


def normalise(text: str, rules: str = "full") -> str:
    """The course's reference Arabic normalisation (Lab 2.2 builds its own).
    "none": only whitespace and case. "light": also diacritics, tatweel, punctuation, digits.
    "full": also alef variants to alef, alef maqsura to ya, ta marbuta to ha."""
    t = unicodedata.normalize("NFKC", text).lower()
    if rules in ("light", "full"):
        t = DIACRITICS.sub("", t).replace("ـ", "")
        t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
        t = PUNCT.sub(" ", t)
    if rules == "full":
        t = re.sub("[أإآٱ]", "ا", t).replace("ى", "ي").replace("ة", "ه")
    return " ".join(t.split())


def wer(refs: list[str], hyps: list[str], rules: str = "full") -> float:
    """Corpus word error rate with jiwer after normalise(rules)."""
    import jiwer
    return jiwer.wer([normalise(r, rules) for r in refs], [normalise(h, rules) for h in hyps])


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion k/n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


# ------------------------------------------------------------------ streaming audio (Lab 2.4)

SR = 16000
UTTERANCES = [  # (start s, end s, text): the synthetic call's speech
    (1.0, 3.4, "السلام عليكم أبي أحجز جولة"),
    (5.2, 7.0, "في قلعة النخيل"),
    (12.5, 14.8, "يوم الخميس الجاي"),
    (16.0, 17.6, "لعدد خمسة أشخاص"),
    (24.0, 26.2, "واسمي على الحجز وداد"),
    (33.0, 34.6, "شكرا مع السلامة"),
]
HUM = (19.0, 22.5)
HALLUCINATIONS = ["شكرا للمشاهدة", "اشتركوا في القناة", "Thank you.", "موسيقى", "you"]


def synthetic_call(seconds: float = 38.0, seed: int = 408):
    """A synthetic call at 16 kHz: speech-like bursts (a voiced tone with a syllable envelope and
    noise) at the times in UTTERANCES, quiet line noise elsewhere, and a hum from HUM[0] to HUM[1].
    No voice is recorded or imitated. Returns (samples as float32, sample rate)."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = rng.normal(0, 0.003, n)
    for s, e, _ in UTTERANCES:
        i0, i1 = int(s * SR), int(e * SR)
        tt = t[i0:i1]
        f0 = 140 + 30 * np.sin(2 * np.pi * 0.7 * tt)
        voiced = sum(np.sin(2 * np.pi * k * f0 * tt) / k for k in range(1, 6))
        env = 0.5 * (1 + np.sin(2 * np.pi * 4.2 * tt - np.pi / 2)) ** 1.5
        x[i0:i1] += 0.18 * env * voiced + 0.02 * env * rng.normal(0, 1, i1 - i0)
    h0, h1 = int(HUM[0] * SR), int(HUM[1] * SR)
    x[h0:h1] += 0.012 * np.sin(2 * np.pi * 50 * t[h0:h1]) + 0.006 * np.sin(2 * np.pi * 150 * t[h0:h1])
    return x.astype(np.float32), SR


def recognise_segment(start_s: float, end_s: float) -> dict:
    """The stand-in streaming recogniser on one segment of synthetic_call(): returns
    {"text", "no_speech_prob", "latency_ms"}. On speech it returns the words of the utterances the
    segment covers. On a segment without speech it writes a phrase anyway, as Whisper-family
    recognisers are reported to do around long non-vocal stretches (Koenecke et al., 2024),
    with a no-speech probability that is usually high but not always (on the hum it is 0.42)."""
    words = []
    covered = 0.0
    for s, e, text in UTTERANCES:
        ov = max(0.0, min(e, end_s) - max(s, start_s))
        if ov > 0:
            covered += ov
            frac = ov / (e - s)
            toks = text.split()
            if frac > 0.85:
                words += toks
            elif frac > 0.25:  # a cut utterance loses words at the cut
                k = max(1, round(len(toks) * frac))
                words += toks[:k] if start_s <= s else toks[-k:]
    lat = round(150 + 45 * (end_s - start_s) + 30 * _h("seg", round(start_s, 2)), 1)
    if words:
        return {"text": " ".join(words), "no_speech_prob": round(0.02 + 0.05 * _h("nsp", start_s), 3), "latency_ms": lat}
    on_hum = max(0.0, min(HUM[1], end_s) - max(HUM[0], start_s)) > 0.3
    u = _h("hall", round(start_s, 1), round(end_s, 1))
    if on_hum:
        return {"text": HALLUCINATIONS[int(u * 3)], "no_speech_prob": 0.42, "latency_ms": lat}
    if u < 0.7:
        return {"text": HALLUCINATIONS[int(u / 0.7 * len(HALLUCINATIONS)) % len(HALLUCINATIONS)],
                "no_speech_prob": round(0.62 + 0.3 * _h("nsp2", start_s), 3), "latency_ms": lat}
    return {"text": "", "no_speech_prob": 0.97, "latency_ms": lat}


# ------------------------------------------------------------------ synthesis (Lab 3.1)

def synthesise(text: str, lang: str = "ar", out: Path | None = None) -> Reply:
    """Speak `text`. Hosted: the open-weight voice on Groq (TTS_MODELS), the WAV written to `out`
    and its true length measured. Stand-in: no audio; the length is estimated at 12.5 characters a
    second for Arabic and 14 for English, plus 0.25 s for each comma or full stop."""
    if hosted("speech"):
        import wave
        from openai import OpenAI
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"])
        voice = os.environ.get("HT_TTS_VOICE_" + lang.upper(), "")
        t0 = time.perf_counter()
        kwargs = {"model": TTS_MODELS[lang], "input": text, "response_format": "wav"}
        if voice:
            kwargs["voice"] = voice
        r = client.audio.speech.create(**kwargs)
        lat = (time.perf_counter() - t0) * 1000
        out = out or artifacts("tts") / f"say_{abs(hash(text)) % 10**8}.wav"
        r.write_to_file(out)
        with wave.open(str(out)) as w:
            dur = w.getnframes() / w.getframerate()
        return Reply(text, 0, 0, round(lat, 1), TTS_MODELS[lang], {"seconds": round(dur, 2), "wav": str(out)})
    rate = 12.5 if lang == "ar" else 14.0
    pauses = text.count(",") + text.count("،") + text.count(".")
    dur = len(text) / rate + 0.25 * pauses
    return Reply(text, 0, 0, round(120 + 8 * len(text) ** 0.5, 1), "stand-in-tts", {"seconds": round(dur, 2)})


# ------------------------------------------------------------------ traces and percentiles

def pct(values, q: float) -> float:
    """The q-th percentile (0 to 100) with linear interpolation."""
    return float(np.percentile(np.asarray(values, dtype=float), q))


def match_boxes(pred, ref, thr=0.5):
    """Greedy same-label matching, best IoU first (the reference version of Lab 1.3's match).
    Returns (hits, number of predictions, number of references)."""
    pairs = sorted(((iou(p["box"], r["box"]), i, j) for i, p in enumerate(pred) for j, r in enumerate(ref)
                    if p["label"] == r["label"]), reverse=True)
    used_p, used_r, hits = set(), set(), 0
    for v, i, j in pairs:
        if v < thr:
            break
        if i not in used_p and j not in used_r:
            used_p.add(i)
            used_r.add(j)
            hits += 1
    return hits, len(pred), len(ref)
