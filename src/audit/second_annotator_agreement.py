"""Human–human agreement: the second annotator's blind sheets vs Mahdi's blind labels (and vs our final labels).

Inputs (raw sheets, never edited):
  data/labels/second_annotator/genre_blind200_filled_annotator2_raw.csv   (200 questions, blind)
  data/labels/second_annotator/halluc_blind200_filled_annotator2_raw.csv  (200 answers = 40 whole questions, blind)
  data/labels/genre_blind200_human_mahdi_raw.csv                          (Mahdi's blind genres, same 200 questions)
  data/final/benhallueval-qa-v1.3/human_validation_blind198.csv           (Mahdi's blind hallucination labels)
Writes data/labels/second_annotator/agreement.json and agreement.md. Joins on ids, never on text.

Usage: python3 -I src/audit/second_annotator_agreement.py <project_root>
"""
import collections
import csv
import json
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
SA = root / "data/labels/second_annotator"
PKG = root / "data/final/benhallueval-qa-v1.3"
SEED, B = 2026, 2000
V1 = {"History & Politics": "History, Politics & Education", "Arts & Culture": "Arts, Culture & Sports",
      "Sports": "Arts, Culture & Sports"}
TYPO = {"yes": "yes", "no": "no", "yws": "yes", "yed": "yes", "tes": "yes"}


def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[g] * cb[g] for g in set(ca) | set(cb)) / n ** 2
    return po, ((po - pe) / (1 - pe) if pe < 1 else 1.0)


def summary(pairs, groups=None):
    """groups: list of index lists to re-sample together (whole questions); default single items."""
    po, k = kappa(pairs)
    rng = random.Random(SEED)
    units = groups or [[i] for i in range(len(pairs))]
    ks = []
    for _ in range(B):
        sample = [pairs[i] for _ in units for i in units[rng.randrange(len(units))]]
        ks.append(kappa(sample)[1])
    ks.sort()
    return {"n": len(pairs), "agreement": round(po, 4), "kappa": round(k, 3),
            "kappa_range95": [round(ks[int(0.025 * B)], 3), round(ks[int(0.975 * B) - 1], 3)],
            "disagreements": dict(collections.Counter(f"{a} -> {b}" for a, b in pairs if a != b).most_common())}


out = {}
# ---- genre: 200 blind questions ----
a2 = {r["id"]: r["your_genre"].strip() for r in load(SA / "genre_blind200_filled_annotator2_raw.csv")}
mh = {r["id"]: V1.get(r["your_genre"].strip(), r["your_genre"].strip()) for r in load(root / "data/labels/genre_blind200_human_mahdi_raw.csv")}
final = {r["question_id"]: r["genre"] for r in load(PKG / "items.csv")}
assert set(a2) == set(mh), "the two genre sheets must cover the same 200 questions"
ids = sorted(a2)
out["genre_annotator2_vs_mahdi_blind"] = summary([(mh[i], a2[i]) for i in ids])
in_final = [i for i in ids if i in final]
out["genre_annotator2_vs_final_labels"] = summary([(final[i], a2[i]) for i in in_final])
out["genre_mahdi_blind_vs_final_labels"] = summary([(final[i], mh[i]) for i in in_final])
out["genre_label_counts"] = {"annotator2": dict(collections.Counter(a2.values())), "mahdi_blind": dict(collections.Counter(mh.values()))}

# ---- hallucination: 200 answers (40 whole questions) ----
h2 = {r["item_id"]: TYPO.get(r["hallucinated (yes/no)"].strip().lower(), "") for r in load(SA / "halluc_blind200_filled_annotator2_raw.csv")}
val = {r["item_id"]: r for r in load(PKG / "human_validation_blind198.csv")}
assert all(v in ("yes", "no") for v in h2.values()), "every answer needs yes or no"
assert all(val[k]["changed_since_check"] == "no" for k in h2), "only answers unchanged since Mahdi's check"
items = sorted(h2, key=lambda k: (val[k]["question_id"], k))
qgroups = collections.defaultdict(list)
for i, k in enumerate(items):
    qgroups[val[k]["question_id"]].append(i)
groups = list(qgroups.values())
out["halluc_annotator2_vs_mahdi_blind"] = summary([(val[k]["human_hallucinated"], h2[k]) for k in items], groups)
out["halluc_annotator2_vs_design_labels"] = summary([(val[k]["label_v1.1"], h2[k]) for k in items], groups)
out["halluc_mahdi_blind_vs_design_labels_same_200"] = summary([(val[k]["label_v1.1"], val[k]["human_hallucinated"]) for k in items], groups)
out["halluc_disagreeing_items"] = [{"item_id": k, "answer_type": val[k]["answer_type"], "design": val[k]["label_v1.1"],
                                    "mahdi": val[k]["human_hallucinated"], "annotator2": h2[k]}
                                   for k in items if len({val[k]["label_v1.1"], val[k]["human_hallucinated"], h2[k]}) > 1]

(SA / "agreement.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
md = ["# Second annotator: agreement (blind sheets)", "",
      "| Comparison | n | Agreement | Cohen's kappa (95% range) |", "|---|---|---|---|"]
for k, v in out.items():
    if isinstance(v, dict) and "kappa" in v:
        md.append(f"| {k} | {v['n']} | {100 * v['agreement']:.1f}% | {v['kappa']:.3f} ({v['kappa_range95'][0]:.3f} to {v['kappa_range95'][1]:.3f}) |")
md += ["", "Hallucination ranges re-sample whole questions (40). Disagreements are listed in `agreement.json`."]
(SA / "agreement.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
for k in ("genre_annotator2_vs_mahdi_blind", "halluc_annotator2_vs_mahdi_blind"):
    print(f"\n{k} disagreements:", out[k]["disagreements"])
print("label counts:", out["genre_label_counts"])
print("hallucination items where anyone disagrees:", out["halluc_disagreeing_items"])
