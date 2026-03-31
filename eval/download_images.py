"""Download test images from Pexels for evaluation."""

import json
import os
import urllib.request
import sys


def download_images(urls_file: str = "image_urls.json", output_dir: str = "images"):
    os.makedirs(output_dir, exist_ok=True)

    with open(urls_file) as f:
        images = json.load(f)

    total = len(images)
    downloaded = 0
    failed = 0

    for i, entry in enumerate(images):
        image_id = entry["id"]
        url = entry["url"]
        filepath = os.path.join(output_dir, f"{image_id}.jpg")

        if os.path.exists(filepath):
            print(f"[{i+1}/{total}] {image_id} already exists, skipping")
            downloaded += 1
            continue

        try:
            print(f"[{i+1}/{total}] Downloading {image_id}...")
            req = urllib.request.Request(url, headers={"User-Agent": "FashionAI-Eval/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(filepath, "wb") as out:
                    out.write(resp.read())
            downloaded += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print(f"\nDone: {downloaded} downloaded, {failed} failed out of {total}")


if __name__ == "__main__":
    download_images()
