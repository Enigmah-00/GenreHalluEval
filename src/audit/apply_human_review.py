"""Turn Mahdi's reviewed audit sheet + Claude's follow-ups into one decision file for the v1.2 seed build.

Inputs (never edited):
  data/labels/human_audit_review/review_audit_changes_human_raw.csv   Mahdi's review (approve, your_fix, edited cells)
  data/final/review_audit_changes.csv                                 the sheet as we sent it (to see which cells he edited)
  data/labels/human_audit_review/claude_followups_v1.2.json           Claude's follow-ups, each with a reason
  data/raw/benhallueval/banglahallueval_qa_1000.csv                   to map question_id -> unique-question index
Output:
  data/labels/human_audit_review/decisions_v1.2.json                  read by src/audit/build_final_seeds.py

A cell counts as edited only if it differs from what we sent (after trimming spaces). approve = 0 means drop.
An edited question_original (instead of question_new) is read as the new question.

Usage: python3 -I src/audit/apply_human_review.py <project_root>
"""
import csv
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
D = root / "data/labels/human_audit_review"


def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


uidx = {}
for r in load(root / "data/raw/benhallueval/banglahallueval_qa_1000.csv"):   # unique questions, first-appearance order
    uidx.setdefault(r["id"], len(uidx))
sent = {r["question_id"]: r for r in load(root / "data/final/review_audit_changes.csv")}
human = load(D / "review_audit_changes_human_raw.csv")
assert {r["question_id"] for r in human} == set(sent), "the reviewed sheet must have the same rows as the one we sent"


def no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    assert not dup, f"duplicate keys in claude_followups_v1.2.json: {dup} (the later one would silently win)"
    return dict(pairs)


follow = json.loads((D / "claude_followups_v1.2.json").read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)

decisions = {}
for h in human:
    o, k = sent[h["question_id"]], uidx[h["question_id"]]
    d = {"uidx": k, "question_id": h["question_id"], "review_no": int(h["review_no"]), "approve": h["approve"].strip(),
         "human_note": h["your_fix"].strip(), "followups": []}
    if d["approve"] == "0":
        d["action"] = "drop"
    else:
        assert d["approve"] == "1", h["approve"]
        edits = {}
        qn_h, qn_o = h["question_new"].strip(), o["question_new"].strip()
        qo_h, qo_o = h["question_original"].strip(), o["question_original"].strip()
        if qn_h != qn_o:
            edits["question" if qn_h else "question_revert"] = qn_h or True
        elif qo_h != qo_o:
            edits["question"] = qo_h
        an_h, an_o = h["correct_answer_new"].strip(), o["correct_answer_new"].strip()
        if an_h and an_h != an_o:
            edits["correct_answer"] = an_h
        cn_h, cn_o = h["context_new"].strip(), o["context_new"].strip()
        if cn_h and cn_h != cn_o:
            edits["context"] = cn_h
        d["action"] = "edit" if edits else "approve"
        d["human_edits"] = edits
    decisions[k] = d

for key, f in follow["items"].items():
    k = int(key)
    d = decisions.setdefault(k, {"uidx": k, "question_id": next(q for q, i in uidx.items() if i == k),
                                 "action": "not_in_review", "human_note": "", "followups": []})
    d["followups"].append({"kind": f["kind"], "reason": f["reason"]})
    for field in ("question", "correct_answer", "context_patches", "normalize_space", "status", "genre",
                  "time_sensitive", "skip_human"):
        if field in f:
            d.setdefault("claude_edits", {})[field] = f[field]

out = {"as_of": follow["as_of"], "items": {str(k): decisions[k] for k in sorted(decisions)}}
(D / "decisions_v1.2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
acts = {}
for d in decisions.values():
    acts[d["action"]] = acts.get(d["action"], 0) + 1
print(f"{len(decisions)} decisions: {acts}; with Claude follow-ups: {sum(bool(d['followups']) for d in decisions.values())}")
