const fs = require('fs');

console.log("=== Testing All Screens Execution in index.html ===");

const code = fs.readFileSync('scratch/script_1.js', 'utf8');

// Setup mock browser globals
global.window = global;
global.window.addEventListener = function() {};
global.window.scrollTo = function() {};
global.window.location = { href: '', search: '', pathname: '/' };
global.document = {
  body: { classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{} } },
  documentElement: { lang: 'en', setAttribute: function(k, v){ this[k]=v; }, getAttribute: function(k){ return this[k]; } },
  getElementById: function(id) {
    if (!this.elements) this.elements = {};
    if (!this.elements[id]) {
      this.elements[id] = {
        id,
        value: '1500000',
        innerHTML: '',
        innerText: '',
        style: {},
        classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{} },
        dispatchEvent: ()=>{},
        appendChild: ()=>{},
        querySelectorAll: ()=>[],
        querySelector: ()=>null,
        addEventListener: ()=>{}
      };
    }
    return this.elements[id];
  },
  querySelector: function() { return null; },
  querySelectorAll: function() { return []; },
  createElement: function(tag) {
    return {
      tagName: tag,
      id: '',
      className: '',
      style: {},
      classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{} },
      appendChild: ()=>{},
      innerHTML: '',
      innerText: ''
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

// Evaluate full application script
eval(code);

const testScreens = [
  // Existing core screens
  'dashboard', 'tax-calc', 'shop-mode', 'employees', 'payroll',
  'salary-journey', 'tax-detective', 'coin-vault', 'qr-scanner',
  'salary-buddy', 'what-if-raise', 'goal-solver', 'offer-compare',
  'payslip-timeline', 'tax-checklist', 'hra-calc', 'overtime-calc',
  'festival-bonus', 'cashflow-cal', 'ff-settlement', 'onboarding-check',
  'health-score', 'forecast-3m', 'life-events', 'assistant', 'audit-trail', 'settings',
  
  // 12 New Worker Rights & Welfare screens
  'welfare-hub',
  'welfare-fair-pay',
  'welfare-ledger',
  'welfare-benefits',
  'schemes',
  'welfare-schemes',
  'welfare-loan-trap',
  'welfare-women-family',
  'welfare-pulse',
  'welfare-gig-income',
  'welfare-savings-coach',
  'welfare-grievance',
  'welfare-admin-rules',

  // Short aliases
  'welfare', 'fair-pay', 'ledger', 'benefits', 'loan-trap', 'pulse', 'gig-income', 'savings-coach', 'grievance', 'welfare-rules'
];

let okCount = 0, failCount = 0;
for (const sId of testScreens) {
  try {
    showScreen(sId);
    okCount++;
    console.log(`PASS: Screen "${sId}" rendered successfully.`);
  } catch (err) {
    failCount++;
    console.error(`FAIL: Screen "${sId}" threw error:`, err);
  }
}

console.log(`\nScreen Render Summary: ${okCount} passed, ${failCount} failed out of ${testScreens.length} screens.`);
if (failCount > 0) process.exit(1);
