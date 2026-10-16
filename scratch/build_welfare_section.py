import re
import json

print("Starting Welfare Section builder...")

# Load current index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Verify backup exists
with open("index.html.bak2", "w", encoding="utf-8") as f:
    f.write(html)
print("Backup created at index.html.bak2")

# 1. Update CSS styles for welfare section, RTL support, big buttons, and voice buttons
welfare_css = """
    /* =========================================================================
       WORKER RIGHTS & WELFARE STYLES (A11Y, RTL, VOICE, BIG BUTTONS)
       ========================================================================= */
    [dir="rtl"] { direction: rtl; text-align: right; }
    [dir="rtl"] .card, [dir="rtl"] .view-pane, [dir="rtl"] .form-group, [dir="rtl"] .table-container { text-align: right; }
    [dir="rtl"] .welfare-grid { direction: rtl; }
    [dir="rtl"] #sidebar-dock { border-right: none; border-left: 1px solid var(--border-subtle); }
    [dir="rtl"] .nav-item.active { border-left: none; border-right: 3px solid var(--cinema-orange); }

    .welfare-card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin: 20px 0;
    }
    @media (max-width: 600px) {
      .welfare-card-grid { grid-template-columns: 1fr !important; }
      .welfare-btn-strip { flex-direction: column !important; width: 100% !important; }
      .welfare-big-btn { width: 100% !important; min-height: 52px !important; }
    }
    .welfare-hub-tile {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 24px;
      cursor: pointer;
      transition: var(--transition-smooth);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 220px;
    }
    .welfare-hub-tile:hover {
      transform: translateY(-4px);
      border-color: var(--cinema-gold);
      box-shadow: 0 12px 36px rgba(244, 201, 93, 0.15);
    }
    .welfare-verdict-box {
      border-radius: var(--radius-md);
      padding: 20px;
      margin: 16px 0;
      border: 2px solid;
    }
    .welfare-verdict-green { background: rgba(16, 185, 129, 0.12); border-color: var(--cinema-emerald); color: var(--cinema-emerald); }
    .welfare-verdict-amber { background: rgba(244, 201, 93, 0.12); border-color: var(--cinema-gold); color: var(--cinema-gold); }
    .welfare-verdict-red { background: rgba(244, 63, 94, 0.12); border-color: var(--cinema-crimson); color: var(--cinema-crimson); }
    
    .btn-mic {
      background: rgba(255, 138, 61, 0.15);
      border: 1px solid var(--cinema-orange);
      color: var(--cinema-orange);
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      font-weight: 600;
      transition: all 0.2s ease;
    }
    .btn-mic:hover { background: var(--cinema-orange); color: #000; }
    .btn-mic.listening {
      background: var(--cinema-crimson);
      color: #fff;
      animation: pulseMic 1.2s infinite;
    }
    @keyframes pulseMic { 0% { transform: scale(1); } 50% { transform: scale(1.08); } 100% { transform: scale(1); } }
    
    .btn-read-aloud {
      background: rgba(45, 212, 191, 0.15);
      border: 1px solid var(--cinema-teal);
      color: var(--cinema-teal);
      padding: 8px 16px;
      border-radius: var(--radius-pill);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
      font-size: 13px;
      transition: all 0.2s ease;
    }
    .btn-read-aloud:hover { background: var(--cinema-teal); color: #000; }

    .welfare-legal-notice {
      font-size: 12px;
      color: var(--cinema-muted);
      border-top: 1px solid var(--border-subtle);
      padding-top: 12px;
      margin-top: 20px;
      line-height: 1.6;
    }
    .welfare-step-box {
      background: var(--bg-card-subtle);
      border-left: 4px solid var(--cinema-teal);
      padding: 14px 18px;
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      margin: 12px 0;
      font-size: 14px;
      line-height: 1.6;
    }
    .welfare-checklist-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 14px;
      cursor: pointer;
    }
    .welfare-checklist-item:last-child { border-bottom: none; }
    .welfare-badge-pill {
      display: inline-block;
      padding: 4px 12px;
      border-radius: var(--radius-pill);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
"""

if "WORKER RIGHTS & WELFARE STYLES" not in html:
    html = html.replace("</style>", welfare_css + "\n</style>")
    print("Added Welfare CSS styles.")

