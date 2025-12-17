#!/usr/bin/env python3

# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""Simple markdown checks used by the docs-lint GitHub Action.
Checks:
 - No trailing whitespace
 - No tabs
 - Max line length 120
 - Files under docs/ and README.md
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('paths', nargs='*', help='Optional list of files to check')
args = parser.parse_args()

if args.paths:
    paths = [Path(p) for p in args.paths]
else:
    paths = list(ROOT.glob('docs/**/*.md')) + [ROOT / 'README.md']
errors = []
for p in paths:
    try:
        text = p.read_text(encoding='utf-8').splitlines()
    except Exception as e:
        errors.append(f'FAIL: Could not read {p}: {e}')
        continue
    for i, line in enumerate(text, start=1):
        if '\t' in line:
            errors.append(f'{p}:{i}: contains tab character')
        if line.rstrip('\n').endswith(' '):
            errors.append(f'{p}:{i}: trailing whitespace')
        if len(line) > 120:
            errors.append(f'{p}:{i}: line too long ({len(line)} chars)')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('OK')
