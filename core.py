"""Haqdaar core logic: the four agents' brains, plain Python so they are testable."""
import json, re, pathlib
from datetime import date

SCHEMES = json.loads((pathlib.Path(__file__).parent / "schemes.json").read_text())
STATES = ["Uttar Pradesh","Delhi","Bihar","Rajasthan","Haryana","Maharashtra","Gujarat","Madhya Pradesh","West Bengal","Tamil Nadu","Karnataka","Kerala","Punjab","Odisha","Jharkhand","Uttarakhand"]
CATS = {"sc":"SC","st":"ST","obc":"OBC","general":"General","minority":"Minority","muslim":"Minority","sikh":"Minority","christian":"Minority"}
OCCS = ["student","farmer","street vendor","labourer"]
DISCLAIMER = "Verify on the official portal before applying. Rules change; this is guidance, not a guarantee."
REQUIRED = ["state","income","category","occupation","age"]
QUESTIONS = {"state":"Which state do you live in?","income":"What is your family's annual income (in Rs)?","category":"Your category: SC, ST, OBC, General or Minority?","occupation":"Your occupation: student, farmer, street vendor, labourer or other?","age":"Your age?"}

def parse(text, profile):
    """Fill profile from free text. Rule-based so it works offline."""
    t = text.lower(); p = dict(profile)
    for s in STATES:
        if s.lower() in t: p["state"] = s
    if re.search(r"\bup\b", t): p["state"] = "Uttar Pradesh"
    for k, v in CATS.items():
        if re.search(rf"\b{k}\b", t): p["category"] = v
    for o in OCCS:
        if o in t or (o == "labourer" and "labor" in t): p["occupation"] = o
    if "other" in t and "occupation" not in p: p["occupation"] = "other"
    m = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lac|l\b)", t)
    if m: p["income"] = int(float(m.group(1)) * 100000)
    else:
        m = re.search(r"(?:income|earn|rs\.?|₹)\s*[:=]?\s*(\d[\d,]{3,})", t) or re.search(r"\b(\d{5,7})\b", t)
        if m: p["income"] = int(m.group(1).replace(",", ""))
    # Parse explicit age formats first.
    m = (
        re.search(r"\b(\d{1,3})\s*(?:years|yrs|yr|y/o)\b", t)
        or re.search(r"\bage\s*[:=]?\s*(\d{1,3})\b", t)
    )

    if m:
        p["age"] = int(m.group(1))
    else:
        # Accept a bare number only if the whole message is a number,
        # or a number appears at the end after an ASI:One agent mention.
        mm = re.fullmatch(r"\s*(\d{1,3})\s*", t)

        if not mm:
            mm = re.search(r"\s(\d{1,3})\s*$", t)

        if mm and "income" in p:
            number = int(mm.group(1))
            if 0 <= number <= 120:
                p["age"] = number
    if re.search(r"\b(female|woman|girl|she|mother)\b", t): p["gender"] = "female"
    if re.search(r"\b(male|man|boy)\b", t) and "female" not in t: p["gender"] = "male"
    for k in ("name",):
        m = re.search(r"my name is ([a-z ]+)", t)
        if m: p["name"] = m.group(1).strip().title()
    return p

def next_question(profile):
    for k in REQUIRED:
        if k not in profile: return QUESTIONS[k]
    return None

# ---- Agent 1: Eligibility ----
def match_schemes(p):
    out = []
    for s in SCHEMES:
        if s["states"] != "all" and p["state"] not in s["states"]: continue
        if s["max_income"] is not None and p["income"] > s["max_income"]: continue
        if p["category"] not in s["categories"]: continue
        if "any" not in s["occupations"] and p["occupation"] not in s["occupations"]: continue
        if not (s["min_age"] <= p["age"] <= s["max_age"]): continue
        if s["gender"] != "any" and p.get("gender") != s["gender"]: continue
        out.append(s)
    return out

# ---- Agent 2: Documents ----
def doc_checklist(scheme, have):
    have_l = [h.lower() for h in have]
    ok = [d for d in scheme["docs"] if any(h in d.lower() or d.lower() in h for h in have_l)]
    missing = [d for d in scheme["docs"] if d not in ok]
    return {"have": ok, "missing": missing}

# ---- Agent 3: Deadlines ----
def deadline_info(scheme, today=None):
    today = today or date.today()
    d = scheme["deadline"]
    if d == "rolling": return {"status": "open (rolling)", "days_left": None}
    left = (date.fromisoformat(d) - today).days
    note = scheme.get("deadline_note", "")
    status = "CLOSED" if left < 0 else ("URGENT" if left <= 14 else "upcoming")
    return {"status": status, "date": d, "days_left": left, "note": note}

# ---- Agent 4: Form prep ----
def prefill(scheme, p):
    return {"Scheme": scheme["name"], "Applicant name": p.get("name", "<enter>"), "State": p["state"],
            "Category": p["category"], "Annual family income (Rs)": p["income"], "Occupation": p["occupation"],
            "Age": p["age"], "Gender": p.get("gender", "<enter>"), "Aadhaar / bank details": "<enter yourself>",
            "Submit at": scheme["portal"]}

def full_report(p, have=()):
    lines = []
    for s in match_schemes(p):
        c = doc_checklist(s, have); d = deadline_info(s)
        dl = d["status"] + (f" ({d['date']}, {d['days_left']} days left; {d['note']})" if d.get("date") else "")
        lines.append(f"**{s['name']}** - {s['benefit']}\n  Deadline: {dl}\n  Have: {', '.join(c['have']) or 'none yet'}\n  Missing: {', '.join(c['missing']) or 'nothing'}\n  Apply: {s['portal']}")
    if not lines: return "No curated scheme matches your profile yet. " + DISCLAIMER
    return f"Found {len(lines)} scheme(s) for you:\n\n" + "\n\n".join(lines) + "\n\n" + DISCLAIMER
