"""Build the corrected BenHalluEval QA seed table (v1.3): human-verified genres + Claude's audit fixes
+ 2026 updates of time-sensitive answers + Mahdi's review of the changed rows (v1.2, 2026-10-17)
+ Claude's currency and world-fact check, done with Mahdi's review method (v1.3, 2026-10-17).

Inputs (never edited):
  data/raw/benhallueval/banglahallueval_qa_1000.csv     original seeds
  data/labels/genre_human_mahdi_full_raw.csv            Mahdi's verified genres (column `changed` = his corrections)
  data/labels/audit_claude.txt                          Claude's audit: status, rewritten question / gold, note
  data/labels/updates_2026.json                         web check of time-sensitive answers (new gold + passage patch)
  data/labels/human_audit_review/decisions_v1.2.json    Mahdi's review + Claude's follow-ups (src/audit/apply_human_review.py)
  data/labels/currency_check_v1.3.json                  Claude's currency / world-fact decisions, each with a reason
Outputs:
  data/final/benhallueval_qa_seeds_v1.3.csv     one row per unique question, plain UTF-8 (for Kaggle / pandas)
  data/final/human_review_applied_v1.2.csv      what the review changed, row by row (UTF-8 with BOM, for Excel)
  data/final/currency_applied_v1.3.csv          what the currency check changed, row by row

With --v1.1 the review is not applied and the v1.1 outputs are rebuilt instead (the seeds file and the
review sheet review_audit_changes.csv, which is what Mahdi reviewed). v1.1's "--no-current-updates" variant
is not built for v1.2: the hallucinated answers use the old facts as wrong answers, so the two cannot be mixed.

Usage: python3 -I src/audit/build_final_seeds.py <project_root> [--v1.1]
"""
import collections
import csv
import json
import sys
import unicodedata
from pathlib import Path

root = Path(sys.argv[1])
apply_updates = True
v11 = "--v1.1" in sys.argv[2:]
REVIEW_DATE = "2026-10-17"
raw_path = root / "data/raw/benhallueval/banglahallueval_qa_1000.csv"
human_path = root / "data/labels/genre_human_mahdi_full_raw.csv"
audit_path = root / "data/labels/audit_claude.txt"
updates_path = root / "data/labels/updates_2026.json"
out_dir = root / "data/final"

GENRES = ["History, Politics & Education", "Arts, Culture & Sports", "Science & Technology",
          "Geography & Places", "Religion", "Other"]
TYPO = {"History,Politics & Education": "History, Politics & Education",
        "Geography & Place": "Geography & Places"}
# Rewritten questions whose topic moved to another genre (guide v1.0 rules), unique-question index -> genre.
GENRE_AFTER_FIX = {14: "History, Politics & Education",   # now asks about Earhart's 1937 flights (an event)
                   548: "History, Politics & Education",  # now asks about the 9/11 attack
                   388: "History, Politics & Education"}  # now asks about the Umayyad Caliphate's area
# UPD = gold replaced by a 2026 fact: like FIXA, its 4 hallucinated answers must be checked before use.
# FIXA and UPD were "check" until the hallucinated answers existed; they were then written against the final
# gold (2026-10-14, src/halluc/), so they are "yes" now.
INCLUDE = {"EXCL": "no"}  # everything else: yes


def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(t):
    return " ".join(unicodedata.normalize("NFC", t).split())


NUKTA = {"\u09dc": "\u09a1\u09bc", "\u09dd": "\u09a2\u09bc", "\u09df": "\u09af\u09bc"}   # ড় ঢ় য়


def as_in_passage(text, ctx):
    """The same text as the passage writes it: ড়/ঢ়/য় can be one code point or a letter + nukta."""
    if text in ctx:
        return text
    for t in (unicodedata.normalize("NFC", text), unicodedata.normalize("NFD", text)):
        for v in (t, "".join(NUKTA.get(c, c) for c in t)):
            if v in ctx:
                return v
        joined = t
        for one, two in NUKTA.items():
            joined = joined.replace(two, one)
        if joined in ctx:
            return joined
    return text


def norm_genre(g):
    g = " ".join(g.split())
    g = TYPO.get(g, g)
    assert g in GENRES, f"unknown genre: {g!r}"
    return g


raw = load(raw_path)
human = {r["id"]: r for r in load(human_path)}
rows_of_id = collections.defaultdict(list)
uniq = []
for i, r in enumerate(raw):
    if r["id"] not in rows_of_id:
        uniq.append(r)
    rows_of_id[r["id"]].append(i + 1)

