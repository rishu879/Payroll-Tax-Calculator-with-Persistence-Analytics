# -*- coding: utf-8 -*-
import sys

print("Appending screen renderers to welfare_module.js...")

with open("scratch/welfare_module.js", "a", encoding="utf-8") as f:
    f.write(r'''
    // =========================================================================
    // 7. WELFARE HUB OVERVIEW SCREEN (10 BIG ACTION CARDS)
    // =========================================================================
    function renderWelfareHub(pane) {
      if (!pane) return;
      const r = window.welfareRules || DEFAULT_WELFARE_RULES;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
              <span class="welfare-badge-pill" style="background: rgba(244, 201, 93, 0.2); color: var(--cinema-gold); border: 1px solid var(--cinema-gold); margin-bottom: 8px;">
                🏛️ ${getT('welfareTitle')}
              </span>
              <h2 style="color: var(--cinema-cream); margin-top: 6px; font-family: var(--font-headline); letter-spacing: 0.5px;">
                ${getT('welfareTitle')}
              </h2>
              <p style="color: var(--cinema-muted); font-size: 15px; max-width: 800px; margin-top: 4px;">
                ${getT('welfareSubtitle')}
              </p>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
              <button class="btn-read-aloud" onclick="readAloudText('${getT('welfareTitle')}. ${getT('welfareSubtitle')}')">
                ${getT('readAloud')}
              </button>
            </div>
          </div>
        </div>

        <!-- 10 Big Cards Grid -->
        <div class="welfare-card-grid">
          <!-- 1. Fair-Pay Checker -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-fair-pay')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">⚖️</div>
              <h3 style="color: var(--cinema-orange); margin-bottom: 8px;">1. ${getT('fairPayName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('fairPayDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-orange welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 2. Domestic & Daily Ledger -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-ledger')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">📒</div>
              <h3 style="color: var(--cinema-teal); margin-bottom: 8px;">2. ${getT('ledgerName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('ledgerDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-teal welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 3. Benefits Finder -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-benefits')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">🎁</div>
              <h3 style="color: var(--cinema-gold); margin-bottom: 8px;">3. ${getT('benefitsName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('benefitsDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-gold welfare-big-btn" style="width: 100%; color:#000;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 4. Scheme Matcher -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-schemes')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">📜</div>
              <h3 style="color: var(--cinema-emerald); margin-bottom: 8px;">4. ${getT('schemesName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('schemesDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-teal welfare-big-btn" style="width: 100%; background: var(--cinema-emerald); border-color: var(--cinema-emerald); color:#000;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 5. Loan Trap Detector -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-loan-trap')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">🪤</div>
              <h3 style="color: var(--cinema-crimson); margin-bottom: 8px;">5. ${getT('loanTrapName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('loanTrapDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-glass welfare-big-btn" style="width: 100%; border-color: var(--cinema-crimson); color: var(--cinema-crimson);">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 6. Women & Family Support -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-women-family')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">🌸</div>
              <h3 style="color: #F472B6; margin-bottom: 8px;">6. ${getT('womenFamilyName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('womenFamilyDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-glass welfare-big-btn" style="width: 100%; border-color: #F472B6; color: #F472B6;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 7. Work-Culture Pulse -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-pulse')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">💓</div>
              <h3 style="color: var(--cinema-teal); margin-bottom: 8px;">7. ${getT('pulseName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('pulseDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-teal welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 8. Gig & Freelancer Income -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-gig-income')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">🛵</div>
              <h3 style="color: var(--cinema-orange); margin-bottom: 8px;">8. ${getT('gigIncomeName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('gigIncomeDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-orange welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 9. Money Lessons & Savings Coach -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-savings-coach')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">💡</div>
              <h3 style="color: var(--cinema-gold); margin-bottom: 8px;">9. ${getT('savingsCoachName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('savingsCoachDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-gold welfare-big-btn" style="width: 100%; color:#000;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 10. Grievance Helper -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-grievance')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">📢</div>
              <h3 style="color: var(--cinema-cream); margin-bottom: 8px;">10. ${getT('grievanceName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('grievanceDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-glass welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;
    }

    // =========================================================================
    // 8. SCREEN 1: FAIR-PAY CHECKER
    // =========================================================================
    function renderFairPay(pane) {
      if (!pane) return;
      const r = window.welfareRules || DEFAULT_WELFARE_RULES;
      const states = Object.keys(r.minimumWages || DEFAULT_WELFARE_RULES.minimumWages);

      let stateOptions = states.map(st => `<option value="${st}" ${st === 'Delhi' ? 'selected' : ''}>${st}</option>`).join('');

      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-orange);">⚖️ ${getT('fairPayName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">${getT('fairPayDesc')}</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-fairpay">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Input Card -->
          <div class="card">
            <h3 style="color: var(--cinema-orange); margin-bottom: 16px;">1. Enter Work &amp; Pay Details</h3>
            
            <div class="form-group">
              <label class="form-label">${getT('state')}</label>
              <select class="form-control" id="fp-state" onchange="calculateFairPay()">${stateOptions}</select>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('skillLevel')}</label>
                <select class="form-control" id="fp-skill" onchange="calculateFairPay()">
                  <option value="unskilled">${getT('unskilled')}</option>
                  <option value="semiskilled">${getT('semiSkilled')}</option>
                  <option value="skilled" selected>${getT('skilled')}</option>
                  <option value="highlySkilled">${getT('highlySkilled')}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">${getT('payType')}</label>
                <select class="form-control" id="fp-pay-type" onchange="calculateFairPay()">
                  <option value="monthly" selected>${getT('monthly')}</option>
                  <option value="daily">${getT('daily')}</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <label class="form-label" style="margin:0;">${getT('amountPaid')}</label>
                <button type="button" class="btn-mic" data-mic-for="fp-amount" onclick="startVoiceInput('fp-amount')">🎤 ${getT('speakMic')}</button>
              </div>
              <input type="number" class="form-control font-mono" id="fp-amount" value="18000" oninput="calculateFairPay()">
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('hoursPerDay')}</label>
                <input type="number" class="form-control font-mono" id="fp-hours" value="8" min="1" max="16" oninput="calculateFairPay()">
              </div>
              <div class="form-group">
                <label class="form-label">${getT('daysPerWeek')}</label>
                <input type="number" class="form-control font-mono" id="fp-days-week" value="6" min="1" max="7" oninput="calculateFairPay()">
              </div>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('overtimeHours')}</label>
                <input type="number" class="form-control font-mono" id="fp-ot-hours" value="0" min="0" oninput="calculateFairPay()">
              </div>
              <div class="form-group">
                <label class="form-label">${getT('payDate')}</label>
                <input type="number" class="form-control font-mono" id="fp-pay-date" value="7" min="1" max="31" oninput="calculateFairPay()">
              </div>
            </div>
          </div>

          <!-- Result Output Card -->
          <div class="card card-glow-orange" id="fp-result-card">
            <!-- Rendered by calculateFairPay() -->
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-fairpay').onclick = () => {
        const text = document.getElementById('fp-result-speech-text')?.innerText || getT('fairPayDesc');
        readAloudText(text);
      };

      calculateFairPay();
    }

    function calculateFairPay() {
      try {
        const r = window.welfareRules || DEFAULT_WELFARE_RULES;
        const state = document.getElementById('fp-state')?.value || 'Delhi';
        const skill = document.getElementById('fp-skill')?.value || 'unskilled';
        const payType = document.getElementById('fp-pay-type')?.value || 'monthly';
        const amount = parseFloat(document.getElementById('fp-amount')?.value || 0);
        const hours = parseFloat(document.getElementById('fp-hours')?.value || 8);
        const daysPerWeek = parseFloat(document.getElementById('fp-days-week')?.value || 6);
        const otHours = parseFloat(document.getElementById('fp-ot-hours')?.value || 0);
        const payDate = parseFloat(document.getElementById('fp-pay-date')?.value || 7);

        const stateWages = (r.minimumWages && r.minimumWages[state]) || DEFAULT_WELFARE_RULES.minimumWages['Delhi'];
        
        let minMonthly = 0, minDaily = 0;
        if (skill === 'unskilled') { minMonthly = stateWages.unskilledMonthly; minDaily = stateWages.unskilledDaily; }
        else if (skill === 'semiskilled') { minMonthly = stateWages.semiskilledMonthly; minDaily = stateWages.semiskilledDaily; }
        else if (skill === 'skilled') { minMonthly = stateWages.skilledMonthly; minDaily = stateWages.skilledDaily; }
        else { minMonthly = stateWages.highlySkilledMonthly; minDaily = stateWages.highlySkilledDaily; }

        const baseStatutoryWage = payType === 'monthly' ? minMonthly : (minDaily * 26);
        const dailyRate = minDaily > 0 ? minDaily : (minMonthly / 26);
        const hourlyRate = dailyRate / 8;
        const otDue = Math.round(otHours * hourlyRate * 2.0); // Double rate under Indian Labour Act
        const totalStatutoryDue = Math.round(baseStatutoryWage + otDue);

        const shortfall = Math.max(0, totalStatutoryDue - amount);

        let verdict = 'green', verdictClass = 'welfare-verdict-green', verdictTitle = getT('verdictGreen');
        if (amount < baseStatutoryWage) {
          verdict = 'red';
          verdictClass = 'welfare-verdict-red';
          verdictTitle = getT('verdictRed');
        } else if (shortfall > 0 || payDate > 10 || daysPerWeek > 6) {
          verdict = 'amber';
          verdictClass = 'welfare-verdict-amber';
          verdictTitle = getT('verdictAmber');
        }

        // Ready message for boss
        const bossMessage = `Namaste ji, As per the official minimum wage notification for ${state} (${skill} category), the statutory minimum wage is ₹${baseStatutoryWage.toLocaleString('en-IN')}/month. With ${otHours} hours of overtime at statutory double-rate (₹${otDue.toLocaleString('en-IN')}), the total due is ₹${totalStatutoryDue.toLocaleString('en-IN')}. My current wage is ₹${amount.toLocaleString('en-IN')}. Please adjust the difference of ₹${shortfall.toLocaleString('en-IN')} as per labour department rules. Thank you.`;

        const speechSummary = `${verdictTitle}. Statutory minimum wage for ${state} is ₹${baseStatutoryWage}. Total due including overtime is ₹${totalStatutoryDue}. You received ₹${amount}. Shortfall is ₹${shortfall}.`;

        const outCard = document.getElementById('fp-result-card');
        if (!outCard) return;

        outCard.innerHTML = `
          <div id="fp-result-speech-text" style="display:none;">${escapeHtml(speechSummary)}</div>
          
          <div class="welfare-verdict-box ${verdictClass}">
            <h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 800;">${verdictTitle}</h3>
            <div style="font-size: 28px; font-weight: 800; font-family: var(--font-mono); margin: 6px 0;">
              ${shortfall > 0 ? `Shortfall: -₹${shortfall.toLocaleString('en-IN')}` : `Fair Pay ✓ No Shortfall`}
            </div>
            <div style="font-size: 13px; opacity: 0.9;">
              ${payDate > 10 ? `⚠️ Late payment: Wages paid on day ${payDate} (Law requires payment by 7th or 10th of month).` : ''}
              ${daysPerWeek > 6 ? `⚠️ Missing weekly rest day: Working 7 days/week without paid holiday violates the Minimum Wages Act.` : ''}
            </div>
          </div>

          <h4 style="color: var(--cinema-cream); margin: 16px 0 10px 0;">${getT('numbersUsed')}</h4>
          <div class="table-container" style="margin-bottom: 16px;">
            <table>
              <tr><td>State &amp; Category:</td><td class="font-mono"><strong>${state} (${skill})</strong></td></tr>
              <tr><td>Base Minimum Wage:</td><td class="font-mono">₹${baseStatutoryWage.toLocaleString('en-IN')} / mo</td></tr>
              <tr><td>Overtime Due (${otHours} hrs @ 2x rate):</td><td class="font-mono">₹${otDue.toLocaleString('en-IN')}</td></tr>
              <tr><td>Total Statutory Amount Due:</td><td class="font-mono" style="color:var(--cinema-gold);">₹${totalStatutoryDue.toLocaleString('en-IN')}</td></tr>
              <tr><td>Actual Amount Paid:</td><td class="font-mono">₹${amount.toLocaleString('en-IN')}</td></tr>
              <tr><td>Net Monthly Shortfall:</td><td class="font-mono" style="color:${shortfall > 0 ? 'var(--cinema-crimson)' : 'var(--cinema-emerald)'}; font-weight:700;">₹${shortfall.toLocaleString('en-IN')}</td></tr>
            </table>
          </div>

          <h4 style="color: var(--cinema-teal); margin-bottom: 8px;">${getT('whatToDoNext')}</h4>
          <div class="welfare-step-box">
            ${shortfall > 0 
              ? `1. Show the calculation and polite message below to your employer.<br>2. Keep bank passbook or cash receipts as proof of payment.<br>3. If unresolved, call the National Labour Helpline at <strong>14434</strong> or submit on SAMADHAAN portal.`
              : `1. Your wage meets the statutory minimum wage standards.<br>2. Ensure regular PF (12%) and ESI contributions are deposited in your UAN account.<br>3. Request a signed salary slip each month.`}
          </div>

          <div style="margin-top: 16px;">
            <label class="form-label" style="color: var(--cinema-gold);">${getT('msgToBossTitle')}</label>
            <textarea class="form-control" id="fp-boss-msg" rows="3" style="font-size: 12px; margin-bottom: 12px;" readonly>${bossMessage}</textarea>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
              <button class="btn btn-teal" onclick="copyWelfareText(document.getElementById('fp-boss-msg').value, this)">
                ${getT('copyText')}
              </button>
              <button class="btn btn-orange" onclick="shareWelfareWhatsApp(document.getElementById('fp-boss-msg').value)">
                ${getT('shareWhatsApp')}
              </button>
            </div>
          </div>
        `;
      } catch (err) {
        console.error('Fair-Pay calculation error:', err);
      }
    }
''')

print("Fair-Pay checker written.")
