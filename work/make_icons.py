#!/usr/bin/env python3
"""Turn the four supplied artwork PNGs into square, transparent stat icons.

Each source is a poster: a title line at the top, then the artwork, on white.
We drop the title band (the copy goes into HTML instead), knock the white
background out to transparent, and centre the artwork on a square canvas so
all four render at a consistent visual size in the 80x80 slot.
"""
from playwright.sync_api import sync_playwright
import base64, pathlib, json

OUT = pathlib.Path('goldreach/assets')
NAMES = {'1': 'stat-team.png', '2': 'stat-views.png',
         '3': 'stat-years.png', '4': 'stat-content.png'}
SIZE = 400          # exported square, ~5x the 80px display slot

JS = r"""
async ({src, SIZE}) => {
  const img = new Image();
  await new Promise((res, rej) => { img.onload = res; img.onerror = rej; img.src = src; });

  // 1. work at a manageable resolution
  const scale = Math.min(1, 1000 / Math.max(img.naturalWidth, img.naturalHeight));
  const W = Math.round(img.naturalWidth * scale), H = Math.round(img.naturalHeight * scale);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const x = c.getContext('2d');
  x.fillStyle = '#fff'; x.fillRect(0, 0, W, H);        // flatten any existing alpha onto white
  x.drawImage(img, 0, 0, W, H);
  let d = x.getImageData(0, 0, W, H).data;

  const isInk = i => !(d[i] > 244 && d[i+1] > 244 && d[i+2] > 244);

  // 2. row bands of ink -> first band is the title line, drop it
  const rowInk = [];
  for (let y = 0; y < H; y++) {
    let n = 0;
    for (let px = 0; px < W; px++) if (isInk((y*W + px)*4)) n++;
    rowInk.push(n);
  }
  const minInk = Math.max(3, W * 0.002);
  const bands = [];
  let s = null;
  for (let y = 0; y < H; y++) {
    if (rowInk[y] > minInk) { if (s === null) s = y; }
    else if (s !== null) { bands.push([s, y-1]); s = null; }
  }
  if (s !== null) bands.push([s, H-1]);
  // merge bands separated by tiny gaps (letter descenders etc.)
  const merged = [];
  for (const b of bands) {
    if (merged.length && b[0] - merged[merged.length-1][1] < H * 0.02) merged[merged.length-1][1] = b[1];
    else merged.push([...b]);
  }
  let art = merged;
  if (merged.length > 1 && merged[0][1] < H * 0.30) art = merged.slice(1);   // drop the title
  const y0 = art[0][0], y1 = art[art.length-1][1];

  // 3. column bounds within the artwork rows
  let x0 = W, x1 = 0;
  for (let y = y0; y <= y1; y++)
    for (let px = 0; px < W; px++)
      if (isInk((y*W + px)*4)) { if (px < x0) x0 = px; if (px > x1) x1 = px; }

  const cw = x1 - x0 + 1, ch = y1 - y0 + 1;
  const crop = document.createElement('canvas'); crop.width = cw; crop.height = ch;
  crop.getContext('2d').drawImage(c, x0, y0, cw, ch, 0, 0, cw, ch);

  // 4. flood-fill the white background from the edges -> transparent
  const cc = crop.getContext('2d');
  const im = cc.getImageData(0, 0, cw, ch);
  const p = im.data;
  const white = i => p[i] > 240 && p[i+1] > 240 && p[i+2] > 240;
  const seen = new Uint8Array(cw * ch);
  const stack = [];
  for (let px = 0; px < cw; px++) { stack.push(px); stack.push((ch-1)*cw + px); }
  for (let y = 0; y < ch; y++)   { stack.push(y*cw); stack.push(y*cw + cw - 1); }
  while (stack.length) {
    const k = stack.pop();
    if (seen[k]) continue;
    const i = k*4;
    if (!white(i)) continue;
    seen[k] = 1; p[i+3] = 0;
    const px = k % cw, py = (k - px) / cw;
    if (px > 0)    stack.push(k-1);
    if (px < cw-1) stack.push(k+1);
    if (py > 0)    stack.push(k-cw);
    if (py < ch-1) stack.push(k+cw);
  }
  cc.putImageData(im, 0, 0);

  // 5. export tight — no square padding, so CSS height normalisation gives
  //    every artwork the same optical height regardless of aspect ratio
  const k = Math.min(SIZE / cw, SIZE / ch, 1);
  const out = document.createElement('canvas');
  out.width = Math.round(cw * k); out.height = Math.round(ch * k);
  const oc = out.getContext('2d');
  oc.imageSmoothingQuality = 'high';
  oc.drawImage(crop, 0, 0, out.width, out.height);

  return {png: out.toDataURL('image/png'), cropped: [cw, ch],
          exported: [out.width, out.height],
          bands: merged.length, droppedTitle: art !== merged};
}
"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page()
    pg.goto('http://127.0.0.1:8081/', wait_until='domcontentloaded')
    for num, name in NAMES.items():
        r = pg.evaluate(JS, {'src': f'/assets/_src/{num}.png', 'SIZE': SIZE})
        data = base64.b64decode(r['png'].split(',', 1)[1])
        (OUT / name).write_bytes(data)
        print(f"{name:20} crop={r['cropped'][0]}x{r['cropped'][1]:<5} "
              f"bands={r['bands']} title-dropped={r['droppedTitle']} {len(data):,} bytes")
    b.close()
