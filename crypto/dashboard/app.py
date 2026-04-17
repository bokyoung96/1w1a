from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .preview import CryptoDashboardPreviewService


def create_app() -> FastAPI:
    app = FastAPI(title="1W1A Crypto Dashboard")
    service = CryptoDashboardPreviewService()

    @app.get("/api/preview")
    def get_preview() -> dict[str, object]:
        return service.build()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>1W1A Crypto Dashboard</title>
  <style>
    :root { --bg:#12161a; --panel:rgba(247,240,231,.05); --line:rgba(247,240,231,.12); --text:#f7f0e7; --muted:#bdaea1; --accent:#f0a44b; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,system-ui,sans-serif; color:var(--text); background:linear-gradient(180deg,#191e23 0%,#12161a 55%); }
    main { padding:28px; display:grid; gap:18px; max-width:1280px; margin:0 auto; }
    .hero, .panel { border:1px solid var(--line); background:var(--panel); border-radius:22px; padding:18px; }
    .hero h1, .panel h2, .panel h3, p { margin:0; }
    .hero p, .muted { color:var(--muted); }
    .metrics, .grid, .registry, .basket { display:grid; gap:12px; }
    .metrics { grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); }
    .metric, .registry-card, .basket-row { border:1px solid var(--line); border-radius:16px; padding:12px; background:rgba(247,240,231,.03); }
    .grid { grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }
    .basket-row { display:grid; grid-template-columns:minmax(0,2.5fr) repeat(3,minmax(70px,.8fr)); align-items:center; }
    .registry { grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); }
    .pill { display:inline-block; padding:4px 10px; border-radius:999px; border:1px solid var(--line); color:var(--muted); font-size:12px; }
    svg { width:100%; height:220px; display:block; }
    table { width:100%; border-collapse:collapse; }
    th, td { text-align:left; padding:8px 6px; border-bottom:1px solid var(--line); }
    th { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.12em; }
    .right { text-align:right; }
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>Crypto Factory Dashboard</h1>
    <p>Crypto research now lives under <code>crypto/</code>. This page reviews the candidate pool, orthogonality-selected basket, hierarchical allocation, and preview performance without touching the legacy dashboard stack.</p>
  </section>
  <section class="panel">
    <h2>Summary</h2>
    <div id="summary" class="metrics"></div>
  </section>
  <section class="panel grid">
    <article>
      <h3>Equity preview</h3>
      <div id="equity-chart"></div>
    </article>
    <article>
      <h3>Family allocation</h3>
      <table id="family-table"></table>
    </article>
  </section>
  <section class="panel">
    <h2>Selected basket</h2>
    <div id="basket" class="basket"></div>
  </section>
  <section class="panel">
    <h2>Registered strategies</h2>
    <div id="registry" class="registry"></div>
  </section>
</main>
<script>
  function pct(v){ return (v*100).toFixed(1) + '%'; }
  function num(v){ return Number(v).toFixed(3); }
  function money(v){ return '$' + Number(v).toLocaleString(undefined,{maximumFractionDigits:0}); }
  function path(points, width, height){
    if(!points.length) return '';
    const values = points.map(p => p.value);
    const min = Math.min(...values), max = Math.max(...values);
    const span = Math.max(max - min, 1e-9);
    return points.map((p,i) => {
      const x = (i / Math.max(points.length-1,1)) * width;
      const y = height - (((p.value - min)/span) * height);
      return `${i===0?'M':'L'} ${x.toFixed(2)} ${y.toFixed(2)}`;
    }).join(' ');
  }
  fetch('/api/preview').then(r => r.json()).then(payload => {
    const summary = payload.summary;
    document.getElementById('summary').innerHTML = [
      ['Candidate pool', summary.candidate_pool_size],
      ['Selected basket', summary.selected_basket_size],
      ['Registered strategies', summary.registered_strategy_count],
      ['Family cap', summary.family_cap + ' / family'],
      ['Trigger', summary.trigger_reason],
      ['Paper Sharpe', payload.performance_summary.paper_sharpe.toFixed(2)],
    ].map(([k,v]) => `<div class="metric"><div class="muted">${k}</div><strong>${v}</strong></div>`).join('');

    const equity = payload.performance.equity_curve;
    const drawdown = payload.performance.drawdown_curve;
    document.getElementById('equity-chart').innerHTML = `<svg viewBox="0 0 600 220" preserveAspectRatio="none">
      <path d="${path(equity, 600, 160)}" fill="none" stroke="#f0a44b" stroke-width="3"></path>
      <path d="${path(drawdown, 600, 160)}" fill="none" stroke="#7cb8d8" stroke-width="2"></path>
    </svg><div class="muted">Equity starts near ${money(equity[0].value)} and ends near ${money(equity[equity.length-1].value)}.</div>`;

    document.getElementById('family-table').innerHTML =
      '<thead><tr><th>Family</th><th class="right">Weight</th><th class="right">Strategies</th></tr></thead><tbody>' +
      payload.family_allocations.map(row => `<tr><td>${row.family}</td><td class="right">${pct(row.weight)}</td><td class="right">${row.strategy_count}</td></tr>`).join('') +
      '</tbody>';

    document.getElementById('basket').innerHTML = payload.selected_basket.map(row => `
      <div class="basket-row">
        <div><strong>${row.strategy_name}</strong><div class="muted">${row.family}</div></div>
        <div>${num(row.total_score)}</div>
        <div>${pct(row.target_weight)}</div>
        <div>${pct(row.max_pairwise_correlation)}</div>
      </div>`).join('');

    document.getElementById('registry').innerHTML = payload.registry.map(row => `
      <div class="registry-card">
        <div style="display:flex;justify-content:space-between;gap:8px;align-items:flex-start">
          <strong>${row.name}</strong>
          <span class="pill">${row.selected ? 'selected' : 'registered'}</span>
        </div>
        <div class="muted" style="margin-top:8px">${row.family}</div>
        <div class="muted" style="margin-top:8px">${row.rationale_excerpt}</div>
        <div class="muted" style="margin-top:10px">${row.candidate_count} candidates · top score ${num(row.top_score)}</div>
      </div>`).join('');
  });
</script>
</body>
</html>"""

    return app


app = create_app()
