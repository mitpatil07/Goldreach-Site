# Mirror Report — metromediahouse.co → GoldReach Consulting

| | |
|---|---|
| **Source URL** | https://www.metromediahouse.co/ |
| **Capture date** | 2026-08-06 |
| **Source stack** | Webflow (static HTML + shared CSS bundle + 4 Webflow JS chunks + jQuery) |
| **Deliverables** | `mirror/` (faithful baseline), `goldreach/` (rebranded copy) |

## Authorization

Confirmed with the user before any capture. Verbatim:

> **Yes — I'm authorized** — "this agency website of my client now i want to make a same to same
> website with full context, data and visuals For ''GoldReach Consulting''"

No CAPTCHAs, paywalls, logins, or bot protection were encountered or bypassed. No `noarchive`
directive was present.

## Achieved acceptance level

| Build | Route × Viewport | Level achieved | Evidence |
|---|---|---|---|
| `mirror/` | `/` @ 1440×900 | **Validated** | `evidence/validation_report.json`, `evidence/home_1440x900.png` |
| `mirror/` | `/` @ 390×844 | **Validated** | `evidence/validation_report.json`, `evidence/home_390x844.png` |
| `goldreach/` | `/` @ 1440×900 | **Offline-validated** | `evidence/goldreach/`, `evidence/goldreach-offline/` |
| `goldreach/` | `/` @ 390×844 | **Validated** | `evidence/goldreach/validation_report.json` |

**Not exercised** (therefore not claimed as passing): hover states, video *playback*,
`goldreach/` offline at 390×844, `mirror/` offline at either viewport.

### Gate results

| Gate | Result |
|---|---|
| **Boot** | Both builds return 200 and render fully; no blank page, no hanging preloader |
| **Dependency** | **0 mirror-introduced 404s** at both viewports, both builds, online and offline |
| **Experience** | Live page and mirror both measure **exactly 12712px** full-page height at 1440px wide. Rebranded build measures 12748px (+36px — "GoldReach Consulting" wraps one line longer than "Metro Media House" in the footer) |
| **Offline** | `goldreach/` at 1440×900 with all non-localhost requests aborted: 0 404s, 0 console errors, full-page height 12748px — **identical to the online run** |

Console output is clean of mirror-introduced errors. The only remaining console messages are
`upgrade-insecure-requests ... ignored when delivered in a report-only policy` warnings emitted
by the **external Gumlet video iframes**, which occur on the live site too.

### Interaction evidence (`evidence/goldreach/interactions.json`)

| Interaction | Result |
|---|---|
| FAQ accordion | 3 triggers found; first expands, page height +105px |
| Mobile nav menu (390px) | Button present; menu opens to full-height 844px overlay |
| Full-page scroll | Completes to bottom at both viewports; lazy images resolve |
| Console during interactions | 0 errors |

## Launch instructions

Prerequisite: Python 3 (stdlib only). Serve from the project root:

```bash
python3 "$HOME/.claude/skills/open-mirror/scripts/serve.py" --root goldreach --port 8081 --manifest manifest.json
```

Then open http://localhost:8081/ . For the untouched baseline, use `--root mirror --port 8080`.

Do **not** open via `file://` — the query-variant asset map and correct content types require the server.

## Dependency table

| Class | Count | Detail |
|---|---|---|
| **Local** | 132 files, 4.1 MB | All Webflow CDN assets (images, AVIF/PNG/SVG, responsive `srcset` branches), the shared CSS bundle, 4 Webflow JS chunks, jQuery, 12 Google woff2 font files |
| **External-allowed** | ~171 URLs | Gumlet video (`play.gumlet.io` embeds, `video.gumlet.io` HLS/MP4), `cal.com` booking, social profile links |
| **Dropped (beacons)** | ~280 URLs | `ingest.gumlytics.com` and Sentry analytics beacons — not captured, absence is harmless |
| **External-blocked** | 0 | none encountered |
| **Unresolved** | 0 | — |

Three capture failures are recorded in `manifest.json`; all three are **non-assets**: two were
junk URLs mis-extracted from `<meta>` text content (`/website`, bare `fonts.googleapis.com`), and
one was a truncated filename that was subsequently re-captured successfully.

## Construction-time accommodations

Every edit made to captured bytes, and why:

| # | Edit | Reason |
|---|---|---|
| 1 | Rewrote 187 absolute CDN/font URLs to local `_ext/<host>/...` paths in `index.html` and the CSS bundle | Required for local serving |
| 2 | **Stripped 6 SRI `integrity` attributes** (1 stylesheet, 5 scripts) | Accommodation #1 changes file bytes, so the SHA-384 digests no longer matched and Chrome **blocked the main stylesheet entirely** — the page rendered completely unstyled until this was removed |
| 3 | Replaced the runtime `WebFont.load({google:…})` call with a local `_ext/fonts.local.css` stylesheet, and captured all 12 Google woff2 files | The runtime loader fetches from Google at page load; without this the offline gate fails and fonts fall back |
| 4 | Percent-encoded 186 local references | Webflow filenames contain spaces and parentheses (e.g. `Clip path group (1)-p-1600.png`). Raw spaces **break `srcset` parsing**, which splits on whitespace — 34 srcset entries were affected |
| 5 | Fixed relative depth in `fonts.local.css` (`../fonts.gstatic.com/` → `fonts.gstatic.com/`) | Path was one level too high |

No markup, styles, layout, or content were otherwise altered in `mirror/`.

