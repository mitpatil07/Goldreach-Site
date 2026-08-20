# GoldReach Consulting — site baseline

Two builds, both working offline-capable static sites:

| Folder | What it is |
|---|---|
| `mirror/` | Untouched capture of `metromediahouse.co`. Reference baseline — don't edit it. |
| `goldreach/` | The same site, rebranded to GoldReach Consulting. **Work here.** |

## Run it

```bash
python3 "$HOME/.claude/skills/open-mirror/scripts/serve.py" --root goldreach --port 8081 --manifest manifest.json
```

Open http://localhost:8081/ . Swap `--root mirror --port 8080` to compare against the original.

`file://` will not work — use the server.

## Before this goes anywhere public

Read the **Gaps** section of [MIRROR_REPORT.md](MIRROR_REPORT.md). In short:

1. Videos still stream from Metro Media House's Gumlet account — replace them.
2. Copy, stats and testimonials are still the original agency's — see gap 4 in the report.
3. Every statistic, testimonial, and client logo is still the original agency's real data.
4. Social + booking links are constructed guesses.

## Editing

Everything lives in one file: `goldreach/index.html` (127 KB, single page).
The original Webflow styles are in `goldreach/_ext/cdn.prod.website-files.com/*/css/*.css` —
**leave those alone**.

### Colour: `goldreach/assets/theme-light.css`

The light theme is a single override sheet loaded after the Webflow bundle. It changes colour
only — no layout, spacing, or typography. Tune the variables at the top and the whole page follows:

| Variable | Now | Controls |
|---|---|---|
| `--gr-bg` | `#ffffff` | page background |
| `--gr-bg-soft` | `#f3f4f6` | top of the section fades |
| `--gr-ink` | `#14161a` | primary text |
| `--gr-ink-muted` | `#5b6169` | body text |
| `--gr-line` | `rgba(0,0,0,.10)` | hairline borders |
| `--gr-gold` | `#ffb950` | brand gold — **backgrounds only** |
| `--gr-gold-ink` | `#9a6206` | brand gold — **text on white** |

Gold needs two values: `#ffb950` on white is only ~1.9:1 contrast, so headings and links use the
darker `--gr-gold-ink` while buttons keep the bright fill with black labels.

To go back to the original dark theme, delete the `theme-light.css` `<link>` from `index.html`.

### Generated theme assets (`goldreach/assets/`)

| File | What it is |
|---|---|
| `grid-lines-light.svg` | hero/CTA bracket grid, strokes inverted to black at the original 0.15 opacity |
| `grid-process-light.svg` | process-section grid, same treatment at 0.3 opacity |
| `grid-paper-light.png` | graph-paper grid behind testimonials, RGB-inverted with alpha preserved |
| `goldreach-logo.png` | the real GoldReach wordmark — cropped from your export, background knocked out to transparent (1345×348) |
| `stat-team.png` · `stat-views.png` · `stat-years.png` · `stat-content.png` | hero stat icons — cropped from your four posters, baked-in titles removed, white background knocked out to transparent |

## Other files

| Path | Contents |
|---|---|
| `SCOPE.md` | What was declared in scope, and the authorization statement |
| `MIRROR_REPORT.md` | Full capture report: gates, accommodations, dependencies, gaps |
| `manifest.json` | Per-file record: URL, path, status, size, SHA-256, discovery method |
| `evidence/` | Screenshots, validation reports, server access logs |
| `work/` | Discovery output and capture scripts (not part of the site) |
