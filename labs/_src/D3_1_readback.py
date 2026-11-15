# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pillow>=11.0", "pydantic>=2.12", "jiwer>=4.0", "openai>=2.0", "python-dotenv>=1.1"]
# ///
# %% [markdown]
# # Lab 3.1 · Read-back that callers understand
#
# Day 3 · Session 1 (Synthesis and read-back) · 25 min.
#
# When Rahhal books a visit it reads the booking back: the site, the date, the party size and the booking code. A
# synthetic voice given "2026-12-03" or "HTB-4821" as written says something no caller can check. You write the
# spoken forms in English and Arabic, chunk the booking code for the ear, synthesise the confirmations, and score a
# short listening test by category with intervals.
#
# **Reference state.** Three bookings in this notebook and `data/listening_test.csv`: eight listeners, twelve items
# (names, numbers, dates), each heard as raw text and as read-back. The listening results are synthetic.
#
# **Tasks**
# - [ ] 1 · Spoken forms of dates, numbers and codes in two languages (10')
# - [ ] 2 · Chunk the booking code for the ear (4')
# - [ ] 3 · Synthesise and check the spoken length (4')
# - [ ] 4 · Listening-test accuracy by category, with intervals (7')
# - [ ] ✱ Stretch · Spell an unusual name letter by letter and test it again

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/ae-408.git"
    if not Path("/content/ae-408").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/ae-408"], check=True)
    os.chdir("/content/ae-408/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("trails.py").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import datetime as dt

import pandas as pd

import trails as U

BOOKINGS = [
    {"ref": "HTB-4821", "site_code": "HT-03", "date": "2026-12-03", "party_size": 7, "name": "Wedad Al-Omari"},
    {"ref": "HTB-1590", "site_code": "HT-07", "date": "2026-12-11", "party_size": 12, "name": "Ghusoun Al-Mutlaq"},
    {"ref": "HTB-3007", "site_code": "HT-10", "date": "2027-01-02", "party_size": 2, "name": "Salem Al-Balawi"},
]
print("synthesis path:", "hosted " + U.TTS_MODELS["ar"] if U.hosted("speech") else "stand-in (length estimate only)")

# %% [markdown]
# ## 1 · Spoken forms (10')
#
# ✏️ **Exercise** · Write four functions that turn values into words a voice can say and a caller can check:
#
# | Function | Input | English | Arabic |
# |---|---|---|---|
# | `say_date(d, lang)` | `"2026-12-03"` | `Thursday the third of December` | `الخميس ثلاثة ديسمبر` |
# | `say_party(n, lang)` | `7` | `seven people` | `سبعة أشخاص` |
# | `say_digits(s, lang)` | `"4821"` | `four eight two one` | `أربعة ثمانية اثنين واحد` |
#
# Arabic dates use the day's cardinal number and the month's name; the year is left out when it is the current
# one (the line's "today" is 2026-12-01). For party sizes: 1 is `شخص واحد`, 2 is `شخصين`, 3 to 10 take `أشخاص`,
# 11 and 12 take `شخصا`.

# %%
EN_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]
EN_ORD = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh",
          "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth",
          "twentieth", "twenty-first", "twenty-second", "twenty-third", "twenty-fourth", "twenty-fifth", "twenty-sixth",
          "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth", "thirty-first"]
AR_NUM = ["صفر", "واحد", "اثنين", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة", "أحد عشر", "اثنا عشر",
          "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر", "عشرين", "واحد وعشرين",
          "اثنين وعشرين", "ثلاثة وعشرين", "أربعة وعشرين", "خمسة وعشرين", "ستة وعشرين", "سبعة وعشرين", "ثمانية وعشرين",
          "تسعة وعشرين", "ثلاثين", "واحد وثلاثين"]
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
AR_DAYS = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
TODAY = dt.date(2026, 12, 1)


def say_date(d, lang):
    # BEGIN SOLUTION
    x = dt.date.fromisoformat(d)
    if lang == "en":
        s = f"{x.strftime('%A')} the {EN_ORD[x.day]} of {x.strftime('%B')}"
        return s if x.year == TODAY.year else f"{s} {x.year}"
    s = f"{AR_DAYS[x.weekday()]} {AR_NUM[x.day]} {AR_MONTHS[x.month - 1]}"
    return s if x.year == TODAY.year else f"{s} {x.year}"
    # END SOLUTION


