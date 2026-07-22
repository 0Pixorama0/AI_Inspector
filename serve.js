const http = require('http');
const fs = require('fs');
const path = require('path');

const root = __dirname;
const types = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

http.createServer((req, res) => {
  const [rawPath, query] = req.url.split('?');
  let p = decodeURIComponent(rawPath);
  if (p === '/') p = '/index.html';
  const file = path.join(root, p);
  if (!file.startsWith(root)) { res.writeHead(403); res.end('forbidden'); return; }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); res.end('not found'); return; }
    const ext = path.extname(file).toLowerCase();

    // Review aid: /?only=timeline renders that section alone, at the top of the
    // page, so a headless screenshot can inspect it without scrolling.
    const only = new URLSearchParams(query || '').get('only');
    if (ext === '.html' && only && /^[\w-]+$/.test(only)) {
      data = Buffer.from(String(data).replace(
        '</head>',
        `<style>section,footer{display:none !important}
         #${only}{display:block !important}
         #${only}{padding-top:48px !important}</style></head>`
      ));
    }

    res.writeHead(200, {
      'Content-Type': types[ext] || 'application/octet-stream',
      'Cache-Control': 'no-store',
    });
    res.end(data);
  });
}).listen(4610, () => console.log('proposal preview on http://localhost:4610'));
