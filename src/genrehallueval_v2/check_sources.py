"""Find today's source of every GenreHalluEval passage on Bangla Wikipedia and check that it still says the same.

For each question: search Bangla Wikipedia for the passage's opening words (or use the recorded title), download the
current revision (plain text, revision id, timestamp) and check whether the passage and the gold still appear in it.
Raw API downloads are kept unchanged in data/raw/genrehallueval_v2/wikipedia/ (one JSON per question).
Non-Wikipedia sources (news sites, Banglapedia, unknown) are marked for a manual check.

Writes data/labels/genrehallueval_v2/source_check_2026-10-28.csv
Usage: python3 -I src/genrehallueval_v2/check_sources.py <project_root>
"""
import csv
import datetime
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

root = Path(sys.argv[1])
SRC = root / "data/final/GenreHalluEval-v1.1/questions.csv"
DRAFT = root / "data/labels/genrehallueval_v2/v1_questions_single_genre_draft_claude_2026-10-28.csv"
RAW = root / "data/raw/genrehallueval_v2/wikipedia"
OUT = root / "data/labels/genrehallueval_v2/source_check_2026-10-28.csv"
API = "https://bn.wikipedia.org/w/api.php"
UA = "GenreHalluEval-source-check/1.0 (SUST thesis; research use)"
RAW.mkdir(parents=True, exist_ok=True)


def N(s):
    s = unicodedata.normalize("NFC", s or "")
    s = re.sub(r"\[[^\]]{0,12}\]", "", s)                 # citation marks such as [১], [টীকা ১], [a]
    return re.sub(r"\s+", " ", s).strip()


def get(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(1.0)                              # stay well under the API's rate limit
                d = json.loads(r.read().decode("utf-8"))
                if "error" in d:                             # the API can also refuse inside a normal answer
                    if d["error"].get("code") in ("ratelimited", "maxlag"):
                        time.sleep(15 + 10 * attempt)
                        continue
                    raise RuntimeError(f"API error {d['error']}")
                return d
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("retry-after", "10")) + 2 + 5 * attempt)   # follow the server's request
        except Exception:
            time.sleep(3 + 5 * attempt)
    raise RuntimeError(url)


def page(title):
    d = get(dict(action="query", prop="extracts|revisions|info", rvprop="ids|timestamp", explaintext=1,
                 inprop="url", redirects=1, titles=title))
    p = next(iter(d["query"]["pages"].values()))
    return d, p


def sentences(text):
    return [s for s in re.split(r"(?<=[।?!])\s+", text) if len(s) > 25]


draft = {r["question_id"]: r for r in csv.DictReader(open(DRAFT, encoding="utf-8"))}
rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if draft[r["question_id"]]["keep_in_v2"] == "yes"]
out = []
def check_one(r):
    qid, passage, gold = r["question_id"], N(r["passage"]), N(r["gold"])
    rec = dict(question_id=qid, v1_source=r["source"], wiki_title="", url="", revid="", rev_timestamp="",
               passage_in_current="", share_of_passage_sentences_found="", gold_in_current="", status="", note="")
    if r["source"] != "Wikipedia":
        rec.update(status="manual check", note="not Wikipedia: give the URL and date of the live page")
        return rec
    titles = [r["wiki_title"]] if r["wiki_title"] else []
    if not titles:
        words = re.sub(r"[()\[\]\"'“”‘’:;,]", " ", passage).split()
        for n in (10, 6):
            hits = get(dict(action="query", list="search", srsearch=f'"{" ".join(words[:n])}"', srlimit=3))["query"]["search"]
            if hits:
                titles = [h["title"] for h in hits]
                break
        if not titles:
            hits = get(dict(action="query", list="search", srsearch=" ".join(words[:12]), srlimit=3))["query"]["search"]
            titles = [h["title"] for h in hits]
    best = None
    for t in titles:
        d, p = page(t)
        if "missing" in p:
            continue
        text = N(p.get("extract", ""))
        sents = sentences(passage) or [passage]
        share = sum(N(s) in text for s in sents) / len(sents)
        score = (passage in text, share, gold in text)
        if best is None or score > best[0]:
            best = (score, d, p, text)
        if passage in text:
            break
    if best is None:
        rec.update(status="not found", note="no Wikipedia page found for this passage: check by hand")
    else:
        (exact, share, gold_ok), d, p, text = best
        (RAW / f"{qid}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        rev = p["revisions"][0]
        rec.update(wiki_title=p["title"], url=p.get("fullurl", ""), revid=rev["revid"], rev_timestamp=rev["timestamp"],
                   passage_in_current="yes" if exact else "no", share_of_passage_sentences_found=f"{share:.2f}",
                   gold_in_current="yes" if gold_ok else "no",
                   status="current" if exact and gold_ok else "changed" if share >= 0.5 or gold_ok else "check by hand")
    return rec


for r in rows:
    try:
        rec = check_one(r)
    except Exception as e:                                   # one failed page must not stop the whole check
        rec = dict(question_id=r["question_id"], v1_source=r["source"], wiki_title="", url="", revid="", rev_timestamp="",
                   passage_in_current="", share_of_passage_sentences_found="", gold_in_current="", status="error",
                   note=f"lookup failed ({type(e).__name__}): check by hand")
    out.append(rec)
    qid = rec["question_id"]
    print(qid, rec["status"], rec["wiki_title"], rec["share_of_passage_sentences_found"], rec["gold_in_current"], flush=True)
    time.sleep(1.0)

with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
print("checked", len(out), "on", datetime.date.today().isoformat(), "->", OUT)
