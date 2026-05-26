import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bug_reasoner import analyze_case
from run_demo import load_case


EXAMPLES = ROOT / "examples"
CASES = ROOT / "eval" / "cases.json"
RESULTS = ROOT / "eval" / "results.md"


def main() -> None:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    rows = []
    type_hits = 0
    top1_hits = 0
    top3_hits = 0

    for item in cases:
        case = load_case(EXAMPLES / item["case"])
        analysis = analyze_case(case)
        predicted_files = [hit.path.as_posix() for hit in analysis.suspicious_locations]
        type_hit = analysis.bug_type == item["expected_bug_type"]
        top1_hit = bool(predicted_files) and predicted_files[0] == item["expected_file"]
        top3_hit = item["expected_file"] in predicted_files[:3]
        type_hits += int(type_hit)
        top1_hits += int(top1_hit)
        top3_hits += int(top3_hit)
        rows.append(
            [
                item["case"],
                item["expected_bug_type"],
                analysis.bug_type,
                item["expected_file"],
                predicted_files[0] if predicted_files else "N/A",
                "Y" if type_hit else "N",
                "Y" if top1_hit else "N",
                "Y" if top3_hit else "N",
            ]
        )

    total = len(cases)
    report = [
        "# Evaluation Results",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Bug type accuracy | {type_hits}/{total} = {type_hits / total:.1%} |",
        f"| Top-1 suspicious file hit rate | {top1_hits}/{total} = {top1_hits / total:.1%} |",
        f"| Top-3 suspicious file hit rate | {top3_hits}/{total} = {top3_hits / total:.1%} |",
        "",
        "| Case | Expected Type | Predicted Type | Expected File | Top-1 File | Type Hit | Top-1 | Top-3 |",
        "|---|---|---|---|---|---:|---:|---:|",
    ]
    report.extend("| " + " | ".join(row) + " |" for row in rows)
    RESULTS.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[:8]))
    print(f"Saved: {RESULTS}")


if __name__ == "__main__":
    main()
