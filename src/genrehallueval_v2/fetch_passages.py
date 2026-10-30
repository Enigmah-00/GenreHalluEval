"""Download the current lead section of Bangla Wikipedia articles, for new GenreHalluEval v2 questions.

Input: a text file with one `GENRE|title` per line (titles chosen by Claude for a genre).
For every 20 titles: one API call (plain-text lead section, latest revision id and timestamp, page URL, redirects
followed). Every raw API answer is kept unchanged in data/raw/genrehallueval_v2/new/<batch>__<n>.json. A passage is
later copied word for word from these files, never typed.

Writes data/raw/genrehallueval_v2/new/<batch>__candidates.csv (genre, requested title, title, page id, revision id,
timestamp, url, mode, paragraphs as a JSON list).
With a 4th argument `full`, the whole article is downloaded instead of the lead (one call per title; lines of 4+
characters are kept, so short example lines such as "বিদ্যা + আলয় = বিদ্যালয়" survive). Grammar questions need this,
because the examples sit in the article body. Full downloads are marked mode=full, and a batch file refers to them as
`full::<title>`, so they never replace a lead download of the same article.
Usage: python3 -I src/genrehallueval_v2/fetch_passages.py <project_root> <titles.txt> <batch_name> [full]
"""
import csv
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

root, titles_file, batch = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
FULL = len(sys.argv) > 4 and sys.argv[4] == "full"
OUT = root / "data/raw/genrehallueval_v2/new"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://bn.wikipedia.org/w/api.php"
UA = "GenreHalluEval-source-check/1.0 (SUST thesis; research use)"


def get(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(1.0)
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
            time.sleep(int(e.headers.get("retry-after", "10")) + 2 + 5 * attempt)
        except Exception:
            time.sleep(3 + 5 * attempt)
    raise RuntimeError(url)


lines = [l.strip() for l in titles_file.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
wanted = [tuple(l.split("|", 1)) for l in lines]
rows = []
STEP = 1 if FULL else 20                                  # the API gives a whole article for one page per call
for n in range(0, len(wanted), STEP):
    chunk = wanted[n:n + STEP]
    params = dict(action="query", prop="extracts|revisions|info", explaintext=1, rvprop="ids|timestamp", inprop="url",
                  redirects=1, titles="|".join(t for _, t in chunk))
    params.update(dict(exsectionformat="plain") if FULL else dict(exintro=1, exlimit=20))
    d = get(params)
    (OUT / f"{batch}__{n // STEP:02d}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    norm = {x["from"]: x["to"] for x in d["query"].get("normalized", [])}
    redir = {x["from"]: x["to"] for x in d["query"].get("redirects", [])}
    pages = {p["title"]: p for p in d["query"]["pages"].values() if "missing" not in p}
    for g, t in chunk:
        t2 = redir.get(norm.get(t, t), norm.get(t, t))
        p = pages.get(t2)
        if not p or not p.get("extract"):
            rows.append(dict(genre=g, requested=t, title="", pageid="", revid="", timestamp="", url="",
                             mode="full" if FULL else "lead", paragraphs="[]"))
            continue
        text = unicodedata.normalize("NFC", p["extract"])
        paras = [re.sub(r"\s+", " ", x).strip() for x in text.split("\n") if len(x.strip()) > (3 if FULL else 40)]
        rev = p["revisions"][0]
        rows.append(dict(genre=g, requested=t, title=p["title"], pageid=p["pageid"], revid=rev["revid"],
                         timestamp=rev["timestamp"], url=p.get("fullurl", ""), mode="full" if FULL else "lead",
                         paragraphs=json.dumps(paras, ensure_ascii=False)))
with open(OUT / f"{batch}__candidates.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
found = sum(bool(r["title"]) for r in rows)
print(f"{batch}: {found} of {len(rows)} titles found -> {OUT / (batch + '__candidates.csv')}")
for r in rows:
    if r["title"]:
        print(f"\n### {r['genre']} | {r['title']} | rev {r['revid']} {r['timestamp']}")
        for i, para in enumerate(json.loads(r["paragraphs"])[:3]):
            print(f"[{i}] {para[:700]}")
    else:
        print(f"\n### {r['genre']} | NOT FOUND: {r['requested']}")