audit = {}
for line in audit_path.read_text(encoding="utf-8").splitlines():
    if line.strip() and not line.startswith("#"):
        idx, status, new_q, new_a, note = line.split("|", 4)
        audit[int(idx)] = (status, new_q.strip(), new_a.strip(), note.strip())
assert sorted(audit) == list(range(len(uniq))), "audit must cover every unique question exactly once"
upd_doc = json.loads(updates_path.read_text(encoding="utf-8"))
updates = {int(k): v for k, v in upd_doc["items"].items()}
assert all(v["check"] in ("updated", "still_correct", "kept_unverified", "kept_vacant") for v in updates.values())

final, review = [], []
for k, r in enumerate(uniq):
    h = human[r["id"]]
    genre = norm_genre(h["changed"]) if h["changed"].strip() else norm_genre(h["genre_draft"])
    human_changed = bool(h["changed"].strip())
    fine = "Sports" if (genre == "Arts, Culture & Sports" and h["genre_fine"].strip() == "Sports") else genre
    status, new_q, new_a, note = audit[k]
    genre_note = ""
    if k in GENRE_AFTER_FIX and GENRE_AFTER_FIX[k] != genre:
        genre_note = f"genre changed from {genre} because the question was rewritten"
        genre, fine = GENRE_AFTER_FIX[k], GENRE_AFTER_FIX[k]
    q = new_q if status in ("FIXQ", "FIXS") and new_q else r["question"].strip()
    a = new_a if status in ("FIXA", "FIXS") and new_a else r["correct_answer"].strip()
    if status in ("FIXA", "FIXS") and new_a:
        assert norm(new_a) in norm(r["context"]), f"new gold for {k} not in passage"
    ctx = r["context"]
    u = updates.get(k, {})
    check = u.get("check", "")
    if check == "updated":
        assert status in ("TU", "OK"), f"{k}: update on a {status} row"
        for old, new in u["patches"]:
            assert ctx.count(old) == 1, f"{k}: patch text must occur exactly once: {old[:40]}"
        if apply_updates:
            for old, new in u["patches"]:
                ctx = ctx.replace(old, new)
            a = u["new_gold"]
            assert norm(a) in norm(ctx), f"{k}: new gold not in patched passage"
            note = f"was {status}: {note}; " if note else f"was {status}; "
            note += f"updated to the {upd_doc['as_of']} fact: {u['note']}"
            status = "UPD"
        else:
            check = "updated_not_applied"
    row = {
        "question_id": r["id"],
        "context": ctx,
        "question": q,
        "correct_answer": a,
        "genre": genre,
        "genre_fine": fine,
        "audit_status": status,
        "include_main": INCLUDE.get(status, "yes"),
        "time_sensitive": "yes" if status in ("TU", "UPD") or check else "no",
        "weak_gold": "yes" if status == "WEAK" else "no",
        "audit_note": note,
        "genre_note": genre_note,
        "current_check": check,
        "answer_as_of": upd_doc["as_of"] if check else "",
        "update_note": u.get("note", "") if check != "updated" else "",
        "update_source": u.get("source", ""),
        "question_changed": "yes" if q != r["question"].strip() else "no",
        "answer_changed": "yes" if a != r["correct_answer"].strip() else "no",
        "context_changed": "yes" if ctx != r["context"] else "no",
        "question_original": r["question"].strip(),
        "correct_answer_original": r["correct_answer"].strip(),
        "context_original": r["context"],
        "source_rows": ";".join(map(str, rows_of_id[r["id"]])),
        "genre_human_corrected": "yes" if human_changed else "no",
    }
    final.append(row)
    if status not in ("OK", "TA") or genre_note or check:
        review.append({"review_no": len(review) + 1, "source_rows": row["source_rows"], "question_id": r["id"],
                       "audit_status": status, "current_check": check, "question_original": row["question_original"],
                       "question_new": q if row["question_changed"] == "yes" else "",
                       "correct_answer_original": row["correct_answer_original"],
                       "correct_answer_new": a if row["answer_changed"] == "yes" else "",
                       "genre": genre, "audit_note": note, "update_note": row["update_note"],
                       "update_source": row["update_source"], "genre_note": genre_note,
                       "context": r["context"], "context_new": ctx if row["context_changed"] == "yes" else "",
                       "approve": "", "your_fix": ""})

