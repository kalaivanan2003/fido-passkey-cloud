"""
Inject responsive.css link into all HTML templates that load style-starter.css.
Run once:  python add_responsive_css.py
"""
import os, re

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
INJECT_TAG = '    <link rel="stylesheet" href="../static/assets/css/responsive.css">'

changed = []
skipped = []

for root, dirs, files in os.walk(TEMPLATES_DIR):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        path = os.path.join(root, fname)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        if any('responsive.css' in l for l in lines):
            skipped.append(fname)
            continue

        # Find line index of style-starter.css
        idx = next((i for i, l in enumerate(lines) if 'style-starter.css' in l), None)
        if idx is None:
            skipped.append(fname)
            continue

        # Insert responsive.css on the next line
        lines.insert(idx + 1, INJECT_TAG + '\n')
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        changed.append(fname)

print(f"\n[OK] Injected responsive.css into {len(changed)} templates:")
for f in changed: print(f"   + {f}")

if skipped:
    print(f"\n[SKIP] Skipped {len(skipped)} files (already done or no style-starter.css):")
    for f in skipped: print(f"   - {f}")
