# -*- coding: utf-8 -*-
"""Parse raw.log and generate slides.json.

Usage: python parse_raw_log.py
This reads docs/sem_ppt_plan/raw.log and writes docs/sem_ppt_plan/slides.json.
"""

import json
import os
import re
from datetime import datetime

BASE_DIR = os.path.join(os.path.dirname(__file__), 'docs', 'sem_ppt_plan')
RAW_LOG = os.path.join(BASE_DIR, 'raw.log')
OUT_JSON = os.path.join(BASE_DIR, 'slides.json')

# Regex helpers
HEADER_RE = re.compile(r'^===\s*log-(\d{4}-\d{2}-\d{2})\.txt\s*===')
DATE_ISO_RE = re.compile(r'^(\d{4}-\d{2}-\d{2})')
DATE_TEXT_RE = re.compile(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})')
ID_RE = re.compile(r'#(\d+)')
COMMIT_RE = re.compile(r'([0-9a-f]{7,40})')

MONTHS = {m.lower(): i for i, m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], 1)}


def parse_date_from_line(line):
    """Return date string YYYY-MM-DD if present in line else None."""
    m = DATE_ISO_RE.match(line)
    if m:
        return m.group(1)
    m = DATE_TEXT_RE.match(line)
    if m:
        day = int(m.group(2))
        month = MONTHS.get(m.group(3).lower())
        year = int(m.group(4))
        if month:
            return f"{year:04d}-{month:02d}-{day:02d}"
    return None


def extract_entry(line, current_date):
    low = line.lower()
    if not any(k in low for k in ('commit', 'pr', 'issue')):
        return None
    if any(k in low for k in ('approved pr', 'status: approved', 'i approve', 'approved pull')) or ('approved' in low and 'pr' in low):
        return None

    id_match = ID_RE.search(line)
    commit_hash = ''
    ident = None
    if id_match:
        ident = id_match.group(1)
    if 'commit' in low:
        c_match = COMMIT_RE.search(line)
        if c_match:
            commit_hash = c_match.group(1)[:7]
            if ident is None:
                ident = commit_hash
    if ident is None:
        return None

    # Determine title: take text after the ID/commit reference if available
    pos = None
    before = ''
    if id_match:
        pos = id_match.end()
        before = line[:id_match.start()].strip(' :–—-')
    elif 'commit' in low and commit_hash:
        c_match = re.search(commit_hash, line)
        if c_match:
            pos = c_match.end()
            before = line[:c_match.start()].strip(' :–—-')
    title = ''
    if pos is not None and pos < len(line):
        title = line[pos:].strip(' :–—-')
    if not title:
        title = before
    title = title.split('(')[0]
    title = title.split('. ')[0].split('.\n')[0]
    title = re.sub(r'https?://\S+', '', title)
    title = title.strip('"\'` —').strip()
    before = re.sub(r'^\d{4}-\d{2}-\d{2}\s*[-—–]*\s*', '', before)
    before = re.sub(r'^[A-Za-z]{3}\s+\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\s*[-—–]*\s*', '', before)
    if not title:
        title = before if before else line.strip()

    return {
        'id': ident,
        'title': title,
        'hash': commit_hash,
        'date': current_date or '',
        'stat': '',
        'bullets': [],
        'before': f"img/{ident}_before.png",
        'after': f"img/{ident}_after.png",
    }


def parse_log(path):
    slides = []
    current_date = ''
    with open(path, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(('[', '*', '-', '•', '>', '|')):
                continue
            m = HEADER_RE.match(line)
            if m:
                current_date = m.group(1)
                continue
            maybe_date = parse_date_from_line(line)
            if maybe_date:
                current_date = maybe_date
            entry = extract_entry(line, current_date)
            if entry:
                slides.append(entry)
    return slides


def main():
    slides = parse_log(RAW_LOG)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(slides, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(slides)} entries to {OUT_JSON}")


if __name__ == '__main__':
    main()
