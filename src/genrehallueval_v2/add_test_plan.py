"""Add test_plan_v2.json to the GenreHalluEval v2 package: the test-half design decided by Mahdi Hasan Qurishi on
2026-10-30, after the learn run and the lock, before any test-half answer was judged.

- One route per notebook: route E, route F, route R, and the single best judge A (four notebooks), so the cost of
  each route is measured on its own. This replaces the combined routed notebook (never run).
- Main tests: E vs A, F vs A and R vs A, with the passage and without it: 6 tests, Holm over 6. This replaces the
  "main_tests" line of pool.json (R and F vs A, Holm over 4), which was written before the learn run.
- No OSF registration for v2 (Mahdi, 2026-10-30): this file, with its date and checksum, is the record.

Copies nothing else; updates the package checksums and the Kaggle zip. Never overwrites the file.
Usage: python3 -I src/genrehallueval_v2/add_test_plan.py <project_root> [--package DIR] [--zip PATH] [--labels CSV]
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("--package", default="data/final/GenreHalluEval-v2.0")
ap.add_argument("--zip", default="release/kaggle-genrehallueval-v2/GenreHalluEval-v2.zip")
ap.add_argument("--labels", default="data/labels/genrehallueval_v2/labels_v2.0.csv")
args = ap.parse_args()
root = Path(args.root)
rel = lambda p: Path(p) if Path(p).is_absolute() else root / p
PKG, ZIP, LABELS = rel(args.package), rel(args.zip), rel(args.labels)
OUT = PKG / "test_plan_v2.json"
if OUT.exists():
    raise SystemExit(f"{OUT} already exists. The test plan is never overwritten.")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert (PKG / "lock_ghe2_v1.json").exists(), "make the lock first (make_lock_v2.py)"
plan = dict(
    plan="GenreHalluEval v2 test half",
    decided="2026-10-30 by Mahdi Hasan Qurishi, after the learn run and lock_ghe2_v1, before any test-half run",
    registration="none (no OSF for v2, Mahdi 2026-10-30); this file and its checksum are the record",
    lock_sha256=sha(PKG / "lock_ghe2_v1.json"), labels_file=str(args.labels), labels_sha256=sha(LABELS),
    notebooks={
        "ghe2_route_E": "route E: the best genre guesser names the genre; the best judge for that genre (judge x genre "
                        "table of the learn half) judges. Asked for the genre: the guesser only.",
        "ghe2_route_F": "route F (own genre): every LLM with an own-genre cell names the genre; the LLM with the lowest "
                        "learn-half BHS inside the genre it named judges (tie: lower overall BHS); no cell: A.",
        "ghe2_route_R": "route R (best path): the lower learn-half score of the our-genre path (as E) and the own-genre "
                        "paths of the lock's askers.",
        "ghe2_single_best": "A: the single best judge of the learn half judges every answer."},
    main_tests=dict(comparisons=["E vs A", "F vs A", "R vs A"], conditions=["context", "no_context"], number=6,
                    correction="Holm over the 6", alpha=0.05,
                    method="paired bootstrap over test questions, 10,000 re-samples, seed 2026, two-sided; "
                           "BHS with no_answer as an error; labels as above"),
    also_reported=["each route's own cost (calls, tokens, time)", "every route vs A on all answers together",
                   "per-genre BHS", "determinism: same (judge, answer) must give the same verdict in every notebook"],
    supersedes="pool.json main_tests (R vs A and F vs A, Holm over 4)",
)
OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
with open(PKG / "checksums.sha256", "w", encoding="utf-8") as f:
    for p in sorted(x for x in PKG.rglob("*") if x.is_file() and x.name != "checksums.sha256"):
        f.write(f"{sha(p)}  {p.relative_to(PKG)}\n")
ZIP.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(x for x in PKG.rglob("*") if x.is_file()):
        z.write(p, Path("GenreHalluEval-v2") / p.relative_to(PKG))
print(f"wrote {OUT} (sha256 {sha(OUT)})\npackage checksums updated; zip for Kaggle (new version): {ZIP}")
