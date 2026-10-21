from core import *
from datetime import date
p = parse("I am a 20 years student from Uttar Pradesh, OBC, family income 1.2 lakh, female", {})
assert p["state"]=="Uttar Pradesh" and p["income"]==120000 and p["age"]==20 and p["category"]=="OBC" and p["gender"]=="female", p
ids = [s["id"] for s in match_schemes(p)]
assert "nsp-post-matric-obc" in ids and "up-scholarship" in ids and "pm-kisan" not in ids, ids
c = doc_checklist(SCHEMES[2], ["Aadhaar", "bank passbook"]); assert "Income certificate" in c["missing"]
print("ok", ids)
f = parse("farmer, Bihar, 40 years, SC, income 80000", {}); assert "pm-kisan" in [s["id"] for s in match_schemes(f)]
print(full_report(p, ["Aadhaar"])[:500])
