"""Build the final dataset package (v1.3: gold + 4 hallucinated answers per seed).

Inputs:  data/final/benhallueval_qa_seeds_v1.3.csv
         data/labels/hallucinations_claude/batch_*.txt, then revisions_v1.2.txt and v1.3 on top   (uidx|F|C|S|I)
         data/labels/hallucinations_claude/notes_gold_issues.txt
         data/final/item_positions.csv          frozen answer positions, so item_ids never change between versions
         data/labels/halluc_validation_blind198.csv + human_halluc_blind198/..._raw_v2.csv   the blind human check
Outputs: data/final/benhallueval-qa-v1.3/  items.csv, seeds.csv, gold_issues.csv, human_validation_blind198.csv,
         stats.json, shortcut_report.md, prompts/, docs/, checksums.sha256 (README and Kaggle metadata by hand)

item_id = <question_id>__a<position>. The positions were shuffled once (seed 2026) in v1.1 and are frozen in
item_positions.csv; a question that is new in a later version gets its own shuffle (seed "2026:<question_id>").

Usage: python3 -I src/halluc/build_items.py <project_root>
"""
import csv
import json
import random
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

root = Path(sys.argv[1])
SEED = 2026
WRITER = "claude-opus-5-5"
GUIDE = "prompts/hallucination_writing_guide_v1.md (v1.0)"
TYPES = {"F": "factualness", "C": "comprehension", "S": "specificity", "I": "inference"}
VERSION = "1.3"
OUT = root / f"data/final/benhallueval-qa-v{VERSION}"
POSITIONS = root / "data/final/item_positions.csv"
HDIR = root / "data/labels/hallucinations_claude"

with open(root / f"data/final/benhallueval_qa_seeds_v{VERSION}.csv", encoding="utf-8", newline="") as f:
    seeds = list(csv.DictReader(f))
seed_cols = list(seeds[0].keys())

halluc, revised = {}, {}
REVISIONS = {"revisions_v1.2.txt": "1.2", "revisions_v1.3.txt": "1.3"}
for p in sorted(HDIR.glob("batch_*.txt")) + [HDIR / name for name in REVISIONS]:
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            parts = [a.strip() for a in line.split("|")]
            assert len(parts) == 5, line
            k = int(parts[0])
            if p.name in REVISIONS:
                revised[k] = REVISIONS[p.name]
            else:
                assert k not in halluc, k
            halluc[k] = dict(zip("FCSI", parts[1:]))
need = {k for k, r in enumerate(seeds) if r["include_main"] == "yes"}
assert need <= set(halluc), "run src/halluc/validate.py first"

with open(POSITIONS, encoding="utf-8", newline="") as f:
    frozen = list(csv.DictReader(f))
pos_of = {(r["question_id"], r["answer_type"]): int(r["position"]) for r in frozen}

# ---------- items ----------
items, new_positions = [], []
for k, r in enumerate(seeds):
    if k not in need:
        continue
    qid = r["question_id"]
    answers = [("gold", r["correct_answer"])] + [(t, halluc[k][t]) for t in "FCSI"]
    if all((qid, t) in pos_of for t, _ in answers):
        answers.sort(key=lambda ta: pos_of[(qid, ta[0])])
    else:                                       # a question new in this version: its own fixed shuffle
        random.Random(f"{SEED}:{qid}").shuffle(answers)
        for pos, (t, _) in enumerate(answers):
            pos_of[(qid, t)] = pos
            new_positions.append({"question_id": qid, "answer_type": t, "position": pos, "first_version": VERSION})
    for pos, (t, a) in enumerate(answers):
        items.append({
            "item_id": f"{r['question_id']}__a{pos}",
            "question_id": r["question_id"],
            "position": pos,
            "context": r["context"],
            "question": r["question"],
            "answer": a,
            "label": 0 if t == "gold" else 1,
            "hallucinated": "no" if t == "gold" else "yes",
            "answer_type": t,
            "hallucination_type": "none" if t == "gold" else TYPES[t],
            "answer_source": (f"tydiqa_gold_audited_v{VERSION}" if t == "gold" else
                              f"{WRITER}; {GUIDE}" + (f"; revised in v{revised[k]}" if k in revised else "")),
            "genre": r["genre"],
            "genre_fine": r["genre_fine"],
            "audit_status": r["audit_status"],
            "include_main": r["include_main"],
            "weak_gold": r["weak_gold"],
            "time_sensitive": r["time_sensitive"],
            "current_check": r["current_check"],
            "answer_as_of": r["answer_as_of"],
        })