## Rebrand changes (`goldreach/` only)

Applied with URL attributes masked first, so asset filenames containing `MMH`/`Metro` were never
touched (renaming them would have 404'd the images).

| Change | Count |
|---|---|
| `Metro Media House` → `GoldReach Consulting` | 9 (incl. 1 using a non-breaking space in the footer copyright) |
| `MMH` → `GoldReach` | 3 (nav wordmark, "MMH Spotlight" heading, testimonial body copy) |
| `metromediahouse` → `goldreachconsulting` | 1 |
| Social + booking links repointed | 5 |
| Nav + footer labels renamed | Process→Framework, Solutions→Expertise, Work→Case Studies, Testimonials→Impact (anchor IDs left unchanged so scroll targets still resolve) |
| Footer link list rebuilt | now mirrors the nav (4 new names) plus FAQs; all five wired to real anchors — previously every footer link was a dead `href="#"`. Added `id="section_faq"` to the FAQ section |
| Hero stat row rebuilt | the three original stats (1B+ views / 4 years / 8,000+ videos — Metro Media House's real numbers) replaced with four GoldReach stats and four supplied artworks; grid widened from 3 to 4 columns |
| Sections removed | "GoldReach Spotlight" (`section_layout2`) and "Three ways to work with us" (`section_home-pricing`, the whole pricing/plans block) deleted with all their content. The pricing section carried `id="section_process"` — the Framework nav/footer target — so that anchor was moved to "Content Production, Systematized", and `section_work` (Case Studies) moved to the clips section |
| Client logo strip removed | "Trusted by Industry Leaders" (`section_home-logos`) deleted with all its logos. It carried no nav anchor. The now-dead `img.logo3_logo { filter: invert(1) }` override was removed from theme-light.css |
| Tilted testimonial cards removed | the first `section_home-reviews` block (angled cards from Liah Yoo, Aryan Arora, Zara Jarvis) deleted. No nav anchor on it. A second, differently-styled reviews block (coloured sticky notes) remains |
| Footer credit | "Made with ❤️ by Missing Piece Studio" → "Let's grow your brand"; © 2025 → © 2026 |
| Logo → real wordmark `assets/goldreach-logo.png` (supplied by user) | 4 references (nav, footer, og:image, twitter:image); the separate text label was removed since the wordmark contains the name |

**Verified:** a rendered-DOM text scan of the live GoldReach build returns **0** occurrences of
`metro`, `mmh`, or `metromedia` (case-insensitive), and 9 occurrences of `GoldReach`.

## Gaps — what is NOT reproduced

1. **Videos are not captured.** All video is hosted on Gumlet and served as token-signed HLS/MP4
   from `video.gumlet.io`. The tokens are short-lived and the media belongs to the client's Gumlet
   account. `goldreach/` still points at **Metro Media House's video library** — those embeds show
   the original agency's showreel and client work. **These must be replaced with GoldReach's own
   video assets before this page is shown to anyone.**
2. **Footer developer credit removed.** "Made with ❤️ by Missing Piece Studio" (the agency that
   built the original site) was replaced with "Let's grow your brand", and the copyright year moved
   from 2025 to 2026.
3. **Social and booking links are guesses.** `cal.com/goldreach-consulting/discovery`,
   `x.com/goldreachconsulting`, etc. are constructed placeholders — none are verified to exist.
4. **All copy, statistics, testimonials, and client logos are still Metro Media House's.**
   The hero stats are now GoldReach's own. Still original-agency data: named testimonials
   (Bryan Smith, Zeel Mehta, CJ Finley…), and the client logo strip (Sedona, Maple, Stabledash,
   Emirates…) are the original agency's real claims and real clients. Presenting these as
   GoldReach's own would be false advertising. They are preserved here as layout placeholders only.
5. **Webflow attribution badge** is still present in `goldreach/`, as on the source.
6. **Hover states** were not exercised at any viewport.

## Manifest summary

- **132 files**, **4,100,018 bytes** captured
- Hash algorithm: **SHA-256**, recorded per file in `manifest.json`
- 2 query-variant mappings (jQuery `?site=`, Google Fonts `?family=`)
- Full per-file records: URL, local path, HTTP status, final URL after redirect, content-type,
  byte size, SHA-256, and discovery method

## How the assets were found

Static HTML parsing alone found **146** URLs. A headless-Chromium network-log crawl with full-page
scrolling at both viewports found **583** — the extra 437 were lazy-loaded images, responsive
`srcset` branches, and interaction-triggered requests that naive downloading would have missed.

## Second source — theclips.agency

The user stated (verbatim): *"i need the shorts from clips.agency that same shorts, i've rights of
that clips.agency is also mine"* — recorded in `SCOPE.md`.

On that basis, 14 portrait short-form clips were captured from
`https://theclips.agency/assets/ticker-vids/` into `goldreach/assets/clips/`
(1.3 MB total, SHA-256 per file in `work/clips/capture_records.json`).

They are served **locally** as `<video autoplay muted loop playsinline>` rather than hotlinked, so
the clip marquee passes the offline gate. Native dimensions are 280x498 / 240x427 / 240x426 —
all 9:16 portrait, matching the marquee's card ratio with no cropping.

Discovery note: the clip URLs appear in neither the served HTML nor the single JS bundle — they are
mounted at runtime. All 14 were found only via a scrolling browser crawl with request
logging; a static fetch of the page returns zero of them.
