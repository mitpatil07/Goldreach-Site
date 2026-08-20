# Scope Declaration

**Source:** https://www.metromediahouse.co/
**Captured:** 2026-08-06
**Purpose:** Mirror the client's live site as a reference baseline, then produce a rebranded
editable copy for **GoldReach Consulting**.

## Authorization

Asked before any capture. User's answer, verbatim:

> **Yes — I'm authorized** — "this agency website of my client now i want to make a same to same
> website with full context, data and visuals For ''GoldReach Consulting''"

The user confirmed they own, control, or have client approval to mirror the site *and* to reuse
the design for GoldReach Consulting.

## Routes

Single-page site. One route in scope:

| Route | Notes |
|---|---|
| `/` | Entire page; all sections are anchors (`#section_process`, `#section_solutions`, `#section_work`, `#section_testimonials`) |

No other routes exist on the source site.

## Viewports

| Width × Height | Status |
|---|---|
| 1440 × 900 (desktop) | in scope |
| 390 × 844 (mobile) | in scope |

## Interactions in scope

- Full-page scroll to bottom (scroll-triggered reveals, marquee animation)
- FAQ accordion expand/collapse
- Mobile nav menu open
- Video embeds present and addressable (playback itself is provider-hosted — see report)
- Hover states — **not** exercised

## Acceptance level targeted

**Level 3 — Offline-validated**, for the declared route at 1440×900.
Level 2 (Validated) for 390×844.

## Deliverables

1. `mirror/` — byte-faithful capture of the source site (reference baseline)
2. `goldreach/` — the same site rebranded to GoldReach Consulting (working copy)

## Additional authorization — theclips.agency (2026-08-06)

Asked before capturing any asset from this second origin. User's answer, verbatim:

> "i need the shorts from clips.agency that same shorts, i've rights of that clips.agency is
> also mine"

The user states theclips.agency is also theirs. On that basis the portrait short-form clips from
that site are captured into `goldreach/assets/clips/` and used in the clip marquee.