# ---------- v1.2: apply Mahdi's review (2026-10-17) and Claude's follow-ups ----------
applied = []
if not v11:
    dec = json.loads((root / "data/labels/human_audit_review/decisions_v1.2.json").read_text(encoding="utf-8"))
    for key, d in dec["items"].items():
        k = int(key)
        row = final[k]
        assert row["question_id"] == d["question_id"], k
        before = {f: row[f] for f in ("question", "correct_answer", "context", "audit_status", "genre")}
        he, ce = d.get("human_edits", {}), d.get("claude_edits", {})
        skip = set(ce.get("skip_human", []))
        notes = [f"{f['kind']}: {f['reason']}" for f in d["followups"]]
        if d["action"] == "drop":
            status = "EXCL"
        else:
            if "question" in he and "question" not in skip:
                row["question"] = he["question"]
            if he.get("question_revert") and "question" not in skip:
                row["question"] = row["question_original"]
            if "correct_answer" in he:
                row["correct_answer"] = he["correct_answer"]
            if "context" in he:
                row["context"] = he["context"]
            for f in ("question", "correct_answer"):
                if f in ce:
                    row[f] = ce[f]
            for old, new in ce.get("context_patches", []):
                assert row["context"].count(old) == 1, f"{k}: patch text must occur exactly once: {old[:40]}"
                row["context"] = row["context"].replace(old, new)
            if ce.get("normalize_space"):
                row["context"] = " ".join(row["context"].split())
            row["question"] = " ".join(row["question"].split())
            gold_changed = row["correct_answer"] != before["correct_answer"]
            if "status" in ce:
                status = ce["status"]
            elif gold_changed and row["question"] == before["question"] and row["time_sensitive"] == "yes":
                status = "UPD"
            elif gold_changed:
                status = "FIXA"
            elif row["question"] != before["question"]:
                status = "FIXQ"
            else:
                status = before["audit_status"]
            if status != "EXCL":
                row["correct_answer"] = as_in_passage(row["correct_answer"], row["context"])
                assert norm(row["correct_answer"]) in norm(row["context"]), f"{k}: gold not in passage after review"
            if "time_sensitive" in ce:
                row["time_sensitive"] = ce["time_sensitive"]
                if ce["time_sensitive"] == "no":       # the question now names a date: no current check applies
                    row["current_check"], row["answer_as_of"] = "", ""
            if gold_changed and row["time_sensitive"] == "yes":
                row["current_check"], row["answer_as_of"] = "updated_human", REVIEW_DATE
        if "genre" in ce and ce["genre"] != row["genre"]:
            row["genre_note"] = f"genre changed from {row['genre']} because the question was rewritten (Claude draft; check)"
            row["genre"] = row["genre_fine"] = norm_genre(ce["genre"])
        row["audit_status"] = status
        row["include_main"] = INCLUDE.get(status, "yes")
        row["weak_gold"] = "yes" if status == "WEAK" else "no"
        row["question_changed"] = "yes" if row["question"] != row["question_original"] else "no"
        row["answer_changed"] = "yes" if row["correct_answer"] != row["correct_answer_original"] else "no"
        row["context_changed"] = "yes" if row["context"] != row["context_original"] else "no"
        row["human_review"] = {"drop": "dropped", "edit": "edited", "approve": "approved"}.get(d["action"], "flagged in blind sheet")
        row["human_note"] = d.get("human_note", "")
        row["followup_note"] = " | ".join(notes)
        applied.append({"uidx": k, "question_id": row["question_id"], "action": row["human_review"],
                        "status_before": before["audit_status"], "status_after": status,
                        "question_before": before["question"],
                        "question_after": row["question"] if row["question"] != before["question"] else "",
                        "gold_before": before["correct_answer"],
                        "gold_after": row["correct_answer"] if row["correct_answer"] != before["correct_answer"] else "",
                        "context_changed_in_review": "yes" if row["context"] != before["context"] else "no",
                        "human_note": row["human_note"], "followup_note": row["followup_note"]})
    for row in final:
        for col in ("human_review", "human_note", "followup_note"):
            row.setdefault(col, "not_reviewed" if col == "human_review" else "")

