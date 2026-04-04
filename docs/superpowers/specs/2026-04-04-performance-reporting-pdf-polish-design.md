# Performance Reporting PDF Polish Design

**Date:** 2026-04-04
**Status:** Approved for planning
**Scope:** Visual and layout refinement of `backtesting.reporting` HTML/PDF outputs, with PDF readability as the primary constraint

## Goal

Refine the current performance reporting output so that:

- PDF readability becomes the first-class target
- the web page remains clean and credible, but follows the PDF structure instead of dictating it
- typography, spacing, and table hierarchy feel closer to institutional ETF / fund factsheets than to oversized dashboard cards
- the report can survive long tables and multiple sections without collapsing into cramped figures or oversized decorative chrome

This is not a new analytics feature set. It is a document design correction on top of the current redesigned reporting stack.

## Why A Second Design Pass Is Needed

The current redesign fixed analytics depth, but the rendered document still has presentational issues:

- headline and card typography is too large for a print-first document
- section padding and border treatment consume too much page area
- tables are visually subordinate even though they carry key investment information
- PDF and web are still too tightly coupled to one “large responsive page” look
- comparison and tear sheet covers spend too much visual weight on hero treatment before getting to the analysis

The result is a report that feels styled, but not yet disciplined enough for institutional reading.

## Reference Direction

This pass is guided by two reference families collected with Tavily:

- Strategy references emphasized pixel-perfect reporting, explicit section control, reusable template discipline, and deliberate title/layout treatment rather than generic responsive scaling.
- ETF / fund factsheet references, especially iShares sector and industry material, emphasized compact KPI presentation, restrained typography, dense but legible tables, and a strong first analytical spread after the cover.

Reference links:

- https://www.strategy.com/software/blog/why-pixel-perfect-reporting-matters-for-businesses
- https://www.strategy.com/software/blog/responsive-design-with-strategy-how-to-leverage-dashboard-features-to-boost-user-experience-and-increase-user-adoption-by-66degrees
- https://www.ishares.com/us/literature/presentation/ishares-sector-and-industry-etfs.pdf

## Validated Design Decisions

### 1. Primary Output Standard

PDF readability is the top priority.

Implication:

- layout choices should be validated against A4 pagination first
- web output should inherit the same hierarchy, but may keep limited responsive adaptation
- decorative elements should never force smaller data tables or unreadable chart labels in PDF

### 2. Visual Direction

Chosen direction: `Hybrid Compact Research`

Meaning:

- preserve a polished document feel
- reduce headline scale and empty space
- increase information density after the opening page
- keep Strategy-like order and discipline, but borrow ETF factsheet compactness for KPI and table presentation

### 3. Cover Strategy

Page 1 should remain relatively spacious.

It should behave as a cover page, not as a compressed data wall.

Include only:

- report type
- title
- strategy or participant names
- benchmark
- time range / report identity
- one short descriptor line

Do not place the dense metric grid or large summary tables on page 1.

### 4. Executive Density Starts On Page 2

Page 2 becomes the first high-density analytical spread.

This page should carry the strongest decision-making payload in the document:

- compact KPI strip
- primary performance chart
- benchmark-relative highlights
- one or two dense institutional tables
- a concise secondary risk or drawdown panel

This page should answer most PM / allocator review questions without requiring the appendix.

### 5. Table Philosophy

Tables should follow institutional report density, not presentation-deck spacing.

Implication:

- smaller but controlled font sizes
- tighter row height
- stronger numeric alignment
- fixed and intentional column widths where possible
- repeated header treatment that supports PDF scanning
- reduced corner radius, shadow, and card framing around tables

The table is a primary information surface, not an appendix afterthought.

## Document Architecture

### Tearsheet Structure

Recommended order:

1. Cover page
2. Executive summary spread
3. Rolling diagnostics
4. Return shape / calendar / distribution
5. Holdings and sector exposure
6. Appendix and notes

### Comparison Report Structure

Recommended order:

1. Cover page
2. Ranked comparison summary spread
3. Performance comparison spread
4. Rolling and benchmark-relative diagnostics
5. Holdings / sector comparison
6. Appendix and notes

