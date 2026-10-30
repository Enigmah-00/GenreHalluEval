"""Agreement of the two GenreHalluEval passage-label sheets, and the agreed labels.

Inputs (raw sheets, never edited; each filled alone):
  data/labels/dataset2/passage_labels_annotator1_filled_raw_2026-10-27.csv   annotator 1: Umme Zoayria Abedin
  data/labels/dataset2/passage_labels_annotator2_filled_raw_2026-10-27.csv   annotator 2: Md Saminul Amin
  data/labels/dataset2/passage_labels_annotator2_copy_on_annotator1_sheet_2026-10-27.csv
      (annotator 2 also filled annotator 1's sheet by mistake; only checked here, never used for kappa)
  data/final/GenreHalluEval-v1.1/items.csv
Outputs:
  data/labels/dataset2/passage_label_agreement.md        kappa (all, per condition, per genre) and every disagreement
  data/labels/dataset2/passage_label_resolutions_v1.csv  one row per disagreement, to be decided (never overwritten)
  data/labels/dataset2/passage_labels_agreed_v1.csv      final label per answer, written only when every
                                                         disagreement has a final_label (input of compare_routes.py)

Labels in the sheets: c = correct (0), h = hallucinated (1), unclear. Anything else stops the script.
Usage: python3 -I src/dataset2/label_agreement.py <project_root>
"""
import collections
import csv
import sys
from pathlib import Path

root = Path(sys.argv[1])
L = root / "data/labels/dataset2"
A1 = L / "passage_labels_annotator1_filled_raw_2026-10-27.csv"
A2 = L / "passage_labels_annotator2_filled_raw_2026-10-27.csv"
A2_COPY = L / "passage_labels_annotator2_copy_on_annotator1_sheet_2026-10-27.csv"
ITEMS = root / "data/final/GenreHalluEval-v1.1/items.csv"
RES = L / "passage_label_resolutions_v1.csv"
AGREED = L / "passage_labels_agreed_v1.csv"
LC = "label (correct / hallucinated / unclear)"
MAP = {"c": 0, "correct": 0, "h": 1, "hallucinated": 1, "u": "unclear", "unclear": "unclear"}


def read_sheet(p):
    # the header row can be anywhere (one sheet was sorted after filling)
    with open(p, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    head = next(r for r in rows if r and r[0] == "row")
    out = {}
    for r in rows:
        if r and r[0] != "row":
            x = dict(zip(head, r))
            v = x[LC].strip().lower()
            assert v in MAP, (p.name, x["item_id"], v)
            assert x["item_id"] not in out, (p.name, x["item_id"])
            out[x["item_id"]] = MAP[v]
    return out


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    c1, c2 = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(c1[k] * c2[k] for k in set(c1) | set(c2)) / n / n
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


with open(ITEMS, encoding="utf-8", newline="") as f:
    items = {r["item_id"]: r for r in csv.DictReader(f)}
a1, a2, a2c = read_sheet(A1), read_sheet(A2), read_sheet(A2_COPY)
assert set(a1) == set(a2) == set(a2c) == set(items), "every sheet needs all 1,250 answers"
ids = sorted(items)

groups = [("all answers", ids)]
groups += [(f"condition `{c}`", [i for i in ids if items[i]["condition"] == c]) for c in ("context", "no_context")]
groups += [(g, [i for i in ids if items[i]["genre"] == g]) for g in sorted({items[i]["genre"] for i in ids})]
dis = [i for i in ids if a1[i] != a2[i]]
copy_same = sum(a2[i] == a2c[i] for i in ids)
design = {i: int(items[i]["design_label"]) for i in ids}

lines = ["# GenreHalluEval v1.1: passage-label agreement (made by `src/dataset2/label_agreement.py`)", "",
         "Annotator 1: Umme Zoayria Abedin. Annotator 2: Md Saminul Amin. Each filled a shuffled sheet alone (no answer",
         "type, no design label, no judge output). Labels: passage label (correct only if the passage supports everything",
         "in the answer), for all 1,250 answers.", "",
         "| Answers | n | Agree | Cohen's kappa |", "|---|---|---|---|"]
for name, sub in groups:
    po, k = kappa([(a1[i], a2[i]) for i in sub])
    lines.append(f"| {name} | {len(sub)} | {po * 100:.1f}% | {k:.3f} |")
lines += ["", f"- Label counts: annotator 1 {dict(collections.Counter(map(str, a1.values())))}; annotator 2 "
          f"{dict(collections.Counter(map(str, a2.values())))} (0 = correct, 1 = hallucinated).",
          f"- Against the design label (0 = gold, 1 = written hallucination): annotator 1 differs on "
          f"{sum(a1[i] != design[i] for i in ids)}, annotator 2 on {sum(a2[i] != design[i] for i in ids)}.",
          f"- Annotator 2 also filled annotator 1's sheet by mistake (kept as "
          f"`{A2_COPY.name}`): it agrees with annotator 2's own sheet on {copy_same} of {len(ids)} answers. It is not "
          "used for kappa.", "",
          f"## Disagreements ({len(dis)} answers, {len({items[i]['question_id'] for i in dis})} questions)", "",
          "| item_id | condition | answer type | design | annotator 1 | annotator 2 | answer |", "|---|---|---|---|---|---|---|"]
lines += [f"| {i} | {items[i]['condition']} | {items[i]['answer_type']} | {design[i]} | {a1[i]} | {a2[i]} | "
          f"{items[i]['answer']} |" for i in dis]
(L / "passage_label_agreement.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))

cols = ["item_id", "question_id", "condition", "answer", "label_a1", "label_a2", "final_label", "decided_by", "note"]
if not RES.exists():
    with open(RES, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows([dict(item_id=i, question_id=items[i]["question_id"], condition=items[i]["condition"],
                          answer=items[i]["answer"], label_a1=a1[i], label_a2=a2[i]) for i in dis])
    print("\nwrote", RES.name, "(fill final_label = 0 / 1 / exclude, and decided_by)")
with open(RES, encoding="utf-8", newline="") as f:
    res = {r["item_id"]: r for r in csv.DictReader(f)}
assert set(res) == set(dis), "the resolutions file does not match the disagreements"
open_items = [i for i in dis if res[i]["final_label"].strip() not in ("0", "1", "exclude")]
if open_items:
    print(f"\n{len(open_items)} disagreements are still open; {AGREED.name} not written:", open_items)
    sys.exit(0)
with open(AGREED, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item_id", "question_id", "condition", "label_a1", "label_a2", "label", "how"])
    for i in ids:
        if i in res:
            w.writerow([i, items[i]["question_id"], items[i]["condition"], a1[i], a2[i], res[i]["final_label"].strip(),
                        f"resolved by {res[i]['decided_by'].strip()}"])
        else:
            w.writerow([i, items[i]["question_id"], items[i]["condition"], a1[i], a2[i],
                        "exclude" if a1[i] == "unclear" else a1[i], "agreed"])
print("\nwrote", AGREED.name)