# ---------- v1.3: currency and world-fact check (Claude, Mahdi's method; 2026-10-17) ----------
currency = []
if not v11:
    cur = json.loads((root / "data/labels/currency_check_v1.3.json").read_text(encoding="utf-8"))
    for key, c in cur["items"].items():
        k = int(key)
        row = final[k]
        before = {f: row[f] for f in ("question", "correct_answer", "context", "audit_status", "genre")}
        assert before["audit_status"] != "EXCL" or c.get("drop"), f"{k}: currency edit on an excluded seed"
        if c.get("drop"):
            status = "EXCL"
        else:
            for f in ("question", "correct_answer"):
                if f in c:
                    row[f] = c[f]
            for old, new in c.get("context_patches", []):
                assert row["context"].count(old) == 1, f"{k}: patch text must occur exactly once: {old[:50]}"
                row["context"] = row["context"].replace(old, new)
            row["correct_answer"] = as_in_passage(row["correct_answer"], row["context"])
            assert norm(row["correct_answer"]) in norm(row["context"]), f"{k}: gold not in passage after currency check"
            status = c.get("status", before["audit_status"])
            if "time_sensitive" in c:
                row["time_sensitive"] = c["time_sensitive"]
            if c["kind"] == "update":
                row["current_check"], row["answer_as_of"] = "updated", cur["as_of"]
                row["update_source"] = c.get("source", row["update_source"])
            elif row["time_sensitive"] == "no":
                row["current_check"], row["answer_as_of"] = "", ""
        if "genre" in c and c["genre"] != row["genre"]:
            row["genre_note"] = f"genre changed from {row['genre']} because the question was rewritten (Claude, v1.3)"
            row["genre"] = row["genre_fine"] = norm_genre(c["genre"])
        row["audit_status"] = status
        row["include_main"] = INCLUDE.get(status, "yes")
        row["weak_gold"] = "yes" if status == "WEAK" else "no"
        row["question_changed"] = "yes" if row["question"] != row["question_original"] else "no"
        row["answer_changed"] = "yes" if row["correct_answer"] != row["correct_answer_original"] else "no"
        row["context_changed"] = "yes" if row["context"] != row["context_original"] else "no"
        row["currency_note"] = f"{c['kind']}: {c['reason']}"
        currency.append({"uidx": k, "question_id": row["question_id"], "kind": c["kind"],
                         "status_before": before["audit_status"], "status_after": status,
                         "question_before": before["question"],
                         "question_after": row["question"] if row["question"] != before["question"] else "",
                         "gold_before": before["correct_answer"],
                         "gold_after": row["correct_answer"] if row["correct_answer"] != before["correct_answer"] else "",
                         "context_changed": "yes" if row["context"] != before["context"] else "no",
                         "reason": c["reason"], "source": c.get("source", "")})
    for row in final:
        row.setdefault("currency_note", "")

out_dir.mkdir(parents=True, exist_ok=True)
out_name = "benhallueval_qa_seeds_v1.1.csv" if v11 else "benhallueval_qa_seeds_v1.3.csv"
with open(out_dir / out_name, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(final[0]))
    w.writeheader()
    w.writerows(final)
if v11:
    with open(out_dir / "review_audit_changes.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(review[0]))
        w.writeheader()
        w.writerows(review)
else:
    with open(out_dir / "human_review_applied_v1.2.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(applied[0]))
        w.writeheader()
        w.writerows(applied)
    with open(out_dir / "currency_applied_v1.3.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(currency[0]))
        w.writeheader()
        w.writerows(currency)

n = len(final)
print(f"unique questions: {n}  (from {len(raw)} rows; duplicates merged: {len(raw) - n})")
print("audit status:", dict(collections.Counter(r["audit_status"] for r in final)))
print("include_main:", dict(collections.Counter(r["include_main"] for r in final)))
print("questions changed:", sum(r["question_changed"] == "yes" for r in final),
      "| answers changed:", sum(r["answer_changed"] == "yes" for r in final),
      "| passages changed:", sum(r["context_changed"] == "yes" for r in final),
      "| genres corrected by human:", sum(r["genre_human_corrected"] == "yes" for r in final),
      "| genres changed by rewrite:", sum(bool(r["genre_note"]) for r in final))
print("current check:", dict(collections.Counter(r["current_check"] for r in final if r["current_check"])),
      "| time_sensitive:", sum(r["time_sensitive"] == "yes" for r in final))
if not v11:
    print("human review:", dict(collections.Counter(r["human_review"] for r in final)))
main = [r for r in final if r["include_main"] == "yes"]
print(f"\nfinal genre counts (include_main = yes, n={len(main)}):")
for g, c in collections.Counter(r["genre"] for r in main).most_common():
    print(f"  {g:<32}{c:>5}")
print(f"\nwrote data/final/{out_name} ({n} rows)" + (f" and review_audit_changes.csv ({len(review)} rows)" if v11
                                                     else f", human_review_applied_v1.2.csv ({len(applied)} rows) and currency_applied_v1.3.csv ({len(currency)} rows)"))
