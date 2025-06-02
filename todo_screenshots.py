#!/usr/bin/env python3
"""List missing screenshot files referenced in docs/sem_ppt_plan/slides.json."""
import json
import os
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), "docs", "sem_ppt_plan")
JSON_PATH = os.path.join(BASE_DIR, "slides.json")

def main():
    try:
        with open(JSON_PATH, encoding="utf-8") as f:
            slides = json.load(f)
    except FileNotFoundError:
        sys.stderr.write(f"slides.json not found at {JSON_PATH}\n")
        sys.exit(1)

    for item in slides:
        before_rel = item.get("before", "")
        after_rel = item.get("after", "")
        before_path = os.path.join(BASE_DIR, before_rel)
        after_path = os.path.join(BASE_DIR, after_rel)
        if not os.path.isfile(before_path) or not os.path.isfile(after_path):
            slide_id = item.get("id", "<no id>")
            print(f"{slide_id} \u2013 {before_rel} \u2013 {after_rel}")

if __name__ == "__main__":
    main()
