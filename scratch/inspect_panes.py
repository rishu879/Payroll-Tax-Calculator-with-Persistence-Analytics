import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target_ids = [
    'salary-buddy', 'what-if-raise', 'goal-solver', 'offer-compare',
    'payslip-timeline', 'tax-checklist', 'hra-calc', 'overtime-calc',
    'festival-bonus', 'cashflow-cal', 'ff-settlement', 'onboarding-check',
    'health-score', 'forecast-3m', 'life-events'
]

out = []
for tid in target_ids:
    out.append("=" * 60)
    out.append(f"PANE: pane-{tid}")
    # find starting div
    start_tag = f'<div id="pane-{tid}"'
    idx = text.find(start_tag)
    if idx == -1:
        out.append("MISSING FROM HTML!")
        continue
    # find next view-pane
    next_pane = text.find('class="view-pane', idx + len(start_tag))
    if next_pane == -1:
        next_pane = idx + 2000
    chunk = text[idx:next_pane]
    out.append(chunk[:600])

with open('scratch/panes_preview.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Saved to scratch/panes_preview.txt")
