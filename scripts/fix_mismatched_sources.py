#!/usr/bin/env python3
"""Fetch correct content for mismatched arXiv papers via ar5iv HTML."""
import os
import subprocess
import sys
import time

MISMATCHED = [
    '2012.13401',
    '2104.02796',
    '2209.01113',
    '2209.01062',
    '2104.01506',
    '1811.10927',
    '2105.09206',
    '2103.01799',
    '1907.11714',
    '1711.07576',
    '0709.1542',
    '2012.12965',
]

PYTHON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.venv', 'bin', 'python')
EXTRACT_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authenticated_extract.py')
WEBPAGE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webpage_to_md.py')

def fetch_paper(arxiv_id: str) -> bool:
    dest_dir = f'sources/arxiv-{arxiv_id}'
    out_file = f'{dest_dir}/content.md'

    # Try ar5iv (HTML version of arXiv)
    url = f'https://ar5iv.labs.arxiv.org/html/{arxiv_id}'
    for script in [EXTRACT_SCRIPT, WEBPAGE_SCRIPT]:
        if not os.path.isfile(script):
            continue
        try:
            r = subprocess.run(
                [PYTHON, script, url],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode == 0 and len(r.stdout) > 1000:
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(r.stdout)
                print(f'  OK via ar5iv ({len(r.stdout)} chars): {arxiv_id}')
                return True
        except subprocess.TimeoutExpired:
            print(f'  TIMEOUT: {script} on {arxiv_id}')
        except Exception as e:
            print(f'  ERR ({script}): {e}')

    # Fallback: arXiv abstract page
    url_abs = f'https://arxiv.org/abs/{arxiv_id}'
    for script in [EXTRACT_SCRIPT, WEBPAGE_SCRIPT]:
        if not os.path.isfile(script):
            continue
        try:
            r = subprocess.run(
                [PYTHON, script, url_abs],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode == 0 and len(r.stdout) > 500:
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(r.stdout)
                print(f'  OK via arXiv abstract ({len(r.stdout)} chars): {arxiv_id}')
                return True
        except subprocess.TimeoutExpired:
            print(f'  TIMEOUT abs: {arxiv_id}')
        except Exception as e:
            print(f'  ERR abs ({script}): {e}')

    print(f'  FAILED all methods: {arxiv_id}')
    return False


if __name__ == '__main__':
    ok = 0
    fail = 0
    for arxiv_id in MISMATCHED:
        print(f'Fetching arxiv-{arxiv_id} ...')
        if fetch_paper(arxiv_id):
            ok += 1
        else:
            fail += 1
        time.sleep(1)  # be polite
    print(f'\nDone: {ok} OK, {fail} failed')
