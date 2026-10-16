import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target_ids = [
    'salary-buddy', 'what-if-raise', 'goal-solver', 'offer-compare',
    'hra-calc', 'overtime-calc', 'festival-bonus', 'ff-settlement',
    'onboarding-check', 'health-score', 'forecast-3m', 'life-events'
]

for tid in target_ids:
    m = re.search(r'(<div\s+id="pane-' + re.escape(tid) + r'"\s+class="view-pane".*?)(?=<div\s+id="pane-|</section>)', text, re.DOTALL)
    if m:
        content = m.group(1).strip()
        with open(f'scratch/pane_{tid}.html', 'w', encoding='utf-8') as pf:
            pf.write(content)
        print(f"Wrote scratch/pane_{tid}.html ({len(content)} chars)")
    else:
        print(f"Could not find pane-{tid}")
