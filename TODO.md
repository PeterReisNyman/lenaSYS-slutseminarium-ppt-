# Supplemental-Seminar PowerPoint – Task List

> **Goal:** Produce a detailed PowerPoint that replaces the missed final seminar  
> (extra detail, commit/issue hashes, screenshots, LOC, before/after, etc.)

## 0  Preparation
- [ ] Create folder `docs/sem_ppt_plan/img/` for all screenshots.
- [ ] Install Python deps once:  
  ```bash
  python3 -m venv venv && source venv/bin/activate
  pip install python-pptx pillow
````

## 1  Select Issues/Commits (skip trivial ones)

* [ ] PR #17651 — commit `2562b79` (15 May) – doc refactor
* [ ] Issue #16861 — branch **G2-2025-v5#16861** (02 May) – refactor two PHP services
* [ ] Issue #16731 (17 Apr) – inverse-dependency audit
* [ ] Issue #16659 + PR (16 Apr) – inverse-dep docs, zero found
* [ ] Issue #16452 (11 Apr) – doc inverse dependencies for `createNewCourse_ms.php`
* [ ] PR #17311 (07 May) – new docs for two micro-services
* [ ] PR #17411 — commit `cf65ee6` (09 May) – eight new service docs
* [ ] Docker failure analysis (#16823, 24 Apr)
* [ ] PR #17163 review (06 May) – missing `curlService.php`
* [ ] PR #17164 review (05 May) – CSRF + validation feedback

*(Trim or add items if you need more/less slides.)*

## 2  Gather Evidence per Item

For each selected issue/commit:

| 📄 What            | 📋 Command / Action                                      |
| ------------------ | -------------------------------------------------------- |
| Commit hash & date | `git log --oneline -n 1 <hash>`                          |
| LOC changed        | `git show --stat <hash>`                                 |
| Before screenshot  | checkout *before* branch → run app → screenshot          |
| After screenshot   | checkout *after* branch → run app → screenshot           |
| Bullet summary     | Answer **problem / change / why better / how to verify** |
| Δ code size        | copy the `+xx / -yy` line                                |

Save screenshots as `img/<id>_before.png`, `img/<id>_after.png`.

## 3  Fill `slides.json`

* Open `docs/sem_ppt_plan/slides.json`.
* Duplicate one object per issue/commit and fill every field:

  * `id`, `title`, `hash`, `date`, `stat`, `bullets`, `before`, `after`.

## 4  Auto-generate PowerPoint

```bash
python docs/sem_ppt_plan/build_ppt.py
```

Output: `docs/sem_ppt_plan/supplemental_seminar.pptx`

## 5  Sanity-Check

* [ ] Every slide shows full hash or issue #.
* [ ] Screenshots readable at 100 % zoom.
* [ ] LOC line present.
* [ ] File size ≤ 15 MB (compress PNGs if needed).

Commit the `.pptx` and push.

````

---

### 2  docs/sem_ppt_plan/slides.json (template)
```json
[
  {
    "id": 17651,
    "title": "Massive doc refactor (sectionedService.md)",
    "hash": "2562b79",
    "date": "2025-05-15",
    "stat": "1 file, +79 / -1 127",
    "bullets": [
      "Purged obsolete wall-of-text (−1 127 LOC).",
      "Added concise docs for retrieveAllCourseVersions_ms.php + retrieveSectionedService_ms.php.",
      "Improves maintainability and onboarding speed.",
      "Verified: docs render correctly; links valid."
    ],
    "before": "img/17651_before.png",
    "after":  "img/17651_after.png"
  }

  /*  ←--  Duplicate blocks like this for every slide you need.  */
]
````

---

### 3  docs/sem\_ppt\_plan/build\_ppt.py

```python
# -*- coding: utf-8 -*-
"""
Generate supplemental_seminar.pptx from slides.json
Run:  python docs/sem_ppt_plan/build_ppt.py
"""

import json, os, sys
from pptx import Presentation
from pptx.util import Inches, Pt

BASE = os.path.dirname(__file__)
JSON_PATH = os.path.join(BASE, "slides.json")
OUT_PATH  = os.path.join(BASE, "supplemental_seminar.pptx")

def add_title_slide(prs, item):
    slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title & Content
    slide.shapes.title.text = f"Issue/PR {item['id']} – {item['title']}"
    tf = slide.shapes.placeholders[1].text_frame
    tf.clear()  # wipe default bullets

    meta = [
        f"Commit: {item['hash']}",
        f"Date:   {item['date']}",
        f"Δ LOC:  {item['stat']}",
        ""
    ] + item["bullets"]

    for line in meta:
        p = tf.add_paragraph()
        p.text = line
        p.level = 0
        p.font.size = Pt(18)

def add_screenshot_slide(prs, item):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    title_shape = slide.shapes.title
    if title_shape:
        title_shape.text = "Before     →     After"
    left = Inches(0.2)
    top  = Inches(1.2)
    width = Inches(4.8)
    slide.shapes.add_picture(os.path.join(BASE, item["before"]), left, top, width=width)
    slide.shapes.add_picture(os.path.join(BASE, item["after"]),  left + Inches(5.1), top, width=width)

def main():
    try:
        data = json.load(open(JSON_PATH, encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"slides.json not found at {JSON_PATH}")

    prs = Presentation()
    for item in data:
        add_title_slide(prs, item)
        add_screenshot_slide(prs, item)
    prs.save(OUT_PATH)
    print(f"PowerPoint saved → {OUT_PATH}")

if __name__ == "__main__":
    main()
```

---

### 4  docs/sem\_ppt\_plan/ISSUE\_SLIDE\_TEMPLATE.md  *(optional manual route)*

```markdown
# Issue/PR <ID> – <Short title>

**Commit hash:** `<hash>`  
**Date:** `<yyyy-mm-dd>`  
**Files changed / LOC:** `<files>, +xx / -yy`

## What was wrong
- …

## What I changed
- …

## Why it’s better
- …

## Verification
- …

| Before | After |
|:------:|:-----:|
| ![before](img/<id>_before.png) | ![after](img/<id>_after.png) |
```