## Page-Level Layout Rules

### Cover Page

Purpose:

- establish credibility
- frame the reporting period
- avoid overloading the reader before analysis begins

Rules:

- use restrained title scale
- avoid large hero cards
- avoid multi-card KPI grids
- keep one visual accent band or label system at most

### Executive Summary Spread

Purpose:

- compress the highest-value performance information into one spread

Rules:

- KPI band should be horizontal and compact, not a tall 4x2 card wall
- the main chart should dominate the page width
- secondary tables should sit adjacent to or below the main chart with explicit hierarchy
- supporting labels should be small, uppercase or muted, and never compete with data values

### Analytical Interior Pages

Rules:

- each page should have one primary visual job
- avoid repeating the same card chrome for every section
- remove redundant section labels if the page title already carries the meaning
- favor two-column analytical compositions over isolated stacked blocks when it improves density

## Typography System

The current scale is too large.

The revised system should:

- reduce title size on cover and section heads
- reduce KPI value size enough to keep multiple metrics on one line or one band
- make table text slightly smaller than body text, but with improved contrast and alignment
- use stronger distinction through weight and spacing, not just bigger type

Target feel:

- disciplined
- print-first
- compact
- institutional

Avoid:

- oversized hero numerals
- billboard headings
- long muted paragraphs that occupy scarce page space

## Spacing And Surface Rules

The current design overuses padding, rounded corners, and shadow.

The revised system should:

- reduce section padding
- tighten inter-section spacing
- reduce border radius across panels and tables
- soften or remove heavy drop shadows for print
- use background tone sparingly so data surfaces remain crisp

Preferred visual language:

- warm neutral paper background is acceptable
- white or near-white data panels
- dark ink text
- restrained accent color

## Figure And Table Balance

Current problem:

- figures appear large and comfortable
- tables appear relatively small and secondary

Correction:

- chart blocks should lose some chrome and margin
- tables should gain structural prominence through width, alignment, and placement
- in comparison reports, ranked and benchmark-relative tables should appear earlier and larger

## Web vs PDF Behavior

PDF remains the source of truth.

Web can diverge only where needed for browser usability:

- horizontal overflow for very wide tables is acceptable on web
- PDF should instead use tighter formatting, page breaks, and controlled widths
- web may keep a wider shell, but typography and spacing should still mirror the compact system

Do not maintain two unrelated visual systems.

## Template And CSS Impact

Primary files expected to change:

- `backtesting/reporting/styles.css`
- `backtesting/reporting/templates/tearsheet.html.j2`
- `backtesting/reporting/templates/comparison.html.j2`
- `backtesting/reporting/composers.py`

Possible supporting changes:

- `backtesting/reporting/html.py`
- `backtesting/reporting/pdf.py`

Likely responsibilities:

- CSS introduces a compact print scale, denser table rules, stronger page-break behavior, and lighter section chrome
- templates restructure cover vs executive pages instead of using one repeated “hero + sections” pattern
- composers may need richer context for cover metadata, page grouping, KPI band formatting, and table priority ordering

## Out Of Scope

This pass should not:

- replace the analytics engine
- add new benchmark math unless required by layout grouping
- redesign chart generation logic from scratch
- split the product into completely separate web-only and PDF-only report systems

## Verification Expectations

Implementation is only complete when:

- a generated PDF shows improved hierarchy and denser but readable tables
- the first analytical spread clearly outperforms the current output in information density
- tear sheet and comparison outputs both follow the same visual system
- web output still renders cleanly without breaking relative asset paths

## Implementation Recommendation

Use the existing reporting architecture and execute a PDF-first layout refactor instead of a superficial CSS reskin.

The recommended implementation strategy is:

- restructure templates around `cover` and `executive spread` concepts
- replace the current metric-card wall with a compact KPI strip
- promote top-priority tables earlier in the document
- rework the spacing and type scale in CSS for print-first density
- keep HTML and PDF aligned to one disciplined visual system led by PDF constraints
