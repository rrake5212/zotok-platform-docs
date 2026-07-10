// Post-build script: Copy index.html as 404.html for GitHub Pages SPA fallback
import fs from 'fs';
fs.copyFileSync('dist/index.html', 'dist/404.html');
console.log('Created dist/404.html for SPA fallback');
