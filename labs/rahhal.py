"""Rahhal (رحّال), the reference booking line of the AE-408 labs, and the pieces around it.

    import rahhal as R

- `Store`: the booking store, with a capacity per site and day.
- `parse_slots(text)`: the stand-in language model's understanding of a caller turn (site, date, party size, yes/no).
- `Rahhal`: a cascaded voice agent over text turns. Its policy is scripted (deterministic), its clock is modelled
  per stage: endpointing, recognition, the model's first token, a tool call, synthesis and the network. A trace of
  every turn is kept in `agent.trace`.
- `Caller` and `run_call`: simulated callers from the cards of data/callers.jsonl (Lab 4.2).
- `hear(text, dialect, behaviour, k)`: the stand-in recogniser for simulated calls, with errors by dialect and behaviour.

Nothing here calls a model: every lab that uses this module runs offline. The timing constants are modelling
choices for the case study, not measurements of any product.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"

SITES = {
    "HT-01": ("Red Rock Path", "درب الصخور الحمراء"), "HT-02": ("Sidr Valley Trail", "مسار وادي السدر"),
    "HT-03": ("Palm Fort", "قلعة النخيل"), "HT-04": ("Old Well Walk", "ممشى البئر القديمة"),
    "HT-05": ("Falcon Ridge", "حافة الصقر"), "HT-06": ("Clay Village", "القرية الطينية"),
    "HT-07": ("Inscriptions Gorge", "شعب النقوش"), "HT-08": ("Acacia Plain", "سهل الطلح"),
    "HT-09": ("Watchtower Hill", "تل المرقب"), "HT-10": ("Spring Garden", "بستان العين"),
    "HT-11": ("Caravan Road", "طريق القوافل"), "HT-12": ("Juniper Terraces", "مدرجات العرعر"),
}
TODAY = dt.date(2026, 12, 1)
CAPACITY = 20  # visitors per site per day

# The modelled clock of one agent turn, in milliseconds (the case study's measurements, not a product's)
STAGES = {"endpoint": 500, "asr": 150, "llm_first_token": 280, "tts_first_audio": 130, "network": 60}
TOOL_MS = {"book_visit": 900, "check_availability": 350}


def _h(*parts) -> float:
    s = "|".join(str(p) for p in parts).encode("utf-8")
    return int(hashlib.sha256(s).hexdigest()[:12], 16) / 16 ** 12


class ToolError(Exception):
    """An error the agent can say back to the caller."""


@dataclass
class Store:
    bookings: list = field(default_factory=list)
    calls: int = 0

    def booked(self, site_code: str, date: str) -> int:
        return sum(b["party_size"] for b in self.bookings if b["site_code"] == site_code and b["date"] == date)

    def add(self, site_code: str, date: str, party_size: int, name: str, key: str | None = None) -> str:
        self.calls += 1
        if key:
            for b in self.bookings:
                if b.get("key") == key:
                    return b["ref"]
        ref = f"HTB-{1000 + len(self.bookings) * 7 + int(_h(site_code, date, name) * 900):04d}"
        self.bookings.append({"ref": ref, "site_code": site_code, "date": date, "party_size": party_size,
                              "name": name, "key": key})
        return ref


# ------------------------------------------------------------------ understanding a caller turn

EN_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
          "ten": 10, "eleven": 11, "twelve": 12}
AR_NUM = {"واحد": 1, "اثنين": 2, "ثلاثة": 3, "أربعة": 4, "اربعة": 4, "خمسة": 5, "ستة": 6, "سبعة": 7, "ثمانية": 8,
          "تسعة": 9, "عشرة": 10, "احدعش": 11, "اثنعش": 12}
YES = re.compile(r"\b(yes|yeah|correct|right|book it)\b|(?:^|\s)(نعم|ايه|إيه|أيوه|صح|تمام|احجز)(?=[\s،,.]|$)", re.I)
NO = re.compile(r"\b(no|not|wrong)\b|(?:^|\s)(لا|مو|غلط)(?=[\s،,.]|$)", re.I)


def parse_slots(text: str) -> dict:
    """What the scripted model understands from one caller turn: any of site_code, date, party_size, yes, no."""
    out = {}
    t = text.replace("٠", "0").replace("١", "1").replace("٢", "2").replace("٣", "3").replace("٤", "4") \
        .replace("٥", "5").replace("٦", "6").replace("٧", "7").replace("٨", "8").replace("٩", "9")
    for code, (en, ar) in SITES.items():
        if en.lower() in t.lower() or ar in t:
            out["site_code"] = code
    m = re.search(r"(20\d\d)-(\d\d)-(\d\d)", t)
    if m:
        out["date"] = m.group(0)
    m = re.search(r"(?:for|لعدد|عددنا|party of)\s+(\d{1,2}|\w+)", t, re.I)
    if m:
        v = m.group(1)
        n = int(v) if v.isdigit() else EN_NUM.get(v.lower(), AR_NUM.get(v))
        if n:
            out["party_size"] = n
    if YES.search(t):
        out["yes"] = True
    if NO.search(t):
        out["no"] = True
    return out


def is_arabic(text: str) -> bool:
    return any("؀" <= ch <= "ۿ" for ch in text)


# ------------------------------------------------------------------ the agent

def readback(slots: dict, lang: str) -> str:
    en, ar = SITES[slots["site_code"]]
    if lang == "ar":
        return f"للتأكيد: {ar}، يوم {slots['date']}، لعدد {slots['party_size']}. هل أحجز؟"
    return f"To confirm: {en}, on {slots['date']}, for {slots['party_size']}. Shall I book?"


ASK = {"site_code": ("Which site would you like to visit?", "أي موقع تحب تزور؟"),
       "date": ("On which date?", "في أي تاريخ؟"),
       "party_size": ("For how many people?", "لعدد كم شخص؟")}


@dataclass
class Rahhal:
    """A cascaded booking agent over text turns.

    book_tool: a function (site_code, date, party_size, name) -> booking reference, or None for no tool.
    policy: "book_when_full" books as soon as the three slots are filled (the provided starting point of Lab 3.4);
            "confirm_then_book" reads the slots back and books only after a yes; a change resets the confirmation.
    filler: say a short line while a slow tool runs, so the caller does not hear silence.
    stale_confirmation: the planted bug of Lab 4.2: after a correction, the tool is called with the slots the caller
            first heard, not the corrected ones.
    """
    book_tool: object = None
    policy: str = "confirm_then_book"
    filler: bool = False
    stale_confirmation: bool = False
    name: str = "caller"
    slots: dict = field(default_factory=dict)
    stage: str = "collect"
    heard_slots: dict = field(default_factory=dict)
    booked_ref: str | None = None
    trace: list = field(default_factory=list)
    lang: str = "en"

    def _clock(self, turn: int, tool: str | None) -> dict:
        st = dict(STAGES)
        st["llm_first_token"] += int(120 * _h("llm", turn, self.name))
        ev = {"turn": turn, **st, "tool_ms": 0, "filler": False}
        speak_after = sum(st.values())
        if tool:
            ev["tool_ms"] = TOOL_MS[tool]
            if self.filler:
                ev["filler"] = True  # the filler line is spoken at the normal time; the result follows the tool
            else:
                speak_after += TOOL_MS[tool]
        ev["ttfa_ms"] = speak_after
        return ev

    def respond(self, caller_text: str) -> str:
        turn = len(self.trace) + 1
        if turn == 1:
            self.lang = "ar" if is_arabic(caller_text) else "en"
        got = parse_slots(caller_text)
        tool = None
        changed = any(k in got and got[k] != self.slots.get(k) for k in ("site_code", "date", "party_size"))
        for k in ("site_code", "date", "party_size"):
            if k in got:
                self.slots[k] = got[k]
        missing = [k for k in ("site_code", "date", "party_size") if k not in self.slots]
        ar = self.lang == "ar"
        if self.booked_ref:
            say = "شكرا، مع السلامة." if ar else "Thank you, goodbye."
        elif missing:
            say = ASK[missing[0]][1 if ar else 0]
        elif self.policy == "book_when_full":
            tool = "book_visit"
            say = self._book(self.slots)
        elif self.stage == "confirm" and got.get("yes") and not got.get("no") and not changed:
            tool = "book_visit"
            use = self.heard_slots if self.stale_confirmation else self.slots
            say = self._book(use)
        else:
            if self.stage != "confirm" or not self.heard_slots:
                self.heard_slots = dict(self.slots)
            elif not self.stale_confirmation:
                self.heard_slots = dict(self.slots)
            self.stage = "confirm"
            say = readback(self.slots, self.lang)
        ev = self._clock(turn, tool)
        ev.update({"caller": caller_text, "agent": say, "tool": tool})
        self.trace.append(ev)
        return say

    def _book(self, slots: dict) -> str:
        ar = self.lang == "ar"
        if self.book_tool is None:
            return "عذرا، لا أستطيع الحجز الآن." if ar else "Sorry, I cannot book right now."
        try:
            self.booked_ref = self.book_tool(slots["site_code"], slots["date"], slots["party_size"], self.name)
        except ToolError as e:
            self.stage = "collect"
            self.slots.pop("date", None)
            return (f"عذرا: {e}. أي تاريخ آخر؟" if ar else f"Sorry: {e}. Which other date?")
        self.stage = "done"
        return (f"تم الحجز، رقمه {self.booked_ref}." if ar else f"Booked. Your reference is {self.booked_ref}.")


# ------------------------------------------------------------------ simulated callers (Lab 4.2)

def cards() -> list[dict]:
    return [json.loads(l) for l in (DATA / "callers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def say_slots(goal: dict, lang: str, which: list[str]) -> str:
    en, ar = SITES[goal["site_code"]]
    parts = []
    if lang == "ar":
        if "site_code" in which:
            parts.append(f"أبي أحجز جولة في {ar}")
        if "date" in which:
            parts.append(f"يوم {goal['date']}")
        if "party_size" in which:
            parts.append(f"لعدد {goal['party_size']} أشخاص")
        return " ".join(parts) or "نعم"
    if "site_code" in which:
        parts.append(f"I would like to book {en}")
    if "date" in which:
        parts.append(f"on {goal['date']}")
    if "party_size" in which:
        parts.append(f"for {goal['party_size']} people")
    return " ".join(parts) or "yes"


def hear(text: str, dialect: str, behaviour: str, k: int, caller_id: str) -> str:
    """The stand-in recogniser for simulated calls: digits of a date misheard for southern and Egyptian speakers
    on some turns; numbers lost on the first turns of a mumbling caller; English words transliterated when the
    caller switches language."""
    out = text
    if behaviour == "mumbles" and k < (3 if caller_id in ("SC07",) else 2):
        out = re.sub(r"(لعدد|for) \d+ (أشخاص|people)", "", out)
    if dialect in ("southern", "egyptian") and _h("date", caller_id, k) < 0.5:
        out = re.sub(r"(20\d\d-\d\d-)(\d)(\d)", lambda m: m.group(1) + m.group(2) + str((int(m.group(3)) + 3) % 10), out)
    if behaviour == "code_switches":
        out = out.replace("booking", "بوكنق")
    return " ".join(out.split())


@dataclass
class Caller:
    card: dict
    changed: bool = False
    said: list = field(default_factory=list)

    def first(self) -> str:
        b, lang = self.card["behaviour"], self.card["language"]
        which = ["site_code", "date", "party_size"] if b in ("cooperative", "interrupts", "changes_mind") else ["site_code"]
        t = say_slots(self.card["goal"], lang, which)
        if b == "code_switches":
            t = ("أبي أسوي booking " if lang == "ar" else "I need a booking, ") + t
        return t

    def reply(self, agent_text: str, heard_wrong: bool) -> str:
        g, lang, b = self.card["goal"], self.card["language"], self.card["behaviour"]
        low = agent_text.lower()
        if "shall i book" in low or "هل أحجز" in agent_text:
            if heard_wrong:
                fix = say_slots(g, lang, ["date"])
                return ("لا، " + fix) if lang == "ar" else "no, " + fix
            if b == "changes_mind" and not self.changed:
                self.changed = True
                g["date"] = self.card["change_to"]
                return ("لا، خلها " + f"يوم {g['date']}") if lang == "ar" else f"no, make it on {g['date']}"
            return "نعم احجز" if lang == "ar" else "yes book it"
        for k, (en, ar) in ASK.items():
            if en in agent_text or ar in agent_text:
                return say_slots(g, lang, [k])
        if "Which other date" in agent_text or "أي تاريخ آخر" in agent_text:
            return say_slots(g, lang, ["date"])
        return "شكرا" if lang == "ar" else "thank you"


def run_call(card: dict, agent: "Rahhal", max_turns: int = 8) -> dict:
    """Run one simulated call. Returns the turns (what was said, what the recogniser heard, the agent's reply)."""
    card = json.loads(json.dumps(card))
    caller = Caller(card)
    agent.name = card["caller_id"]
    turns, said = [], caller.first()
    for k in range(max_turns):
        heard = hear(said, card["dialect"], card["behaviour"], k, card["caller_id"])
        reply = agent.respond(heard)
        turns.append({"said": said, "heard": heard, "agent": reply})
        if agent.booked_ref or "goodbye" in reply.lower() or "مع السلامة" in reply:
            break
        wrong = bool(agent.slots.get("date")) and agent.slots.get("date") != card["goal"]["date"]
        said = caller.reply(reply, wrong)
    return {"caller_id": card["caller_id"], "goal": card["goal"], "turns": turns, "booked": agent.booked_ref}