# 2. Update Sidebar Navigation in #sidebar-dock
welfare_sidebar = """
      <div class="nav-category" style="color: var(--cinema-gold); letter-spacing: 0.1em;">⚖️ WORKER RIGHTS &amp; WELFARE</div>
      <a class="nav-item" data-screen="welfare-hub" onclick="showScreen('welfare-hub')"><span style="color:var(--cinema-gold);">🏛️</span> Welfare Hub <span class="badge badge-gold" style="font-size:9px; padding:2px 6px; margin-left:4px;">10 Tools</span></a>
      <a class="nav-item" data-screen="welfare-fair-pay" onclick="showScreen('welfare-fair-pay')"><span>⚖️</span> Fair-Pay Checker</a>
      <a class="nav-item" data-screen="welfare-ledger" onclick="showScreen('welfare-ledger')"><span>📒</span> Daily-Wage Ledger</a>
      <a class="nav-item" data-screen="welfare-benefits" onclick="showScreen('welfare-benefits')"><span>🎁</span> Benefits Finder</a>
      <a class="nav-item" data-screen="welfare-schemes" onclick="showScreen('welfare-schemes')"><span>📜</span> Scheme Matcher</a>
      <a class="nav-item" data-screen="welfare-loan-trap" onclick="showScreen('welfare-loan-trap')"><span>🪤</span> Loan Trap Detector</a>
      <a class="nav-item" data-screen="welfare-women-family" onclick="showScreen('welfare-women-family')"><span>🌸</span> Women &amp; Family</a>
      <a class="nav-item" data-screen="welfare-pulse" onclick="showScreen('welfare-pulse')"><span>💓</span> Culture Pulse (Anon)</a>
      <a class="nav-item" data-screen="welfare-gig-income" onclick="showScreen('welfare-gig-income')"><span>🛵</span> Gig &amp; Freelancer</a>
      <a class="nav-item" data-screen="welfare-savings-coach" onclick="showScreen('welfare-savings-coach')"><span>💡</span> Lessons &amp; Savings</a>
      <a class="nav-item" data-screen="welfare-grievance" onclick="showScreen('welfare-grievance')"><span>📢</span> Grievance Helper</a>
      <a class="nav-item pro-only" data-screen="welfare-admin-rules" onclick="showScreen('welfare-admin-rules')"><span>⚙️</span> Rules &amp; Data</a>
"""

if 'data-screen="welfare-hub"' not in html:
    html = html.replace('<div class="nav-category">ASSIST &amp; SETTINGS</div>', welfare_sidebar + '\n      <div class="nav-category">ASSIST &amp; SETTINGS</div>')
    print("Added Welfare Sidebar Navigation items.")

# 3. Add View Panes into #main-content
welfare_panes = """
      <!-- =======================================================================
           VIEW: WELFARE HUB (10 BIG CARDS OVERVIEW)
           ======================================================================= -->
      <div id="pane-welfare-hub" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 1. FAIR-PAY CHECKER
           ======================================================================= -->
      <div id="pane-welfare-fair-pay" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 2. DOMESTIC & DAILY-WAGE LEDGER
           ======================================================================= -->
      <div id="pane-welfare-ledger" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 3. BENEFITS FINDER
           ======================================================================= -->
      <div id="pane-welfare-benefits" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 4. GOVERNMENT SCHEME MATCHER
           ======================================================================= -->
      <div id="pane-welfare-schemes" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 5. LOAN TRAP DETECTOR
           ======================================================================= -->
      <div id="pane-welfare-loan-trap" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 6. WOMEN & FAMILY SUPPORT
           ======================================================================= -->
      <div id="pane-welfare-women-family" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 7. WORK-CULTURE PULSE (ANONYMOUS)
           ======================================================================= -->
      <div id="pane-welfare-pulse" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 8. GIG & FREELANCER INCOME HELPER
           ======================================================================= -->
      <div id="pane-welfare-gig-income" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 9. MONEY LESSONS & SAVINGS COACH
           ======================================================================= -->
      <div id="pane-welfare-savings-coach" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: 10. GRIEVANCE HELPER
           ======================================================================= -->
      <div id="pane-welfare-grievance" class="view-pane"></div>

      <!-- =======================================================================
           VIEW: WELFARE ADMIN RULES & DATA EDITOR
           ======================================================================= -->
      <div id="pane-welfare-admin-rules" class="view-pane"></div>
"""

if 'id="pane-welfare-hub"' not in html:
    html = html.replace('    </section>\n  </div>', welfare_panes + '\n    </section>\n  </div>')
    print("Added 12 Welfare View Panes into #main-content.")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Saved HTML with styles, sidebar, and panes.")