def say_party(n, lang):
    # BEGIN SOLUTION
    if lang == "en":
        return "one person" if n == 1 else f"{EN_ONES[n]} people"
    if n == 1:
        return "شخص واحد"
    if n == 2:
        return "شخصين"
    return f"{AR_NUM[n]} {'أشخاص' if n <= 10 else 'شخصا'}"
    # END SOLUTION


def say_digits(s, lang):
    # BEGIN SOLUTION
    words = EN_ONES if lang == "en" else AR_NUM
    return " ".join(words[int(ch)] for ch in s if ch.isdigit())
    # END SOLUTION


# %%
CASES = [("say_date", ("2026-12-03", "en"), "Thursday the third of December"),
         ("say_date", ("2026-12-03", "ar"), "الخميس ثلاثة ديسمبر"),
         ("say_date", ("2027-01-02", "en"), "Saturday the second of January 2027"),
         ("say_party", (7, "en"), "seven people"), ("say_party", (7, "ar"), "سبعة أشخاص"),
         ("say_party", (2, "ar"), "شخصين"), ("say_party", (12, "ar"), "اثنا عشر شخصا"),
         ("say_digits", ("4821", "en"), "four eight two one"), ("say_digits", ("4821", "ar"), "أربعة ثمانية اثنين واحد")]
done = 0
for fn, args, want in CASES:
    try:
        got = globals()[fn](*args)
        done += 1
        print("✅" if got == want else "❌", fn, args, "->", got)
    except NotImplementedError:
        print("✏️ not done yet:", fn)
U.check(done == 0 or all(globals()[f](*a) == w for f, a, w in CASES), "every spoken form matches its example")

# %% [markdown]
# ## 2 · A booking code for the ear (4')
#
# "HTB-4821" said as a word is "htb four thousand eight hundred and twenty-one": a caller cannot write that down.
#
# ✏️ **Exercise** · `say_code(code, lang)`: the letters one by one, then the digits in pairs, with a pause (a comma)
# between groups: `H, T, B, four eight, two one`. In Arabic, the Latin letters are said by their names
# (`LETTERS_AR`).

# %%
LETTERS_AR = {"H": "إتش", "T": "تي", "B": "بي"}


def say_code(code, lang):
    # BEGIN SOLUTION
    letters, digits = code.split("-")
    first = [c if lang == "en" else LETTERS_AR[c] for c in letters]
    pairs = [say_digits(digits[i:i + 2], lang) for i in range(0, len(digits), 2)]
    return ("، " if lang == "ar" else ", ").join(first + pairs)
    # END SOLUTION


# %%
try:
    code_en = say_code("HTB-4821", "en")
except NotImplementedError:
    def say_code(code, lang):
        letters, digits = code.split("-")
        first = [c if lang == "en" else LETTERS_AR[c] for c in letters]
        words = EN_ONES if lang == "en" else AR_NUM
        pairs = [" ".join(words[int(c)] for c in digits[i:i + 2]) for i in range(0, len(digits), 2)]
        return ("، " if lang == "ar" else ", ").join(first + pairs)
    code_en = say_code("HTB-4821", "en")
print(code_en, "|", say_code("HTB-4821", "ar"))
U.check(code_en == "H, T, B, four eight, two one", "the code is chunked for the ear")

# %% [markdown]
# ## 3 · Synthesise and check the length (4')
#
# A confirmation the caller cannot hold in mind is no confirmation. Rahhal's rule: **one confirmation in at most 12
# seconds of speech**.
#
# ✏️ **Exercise** · Write `confirmation(b, lang)` that joins the site, the spoken date, the party size and the code
# into one sentence, synthesise it with `U.synthesise(text, lang)` (the reply's `extra["seconds"]` is its length) and
# print the length of each confirmation in both languages.

# %%
def confirmation(b, lang):
    en, ar = U.SITES[b["site_code"]]
    # BEGIN SOLUTION
    if lang == "en":
        return (f"Booked: {en}, {say_date(b['date'], 'en')}, for {say_party(b['party_size'], 'en')}. "
                f"Your code is {say_code(b['ref'], 'en')}.")
    return (f"تم الحجز: {ar}، يوم {say_date(b['date'], 'ar')}، لعدد {say_party(b['party_size'], 'ar')}. "
            f"رقم الحجز {say_code(b['ref'], 'ar')}.")
    # END SOLUTION


