"""
Evaluate classification accuracy against hand-labeled test images.

Usage:
    python eval_runner.py                    # Full evaluation
    python eval_runner.py --max-images 10    # First N images only
    python eval_runner.py --dry-run          # Preview without API calls
"""

import sys
import os
import json
import argparse
import time
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app", "backend"))

from classifier import classify_image
from parser import EXPECTED_ATTRIBUTES


EVAL_ATTRIBUTES = [
    "garment_type", "style", "material", "pattern", "season", "occasion", "color_palette",
]


def normalize(value: str) -> set[str]:
    """Split a comma/space-separated value into lowercase tokens."""
    if not value:
        return set()
    return {v.strip().lower() for v in value.replace(",", " ").split() if v.strip()}


def compute_exact_match(predicted: str, expected: str) -> bool:
    if not predicted or not expected:
        return False
    return expected.strip().lower() in predicted.strip().lower()


def compute_jaccard(predicted: str, expected: str) -> float:
    pred_set = normalize(predicted)
    exp_set = normalize(expected)
    if not pred_set and not exp_set:
        return 1.0
    if not pred_set or not exp_set:
        return 0.0
    return len(pred_set & exp_set) / len(pred_set | exp_set)


def evaluate_image(predicted: dict, expected: dict) -> dict:
    results = {}
    for attr in EVAL_ATTRIBUTES:
        exp_val = expected.get(attr)
        pred_val = predicted.get(attr)
        if exp_val is None:
            continue

        if attr == "color_palette":
            score = compute_jaccard(pred_val or "", exp_val)
            results[attr] = {"score": score, "predicted": pred_val, "expected": exp_val, "method": "jaccard"}
        else:
            match = compute_exact_match(pred_val or "", exp_val)
            results[attr] = {"score": 1.0 if match else 0.0, "predicted": pred_val, "expected": exp_val, "method": "contains"}

    return results


def generate_report(all_results: dict, output_path: str = "report.md"):
    attr_scores = defaultdict(list)
    for image_id, results in all_results.items():
        for attr, data in results.items():
            attr_scores[attr].append(data["score"])

    lines = [
        "# Evaluation Report\n",
        f"**Images evaluated:** {len(all_results)}",
        f"**Attributes evaluated:** {', '.join(EVAL_ATTRIBUTES)}\n",
        "## Per-Attribute Accuracy\n",
        "| Attribute | Accuracy | Samples |",
        "|-----------|----------|---------|",
    ]

    for attr in EVAL_ATTRIBUTES:
        scores = attr_scores.get(attr, [])
        if scores:
            accuracy = sum(scores) / len(scores)
            lines.append(f"| {attr} | {accuracy:.1%} | {len(scores)} |")
        else:
            lines.append(f"| {attr} | N/A | 0 |")

    all_scores = [s for scores in attr_scores.values() for s in scores]
    overall = sum(all_scores) / len(all_scores) if all_scores else 0
    lines.append(f"\n**Overall accuracy:** {overall:.1%}\n")

    # Per-image breakdown
    lines.append("## Detailed Results\n")
    for image_id, results in sorted(all_results.items()):
        lines.append(f"### {image_id}\n")
        lines.append("| Attribute | Expected | Predicted | Score |")
        lines.append("|-----------|----------|-----------|-------|")
        for attr, data in results.items():
            lines.append(
                f"| {attr} | {data['expected']} | {data['predicted'] or 'N/A'} | {data['score']:.0%} |"
            )
        lines.append("")

    # Strengths and weaknesses
    lines.append("## Analysis\n")
    strong = [(a, sum(s)/len(s)) for a, s in attr_scores.items() if s and sum(s)/len(s) >= 0.7]
    weak = [(a, sum(s)/len(s)) for a, s in attr_scores.items() if s and sum(s)/len(s) < 0.7]

    if strong:
        lines.append("### Strengths\n")
        for attr, acc in sorted(strong, key=lambda x: -x[1]):
            lines.append(f"- **{attr}**: {acc:.1%}")

    if weak:
        lines.append("\n### Weaknesses\n")
        for attr, acc in sorted(weak, key=lambda x: x[1]):
            lines.append(f"- **{attr}**: {acc:.1%}")

    report = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(report)
    print(f"\nReport written to {output_path}")
    return report


async def run_evaluation(image_dir: str = "images", max_images: int = None, dry_run: bool = False):
    with open("expected_labels.json") as f:
        expected_labels = json.load(f)

    available = []
    for image_id in expected_labels:
        filepath = os.path.join(image_dir, f"{image_id}.jpg")
        if os.path.exists(filepath):
            available.append((image_id, filepath))

    if not available:
        print("No images found. Run download_images.py first.")
        return

    if max_images:
        available = available[:max_images]

    print(f"Evaluating {len(available)} images...")

    if dry_run:
        for image_id, filepath in available:
            print(f"  {image_id}: {filepath}")
        return

    all_results = {}
    for i, (image_id, filepath) in enumerate(available):
        print(f"[{i+1}/{len(available)}] Classifying {image_id}...")

        try:
            result = await classify_image(filepath)
            predicted = result.get("attributes", {})
            expected = expected_labels[image_id]
            eval_result = evaluate_image(predicted, expected)
            all_results[image_id] = eval_result

            scores = [d["score"] for d in eval_result.values()]
            avg = sum(scores) / len(scores) if scores else 0
            print(f"  Score: {avg:.0%} ({len(scores)} attributes)")

            time.sleep(1)  # rate limit
        except Exception as e:
            print(f"  ERROR: {e}")

    generate_report(all_results)


if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="Evaluate classification accuracy")
    parser.add_argument("--max-images", type=int, help="Max images to evaluate")
    parser.add_argument("--dry-run", action="store_true", help="Preview without API calls")
    parser.add_argument("--image-dir", default="images", help="Directory with test images")
    args = parser.parse_args()

    asyncio.run(run_evaluation(
        image_dir=args.image_dir,
        max_images=args.max_images,
        dry_run=args.dry_run,
    ))
