"""List seeds whose answer may depend on when you ask (the currency check, v1.3; run again before reusing the set).

Flags a seed if its question or gold has a time-dependent cue: "current/now/latest" words, counts of things that
change (people, members, institutions, records), superlatives and rankings, officeholders and owners, or a year
in the question. Also flags passages that say "now/current". This is a wide net; a person (or Claude) decides.

Usage: python3 -I src/audit/scan_time_sensitive.py <project_root> > candidates.txt
"""
import csv
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
CUES = {
    "now": r"বর্তমান|এখন|সর্বশেষ|সাম্প্রতিক|চলতি|আজকের|সর্বাধুনিক|নতুন|সবচেয়ে নবীন",
    "year_in_q": r"[১২][০৯][০-৯][০-৯]|\b(19|20)\d\d\b",
    "count": r"কতগুলো|কতগুলি|কতটি|কয়টি|কয়টি|কত জন|কতজন|মোট কত|সংখ্যা কত|কত সংখ্যক",
    "people": r"জনসংখ্যা|জনগোষ্ঠী|শিক্ষার্থী|ছাত্র|কর্মী|সদস্য|ব্যবহারকারী|ভক্ত|অনুসারী|ভাষাভাষী|বক্তা|দর্শক",
    "institutions": r"বিশ্ববিদ্যালয়|কলেজ|বিদ্যালয়|স্কুল|হাসপাতাল|কোম্পানি|কারখানা|ব্যাংক|পৌরসভা|ইউনিয়ন|উপজেলা|জেলা|থানা|বিভাগ|দেশ|রাষ্ট্র|সংস্থা|দল|শাখা|স্টেশন|বিমানবন্দর|মসজিদ|মন্দির",
    "record": r"সর্বাধিক|সবচেয়ে|সর্বোচ্চ|সর্বনিম্ন|বৃহত্তম|ক্ষুদ্রতম|দীর্ঘতম|উচ্চতম|গভীরতম|তম |রেকর্ড|রান|উইকেট|গোল|পদক|শিরোপা|চ্যাম্পিয়ন|বিজয়ী|জয়ী",
    "office": r"প্রধানমন্ত্রী|রাষ্ট্রপতি|প্রেসিডেন্ট|সভাপতি|চেয়ারম্যান|মহাসচিব|সাধারণ সম্পাদক|উপাচার্য|মেয়র|মহানাগরিক|গভর্নর|মুখ্যমন্ত্রী|মন্ত্রী|অধিনায়ক|কোচ|প্রধান নির্বাহী|সিইও|মালিক|পরিচালক|প্রধান বিচারপতি|স্পিকার|রাজা|রানী|সম্রাট|স্বামী|স্ত্রী|নেতা",
    "money_size": r"আয়তন|দৈর্ঘ্য|উচ্চতা|মুদ্রা|রাজধানী|সদর দপ্তর|সদর দফতর|জিডিপি|বাজেট|আয়|বেতন|দাম|মূল্য",
}
PASSAGE_NOW = re.compile(r"বর্তমান|এখন পর্যন্ত|আজ পর্যন্ত|সম্প্রতি|চলতি")

with open(root / "data/final/benhallueval_qa_seeds_v1.3.csv", encoding="utf-8", newline="") as f:
    seeds = list(csv.DictReader(f))
n = 0
for k, r in enumerate(seeds):
    if r["include_main"] != "yes":
        continue
    text = r["question"] + " || " + r["correct_answer"]
    hits = [c for c, pat in CUES.items() if re.search(pat, text)]
    pnow = PASSAGE_NOW.findall(r["context"])
    strong = {"now", "year_in_q", "office", "people"} & set(hits) or ({"count"} <= set(hits) and
             {"institutions", "people"} & set(hits)) or ({"record"} & set(hits))
    if strong or r["time_sensitive"] == "yes":
        n += 1
        i = r["context"].find("বর্তমান")
        print(f"#{k} [{r['audit_status']}|ts={r['time_sensitive']}|{r['current_check'] or '-'}] {'+'.join(hits)}"
              f"{' | passage-now x' + str(len(pnow)) if pnow else ''}")
        print(f"   Q: {r['question']} | A: {r['correct_answer']}")
        if i >= 0:
            print(f"   P(now): …{r['context'][max(0, i - 80):i + 140]}…")
print(f"\n{n} candidates", file=sys.stderr)