# %%
rows = []
for b in BOOKINGS:
    for lang in ("en", "ar"):
        try:
            text = confirmation(b, lang)
        except NotImplementedError:
            text = f"{U.SITES[b['site_code']][0 if lang == 'en' else 1]}, {b['date']}, {b['party_size']}, {b['ref']}"
        r = U.synthesise(text, lang, out=U.artifacts("D3_1") / f"{b['ref']}_{lang}.wav")
        rows.append({"ref": b["ref"], "lang": lang, "seconds": r.extra["seconds"], "text": text})
lengths = pd.DataFrame(rows)
print(lengths.to_string(index=False))
U.check((lengths.seconds <= 12).all(), "every confirmation fits in 12 seconds", model=True)

# %% [markdown]
# ## 4 · The listening test (7')
#
# Eight listeners heard twelve items twice: as raw text given to the voice, and as your read-back. A listener's answer
# is right when they wrote the item down correctly.
#
# ✏️ **Exercise** · Per category and condition: correct answers, trials, accuracy and its 95% Wilson interval
# (`U.wilson(k, n)`). Which category does read-back help most, and is the gain larger than the intervals?

# %%
test = pd.read_csv(U.DATA / "listening_test.csv")


def score(test):
    # BEGIN SOLUTION
    g = test.groupby(["category", "condition"]).correct.agg(k="sum", n="count").reset_index()
    g["accuracy"] = (g.k / g.n).round(3)
    g[["lo", "hi"]] = [tuple(round(v, 3) for v in U.wilson(k, n)) for k, n in zip(g.k, g.n)]
    return g
    # END SOLUTION


# %%
try:
    scores = score(test)
except NotImplementedError:
    scores = test.groupby(["category", "condition"]).correct.agg(k="sum", n="count").reset_index()
    scores["accuracy"] = (scores.k / scores.n).round(3)
    scores[["lo", "hi"]] = [tuple(round(v, 3) for v in U.wilson(k, n)) for k, n in zip(scores.k, scores.n)]
print(scores.to_string(index=False))
wide = scores.pivot(index="category", columns="condition", values=["accuracy", "lo", "hi"])
gain_clear = wide[("lo", "readback")] > wide[("hi", "raw")]
print("read-back gain larger than both intervals:", gain_clear.to_dict())
U.check(bool(gain_clear["number"]) and bool(gain_clear["date"]), "read-back clearly helps numbers and dates")

# %% [markdown]
# 🔍 **Look at** names: raw text was already understood 29 times in 32, and read-back changed little. A name is the
# item a caller can correct on the spot; a code read as one long number is not.

# %% [markdown]
# ## ✱ Stretch · Spell a name
#
# Some names are heard wrong whatever the voice: write `spell(name, lang)` that adds the letters of the family name
# after it ("Al-Mutlaq: M, U, T, L, A, Q") and decide when Rahhal should use it.

# %%
# BEGIN SOLUTION
def spell(name, lang="en"):
    family = name.split()[-1].replace("Al-", "")
    return f"{name}: " + ", ".join(family.upper())


print(spell("Ghusoun Al-Mutlaq"))
# Use it when the caller asks to repeat the name, or when the name is not in the line's list of common names.
# END SOLUTION

# %% [markdown]
# ## Checkpoint
#
# 1. Why are the digits of a booking code said in pairs and not as one number?
# 2. Which category gained most from read-back, and how do you know the gain is not noise?
# 3. With a hosted voice one confirmation took 14 seconds. What do you cut first?
#
# <details><summary>Answers</summary>
#
# 1. A caller writes digits down in groups; "four thousand eight hundred and twenty-one" must be decoded first.
# 2. Numbers (16 of 32 raw, 32 of 32 read back): the read-back interval's lower end is above the raw interval's upper end.
# 3. The year when it is the current one, then the weekday; never the code or the party size.
# </details>
#
# **Carry forward.** `say_date`, `say_party` and `say_code` belong in the capstone agent's read-back.
