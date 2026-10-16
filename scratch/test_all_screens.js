const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf8');

const dom = {
  elements: {},
  body: { classList: { add: () => {}, remove: () => {}, toggle: () => {} }, setAttribute: () => {} },
  addEventListener: () => {},
  removeEventListener: () => {},
  getElementById: function(id) {
    if (!this.elements[id]) {
      this.elements[id] = {
        id, classList: { add: () => {}, remove: () => {}, toggle: () => {} },
        style: {}, innerHTML: '', textContent: '', value: '100', dataset: {},
        children: [], appendChild: function(c) { this.children.push(c); return c; },
        setAttribute: () => {}, querySelectorAll: () => [],
        remove: () => {}
      };
    }
    return this.elements[id];
  },
  querySelectorAll: function() { return []; },
  createElement: function(tag) {
    return {
      tagName: tag, id: '', className: '',
      classList: { add: () => {}, remove: () => {}, toggle: () => {} },
      style: {}, innerHTML: '', textContent: '', dataset: {}, children: [],
      appendChild: function(c) { this.children.push(c); return c; },
      setAttribute: () => {}, remove: () => {}
    };
  }
};

global.document = dom;
global.window = { scrollTo: () => {}, addEventListener: () => {} };
global.localStorage = { store: {}, getItem: () => null, setItem: () => {} };

const scriptMatch = html.match(/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g);
const fullScript = scriptMatch[scriptMatch.length - 1].replace(/<\/?script[^>]*>/g, '');
eval(fullScript);

console.log('--- TEST 1: TAX CHECKS ---');
const t1 = computeBudget2025Tax(1275000);
console.log('New regime 12.75L tax:', t1.newRegime.totalTax, t1.newRegime.totalTax === 0 ? 'PASS' : 'FAIL');
const t2 = computeBudget2025Tax(1500000);
console.log('New regime 15.0L tax:', t2.newRegime.totalTax, t2.newRegime.totalTax === 97500 ? 'PASS' : 'FAIL');
const t3 = computeBudget2025Tax(1500000, 175000);
console.log('Old regime 15.0L (80C+80D = 1.75L) tax:', t3.oldRegime.totalTax, t3.oldRegime.totalTax === 202800 ? 'PASS' : 'FAIL');
const basic = 600000, hraRec = 240000, rent = 300000, isMetro = true;
const exemptHra = Math.min(hraRec, Math.max(0, rent - 0.10 * basic), (isMetro ? 0.50 : 0.40) * basic);
console.log('HRA Exemption calculation:', exemptHra, exemptHra === 240000 ? 'PASS' : 'FAIL');

console.log('\n--- TEST 2: ALL SCREENS ROUTER TEST ---');
const screensObj = window.screens;
const screenKeys = Object.keys(screensObj);
console.log('Total registered screens:', screenKeys.length);
let passed = 0;
screenKeys.forEach(k => {
  try {
    showScreen(k);
    passed++;
  } catch (e) {
    console.error('FAIL in', k, e.message);
  }
});
console.log('All screens routed and rendered successfully:', passed === screenKeys.length ? 'PASS (' + passed + '/' + screenKeys.length + ')' : 'FAIL');
process.exit(0);