assert len({i["item_id"] for i in items}) == len(items)
if new_positions:                               # append-only: positions, once given, never change
    with open(POSITIONS, "a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=list(new_positions[0])).writerows(new_positions)

OUT.mkdir(parents=True, exist_ok=True)


def write_csv(path, rows, cols):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


write_csv(OUT / "items.csv", items, list(items[0].keys()))
write_csv(OUT / "seeds.csv", seeds, seed_cols)

notes = []
for line in (root / "data/labels/hallucinations_claude/notes_gold_issues.txt").read_text(encoding="utf-8").splitlines():
    if line.strip() and not line.startswith("#"):
        k, note = line.split("|", 1)
        k = int(k)
        notes.append({"question_id": seeds[k]["question_id"], "audit_status": seeds[k]["audit_status"],
                      "include_main": seeds[k]["include_main"],
                      "question": seeds[k]["question"], "correct_answer": seeds[k]["correct_answer"],
                      "note": note.strip()})
import json as _json
_cur = _json.loads((root / "data/labels/currency_check_v1.3.json").read_text(encoding="utf-8"))["items"]
for n in notes:
    k = next(i for i, r in enumerate(seeds) if r["question_id"] == n["question_id"])
    c = _cur.get(str(k))
    n["status_v1.3"] = ("seed dropped" if seeds[k]["include_main"] != "yes" else
                        f"fixed in v1.3 ({c['kind']})" if c else "open")
order = {r["question_id"]: k for k, r in enumerate(seeds)}
notes.sort(key=lambda n: order[n["question_id"]])  # stable: two notes on one seed keep their order
write_csv(OUT / "gold_issues.csv", notes, list(notes[0].keys()))

# ---------- statistics and shortcut baselines ----------
def norm(t):
    t = unicodedata.normalize("NFC", t)
    return " ".join(re.sub(r"[\s,।.;:'\"“”‘’()\-–—]+", " ", t).split()).lower()


def bhs(rows, flag):
    """BHS (lower is better) of a rule that says 'hallucinated' when flag(row) is True."""
    a = [i for i in rows if i["label"] == 0]
    b = [i for i in rows if i["label"] == 1]
    ea = sum(flag(i) for i in a) / len(a)
    eb = sum(not flag(i) for i in b) / len(b)
    return round(50 * (ea + eb), 2), round(100 * ea, 2), round(100 * eb, 2)


main = [i for i in items if i["include_main"] == "yes"]
by_type = defaultdict(list)
for i in main:
    by_type[i["answer_type"]].append(i)
stats = {"items": len(items), "questions": len(items) // 5, "items_main": len(main),
         "questions_main": len(main) // 5, "labels": Counter(i["hallucinated"] for i in items),
         "genre_questions_main": Counter(i["genre"] for i in main if i["answer_type"] == "gold"),
         "length_chars_main": {}, "share_exact_span_in_passage_main": {}, "share_with_comma_main": {},
         "baselines_main": {}}
for t in ["gold", "F", "C", "S", "I"]:
    rows = by_type[t]
    lens = [len(i["answer"]) for i in rows]
    stats["length_chars_main"][t] = {"mean": round(statistics.mean(lens), 1), "median": statistics.median(lens)}
    stats["share_exact_span_in_passage_main"][t] = round(
        sum(i["answer"].strip() in i["context"] for i in rows) / len(rows), 3)
    stats["share_with_comma_main"][t] = round(sum("," in i["answer"] for i in rows) / len(rows), 3)

gold_len = {i["question_id"]: len(i["answer"]) for i in main if i["answer_type"] == "gold"}
rules = {
    "not an exact span of the passage": lambda i: i["answer"].strip() not in i["context"],
    "not a span after normalising spaces and punctuation": lambda i: norm(i["answer"]) not in norm(i["context"]),
    "contains a comma": lambda i: "," in i["answer"],
    "longer than 24 characters (2 x the median gold length)": lambda i: len(i["answer"]) > 24,
    "longest of the 5 answers (uses all 5, so not a real single-answer judge)":
        lambda i: len(i["answer"]) == max(len(j["answer"]) for j in main if j["question_id"] == i["question_id"]),
    "always yes": lambda i: True,
}
for name, rule in rules.items():
    s, ea, eb = bhs(main, rule)
    stats["baselines_main"][name] = {"BHS": s, "trackA_error": ea, "trackB_error": eb}
span = [i for i in main if i["answer"].strip() in i["context"]]
stats["span_subset_main"] = {
    "what": "items whose answer is an exact span of the passage; the span rule cannot separate them",
    "items": len(span), "questions": len({i["question_id"] for i in span}),
    "by_type": Counter(i["answer_type"] for i in span)}
(OUT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = ["# Shortcut report (main set: include_main = yes)", "",
         f"{stats['questions_main']} questions, {stats['items_main']} items. BHS = ½ × (Track A error + Track B error) × 100;"
         " lower is better; 50 = chance. These rules never read the question, so a real judge must beat them to show it"
         " uses the passage and question rather than surface form.", "",
         "## Answer length and form by type", "",
         "| Type | Mean chars | Median chars | Exact span of passage | Contains a comma |", "|---|---|---|---|---|"]
for t in ["gold", "F", "C", "S", "I"]:
    L = stats["length_chars_main"][t]
    lines.append(f"| {t} | {L['mean']} | {L['median']} | {100 * stats['share_exact_span_in_passage_main'][t]:.1f}% |"
                 f" {100 * stats['share_with_comma_main'][t]:.1f}% |")
lines += ["", "## Rule baselines", "", "| Rule ('hallucinated' when …) | BHS | Track A error | Track B error |",
          "|---|---|---|---|"]
for name, v in stats["baselines_main"].items():
    lines.append(f"| {name} | {v['BHS']} | {v['trackA_error']}% | {v['trackB_error']}% |")
sp = stats["span_subset_main"]
lines += ["", "## Span subset (robustness check)", "",
          f"{sp['items']} items in {sp['questions']} questions have an answer that is an exact span of the passage"
          f" (by type: {dict(sp['by_type'])}). On these items the span rule is useless, so judge scores here show"
          " whether a judge really checks that the span answers the question.",
          "", "Golds are TyDiQA-GoldP spans, so every gold is a span. The original BenHalluEval QA design has the"
          " same property (gold spans, generated hallucinations), so this shortcut is a property of the task design,"
          " not only of these answers. Report the span baseline next to every judge score."]
(OUT / "shortcut_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# ---------- the blind human check (Mahdi, 2026-10-17; sheet sent 2026-10-14 from v1.1) ----------
def read(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


sent = {r["item_id"]: r for r in read(root / "data/labels/halluc_validation_blind198.csv")}
human = read(root / "data/labels/human_halluc_blind198/halluc_validation_blind198_human_raw_v2.csv")
TYPO = {"yes": "yes", "no": "no", "yws": "yes", "yed": "yes", "tes": "yes"}   # obvious typos in the sheet
# blind labels whose cell was lost from the sheet, restored later by the labeller
RESTORED = {r["item_id"]: r for r in read(root / "data/labels/human_halluc_blind198/restored_labels.csv")}
ITEM = {i["item_id"]: i for i in items}
old_items = {i["item_id"]: i for i in read(root / "data/final/superseded/v1.1/benhallueval-qa-v1.1/items.csv")}
val = []
for h in sorted(human, key=lambda r: int(r["row"])):
    iid, v = h["item_id"], h["human_hallucinated(yes/no)"].strip().lower()
    source = "sheet (blind)" if v else ""
    if iid in RESTORED:
        assert not v and RESTORED[iid]["blind"] == "yes", f"{iid}: sheet label and restored label, or not blind"
        v, source = RESTORED[iid]["human_hallucinated"], f"sheet (blind), cell lost, restored {RESTORED[iid]['restored_on']}"
    old, now = old_items[iid], ITEM.get(iid)
    val.append({"item_id": iid, "question_id": h["question_id"], "answer_shown": sent[iid]["answer"],
                "label_v1.1": old["hallucinated"], "answer_type": old["answer_type"],
                "human_hallucinated": TYPO.get(v, "") if v else "", "human_label_source": source,
                "human_natural": h["human_natural(1-3)"].strip(),
                "human_note": h["human_note"].strip(),
                f"in_v{VERSION}": "yes" if now else "no (question dropped)",
                "changed_since_check": ("" if not now else "yes" if any(
                    now[c] != sent[iid][c] for c in ("question", "context", "answer")) else "no")})
write_csv(OUT / "human_validation_blind198.csv", val, list(val[0].keys()))


def agreement(rows):
    pairs = [(r["label_v1.1"], r["human_hallucinated"]) for r in rows if r["human_hallucinated"]]
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[g] * cb[g] for g in ca) / n ** 2
    return {"items": n, "agreement": round(po, 4), "kappa": round((po - pe) / (1 - pe), 4),
            "disagreements": [r["item_id"] for r in rows if r["human_hallucinated"]
                              and r["human_hallucinated"] != r["label_v1.1"]]}


stats["human_validation"] = {
    "who": "one person (the project owner), blind to the labels; sheet of 198 questions x 5 answers, shuffled",
    "as_shown_v1.1": agreement(val),
    "restored_labels": [r["item_id"] for r in val if "restored" in r["human_label_source"]],
    "unlabelled_items": [r["item_id"] for r in val if not r["human_hallucinated"]],
    "naturalness_counts": dict(Counter(r["human_natural"] for r in val)),
    "items_changed_or_dropped_since": sum(r["changed_since_check"] != "no" for r in val)}
(OUT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- supporting files and checksums (README.md and dataset-metadata.json are written by hand) ----------
import hashlib
import shutil

(OUT / "docs").mkdir(exist_ok=True)
shutil.copyfile(root / "prompts/hallucination_writing_guide_v1.md", OUT / "docs/hallucination_writing_guide_v1.md")
shutil.copyfile(root / "docs/genre-guide.md", OUT / "docs/genre_guide_v1.md")
shutil.copyfile(root / "data/labels/updates_2026.json", OUT / "updates_2026.json")
(OUT / "prompts").mkdir(exist_ok=True)
for name in ["judge_v1.txt", "judge_noctx_v1.txt", "genre_v1.txt", "judge_bn_v1.txt", "judge_noctx_bn_v1.txt",
             "genre_bn_v1.txt", "README.md"]:
    shutil.copyfile(root / "prompts" / name, OUT / "prompts" / name)

# Mahdi's blind genre labels (200 questions, made before he saw any Claude label), mapped to v1.0 names.
# The notebook scores LLM genre guesses against these too: no LLM touched them.
V1_NAME = {"History & Politics": "History, Politics & Education", "Arts & Culture": "Arts, Culture & Sports",
           "Sports": "Arts, Culture & Sports"}
with open(root / "data/labels/genre_blind200_human_mahdi_raw.csv", encoding="utf-8-sig", newline="") as f:
    blind = list(csv.DictReader(f))
blind_rows = []
for b in blind:
    g = V1_NAME.get(b["your_genre"].strip(), b["your_genre"].strip())
    assert g in {r["genre"] for r in seeds}, g
    blind_rows.append({"question_id": b["id"], "genre_blind_human": g, "genre_blind_human_raw": b["your_genre"].strip()})
write_csv(OUT / "genre_blind200.csv", blind_rows, list(blind_rows[0].keys()))
for name in ["README.md", "dataset-metadata.json"]:
    assert (OUT / name).exists(), f"write {name} first"
files = sorted(f for f in OUT.rglob("*") if f.is_file() and f.name != "checksums.sha256")
(OUT / "checksums.sha256").write_text(
    "".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(OUT)}\n" for f in files), encoding="utf-8")

print(f"items: {len(items)} ({stats['labels']}); main: {len(main)} items, {len(main) // 5} questions")
print("human validation:", json.dumps(stats["human_validation"]["as_shown_v1.1"], ensure_ascii=False))
print(json.dumps(stats["baselines_main"], ensure_ascii=False, indent=1))
