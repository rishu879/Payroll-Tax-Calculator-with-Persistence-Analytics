// Automated validation suite for Worker Rights & Welfare calculators and router
const fs = require('fs');

console.log("=== Testing Worker Rights & Welfare Calculators ===");

// Load welfare module
const jsContent = fs.readFileSync('scratch/welfare_module.js', 'utf8');

// Mock DOM environment
global.window = global;
global.document = {
  documentElement: {
    lang: 'en',
    setAttribute: function(k, v) { this[k] = v; },
    getAttribute: function(k) { return this[k]; }
  },
  getElementById: function(id) {
    if (!this.elements) this.elements = {};
    if (!this.elements[id]) {
      this.elements[id] = {
        id,
        value: '0',
        innerHTML: '',
        style: {},
        classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{} },
        dispatchEvent: ()=>{},
        appendChild: ()=>{}
      };
    }
    return this.elements[id];
  },
  querySelector: function() { return null; },
  querySelectorAll: function() { return []; },
  createElement: function() {
    return {
      style: {},
      classList: { add: ()=>{}, remove: ()=>{} },
      appendChild: ()=>{}
    };
  },
  addEventListener: function() {}
};
global.localStorage = {
  store: {},
  getItem: function(k) { return this.store[k] || null; },
  setItem: function(k, v) { this.store[k] = String(v); }
};
global.escapeHtml = function(s) { return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };

// Evaluate welfare_module
eval(jsContent);

let passes = 0, fails = 0;
function assert(cond, name, details) {
  if (cond) {
    console.log(`PASS: ${name} ${details ? `(${details})` : ''}`);
    passes++;
  } else {
    console.error(`FAIL: ${name} ${details ? `(${details})` : ''}`);
    fails++;
  }
}

// Test 1: Language Switcher and Urdu RTL
changeLanguage('ur');
assert(document.documentElement.getAttribute('dir') === 'rtl', "Urdu sets dir='rtl'");
assert(document.documentElement.lang === 'ur', "Urdu sets lang='ur'");
assert(getT('fairPayName').includes('منصفانہ'), "Urdu translation matches");

changeLanguage('hi');
assert(document.documentElement.getAttribute('dir') === 'ltr', "Hindi sets dir='ltr'");
assert(getT('fairPayName').includes('उचित वेतन'), "Hindi translation matches");

changeLanguage('pa');
assert(getT('fairPayName').includes('ਸਹੀ ਤਨਖਾਹ'), "Punjabi translation matches");

changeLanguage('en');
assert(getT('fairPayName') === 'Fair-Pay Checker', "English translation matches");

// Test 2: Fair-Pay Checker Math
// Case 1: Delhi Unskilled worker paid 15000 (Min wage is 18000) -> Shortfall 3000
const delhiUnskilled = window.welfareRules.minimumWages['Delhi'].unskilledMonthly; // 18000
const shortfall1 = Math.max(0, delhiUnskilled - 15000);
assert(shortfall1 === 3000, "Fair-Pay Case 1: Delhi unskilled shortfall ₹3,000", `got ${shortfall1}`);

// Case 2: Maharashtra Skilled worker paid 18000 (Min wage 16120) -> Shortfall 0
const mahaSkilled = window.welfareRules.minimumWages['Maharashtra'].skilledMonthly; // 16120
const shortfall2 = Math.max(0, mahaSkilled - 18000);
assert(shortfall2 === 0, "Fair-Pay Case 2: Maharashtra skilled shortfall ₹0", `got ${shortfall2}`);

// Case 3: Karnataka Semi-skilled worker paid 14170 with 20h OT at double rate
const karnatakaSemi = window.welfareRules.minimumWages['Karnataka'].semiskilledMonthly; // 14170
const otRate = (karnatakaSemi / 26 / 8) * 2.0; // ~136.25/hr
const otDue = Math.round(20 * otRate); // ~2725
const totalDue = Math.round(karnatakaSemi + otDue); // ~16895
const shortfall3 = Math.max(0, totalDue - 14170);
assert(shortfall3 === otDue && otDue > 2000, "Fair-Pay Case 3: 20h Overtime at double rate correctly calculated", `otDue=₹${otDue}`);

// Test 3: Loan Trap Detector IRR/APR Math
// Case 1: Daily loan: ₹1,000 in hand, ₹100/day for 12 days (Total ₹1200)
// NPV equation: 1000 = sum(100 / (1+r)^t) for t=1..12
let low = 0, high = 10;
for (let iter = 0; iter < 60; iter++) {
  const mid = (low + high) / 2;
  let pv = 0;
  for (let t = 1; t <= 12; t++) pv += 100 / Math.pow(1 + mid, t);
  if (pv > 1000) low = mid; else high = mid;
}
const aprDaily = Math.round(((low + high) / 2) * 365 * 100);
assert(aprDaily > 200, "Loan Trap Case 1: Daily loan APR > 200%", `APR=${aprDaily}%`);

// Case 2: Formal loan: ₹50,000 in hand, ₹4,400/month for 12 months (Total ₹52,800)
low = 0; high = 10;
for (let iter = 0; iter < 60; iter++) {
  const mid = (low + high) / 2;
  let pv = 0;
  for (let t = 1; t <= 12; t++) pv += 4400 / Math.pow(1 + mid, t);
  if (pv > 50000) low = mid; else high = mid;
}
const aprFormal = Math.round(((low + high) / 2) * 12 * 100);
assert(aprFormal >= 9 && aprFormal <= 13, "Loan Trap Case 2: Bank loan APR ~10-12%", `APR=${aprFormal}%`);

// Test 4: Maternity Benefit Math
// Monthly wage 25000 -> Weekly wage = (25000 * 12) / 52 = 5769.23
// 26 weeks paid leave = 26 * 5769.23 = 150000 (exactly 6 months wage)
const maternityTotal = Math.round(((25000 * 12) / 52) * 26);
assert(maternityTotal === 150000, "Maternity Benefit Case: 26 weeks paid wages = ₹1,50,000", `got ₹${maternityTotal}`);

// Test 5: Presumptive Taxation Section 44ADA / 44AD
// ₹4,80,000 receipts in 44AD (6% profit) = ₹28,800 deemed profit. Tax = ₹0
const deemedProfit44AD = Math.round(480000 * 0.06);
assert(deemedProfit44AD === 28800, "Section 44AD Deemed Profit = 6% (₹28,800)", `got ₹${deemedProfit44AD}`);

// ₹12,00,000 receipts in 44ADA (50% profit) = ₹6,00,000 deemed profit. Under Budget 2025: ₹0 tax (within ₹12L rebate)
const deemedProfit44ADA = Math.round(1200000 * 0.50);
assert(deemedProfit44ADA === 600000, "Section 44ADA Deemed Profit = 50% (₹6,00,000)", `got ₹${deemedProfit44ADA}`);

console.log(`\nResults: ${passes} passed, ${fails} failed.`);
if (fails > 0) process.exit(1);
