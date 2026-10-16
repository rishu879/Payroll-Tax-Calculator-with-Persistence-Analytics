const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, 'dist');

// Clean and recreate dist directory
if (fs.existsSync(distDir)) {
  fs.rmSync(distDir, { recursive: true, force: true });
}
fs.mkdirSync(distDir, { recursive: true });

// Core static assets to copy to dist
const filesToCopy = [
  'index.html',
  'style.css',
  'sample-statement.csv',
  'paypilot-data.json'
];

for (const file of filesToCopy) {
  const src = path.join(__dirname, file);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.join(distDir, file));
    console.log(`Copied ${file} -> dist/${file}`);
  }
}

// Generate Netlify _redirects file
const backendUrl = (process.env.BACKEND_API_URL || '').replace(/\/$/, '');
let redirects = '';
if (backendUrl) {
  redirects += `/api/*  ${backendUrl}/api/:splat  200!\n`;
  console.log(`Configured backend proxy: /api/* -> ${backendUrl}/api/*`);
}
redirects += `/*  /index.html  200\n`;

fs.writeFileSync(path.join(distDir, '_redirects'), redirects);
console.log('Generated dist/_redirects successfully.');
console.log('Build completed successfully.');
