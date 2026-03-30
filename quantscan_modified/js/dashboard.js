/* ============================================================
   QuantScan Dashboard JS  —  Real Fundamental + Sentiment View
   ============================================================ */

let trendChart, gaugeChart;

const API = "http://127.0.0.1:8000";

/* ── Helpers ───────────────────────────────────────────────── */
const fmt  = (v, d=2) => (v == null || isNaN(v)) ? "—" : Number(v).toFixed(d);
const pct  = (v)      => (v == null || isNaN(v)) ? "—" : `${Number(v).toFixed(2)}%`;
const cr   = (v)      => (v == null || isNaN(v)) ? "—" : `₹${Number(v).toLocaleString("en-IN", {maximumFractionDigits:2})}`;

function signalClass(signal) {
    if (!signal) return "";
    const s = signal.toUpperCase();
    if (s.includes("STRONG BUY"))  return "strong-buy";
    if (s.includes("BUY"))         return "buy";
    if (s.includes("STRONG SELL")) return "strong-sell";
    if (s.includes("SELL"))        return "sell";
    return "hold";
}

function sentimentClass(label) {
    if (!label) return "";
    if (label === "POSITIVE") return "positive";
    if (label === "NEGATIVE") return "negative";
    return "neutral";
}

/* ── ANALYZE single stock ──────────────────────────────────── */
async function analyze() {
    try {
        let raw = document.getElementById("symbol").value.trim().toUpperCase();
        if (!raw) { alert("Enter a stock symbol (e.g. TCS or TCS.NS)"); return; }

        document.getElementById("insight").innerHTML = `<span class="loading">Analyzing ${raw}…</span>`;

        let res  = await fetch(`${API}/analyze/${raw}`);
        let data = await res.json();

        if (data.detail || data.error) {
            document.getElementById("insight").innerHTML = `<span class="error">Stock not found or no data available.</span>`;
            return;
        }

        renderCharts(data);
        renderInsight(data);
        renderFundamentals(data);
        renderSentiment(data);
        highlightStock(data.symbol);

    } catch(e) {
        console.error("Analyze error:", e);
        document.getElementById("insight").innerHTML = `<span class="error">Connection error — is the backend running?</span>`;
    }
}

/* ── Charts ─────────────────────────────────────────────────── */
function renderCharts(d) {
    if (trendChart) trendChart.destroy();
    trendChart = new Chart(document.getElementById("trend"), {
        type: "bar",
        data: {
            labels: ["Current Price", "Graham Number", "DCF Value", "Intrinsic Value"],
            datasets: [{
                label: "₹ Value",
                data: [d.price, d.graham_value, d.dcf_value, d.intrinsic_value],
                backgroundColor: ["#64748b","#3b82f6","#8b5cf6","#22c55e"],
                borderRadius: 6
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { ticks: { callback: v => "₹" + v.toLocaleString("en-IN") } } }
        }
    });

    if (gaugeChart) gaugeChart.destroy();
    let strength = Math.max(5, Math.min(95, d.upside_pct + 50));
    let color = d.upside_pct >= 5 ? "#22c55e" : d.upside_pct <= -5 ? "#ef4444" : "#f59e0b";
    gaugeChart = new Chart(document.getElementById("gauge"), {
        type: "doughnut",
        data: {
            datasets: [{
                data: [strength, 100 - strength],
                backgroundColor: [color, "#1e293b"],
                borderWidth: 0
            }]
        },
        options: { cutout: "80%", plugins: { legend: { display: false } } }
    });
}

/* ── Insight panel ──────────────────────────────────────────── */
function renderInsight(d) {
    const sc = signalClass(d.recommendation || d.signal);
    document.getElementById("insight").innerHTML = `
      <div class="insight-row">
        <span class="insight-symbol">${d.symbol}</span>
        <span class="signal-badge ${sc}">${d.recommendation || d.signal}</span>
      </div>
      <div class="insight-stats">
        <div class="stat-item"><span class="stat-label">Price</span><span class="stat-val">${cr(d.price)}</span></div>
        <div class="stat-item"><span class="stat-label">Intrinsic</span><span class="stat-val">${cr(d.intrinsic_value)}</span></div>
        <div class="stat-item"><span class="stat-label">Upside</span><span class="stat-val ${d.upside_pct >= 0 ? 'green' : 'red'}">${pct(d.upside_pct)}</span></div>
        <div class="stat-item"><span class="stat-label">QuantScore</span><span class="stat-val">${d.composite_score ?? "—"}/100</span></div>
        <div class="stat-item"><span class="stat-label">Grade</span><span class="stat-val grade-${d.grade}">${d.grade ?? "—"}</span></div>
      </div>
      <div class="valuation-row">
        <span>Graham Number: <b>${cr(d.graham_value)}</b></span>
        <span>DCF Value: <b>${cr(d.dcf_value)}</b></span>
      </div>`;
}

/* ── Fundamentals panel ─────────────────────────────────────── */
function renderFundamentals(d) {
    const el = document.getElementById("fundamentals");
    if (!el) return;
    el.innerHTML = `
      <h3>Fundamental Metrics <span class="grade-badge grade-${d.grade}">${d.grade} (${d.fundamental_score}/100)</span></h3>
      <table class="fund-table">
        <tr><td>P/E Ratio</td><td><b>${fmt(d.pe)}</b></td><td>Fwd P/E</td><td><b>${fmt(d.fwd_pe)}</b></td></tr>
        <tr><td>EPS</td><td><b>₹${fmt(d.eps)}</b></td><td>EPS Growth</td><td><b class="${d.eps_growth_pct>=0?'green':'red'}">${pct(d.eps_growth_pct)}</b></td></tr>
        <tr><td>ROE</td><td><b class="${d.roe_pct>=15?'green':'orange'}">${pct(d.roe_pct)}</b></td><td>ROCE</td><td><b class="${d.roce_pct>=15?'green':'orange'}">${pct(d.roce_pct)}</b></td></tr>
        <tr><td>Debt/Equity</td><td><b class="${d.de_ratio<=0.5?'green':d.de_ratio<=2?'orange':'red'}">${fmt(d.de_ratio)}</b></td><td>Div Yield</td><td><b>${pct(d.div_yield_pct)}</b></td></tr>
      </table>`;
}

/* ── Sentiment panel ────────────────────────────────────────── */
function renderSentiment(d) {
    const el = document.getElementById("sentiment");
    if (!el) return;
    const sc = sentimentClass(d.sentiment_label);
    const headlines = (d.headlines || []).map(h => `<li>${h}</li>`).join("");
    el.innerHTML = `
      <h3>News Sentiment
        <span class="sentiment-badge ${sc}">${d.sentiment_label} (${fmt(d.sentiment_score, 3)})</span>
      </h3>
      <div class="sentiment-counts">
        <span class="pos">▲ ${d.positive_news} Positive</span>
        <span class="neg">▼ ${d.negative_news} Negative</span>
        <span class="neu">● ${d.neutral_news ?? 0} Neutral</span>
      </div>
      <ul class="headline-list">${headlines || "<li>No headlines available</li>"}</ul>`;
}

/* ── Scanner table ──────────────────────────────────────────── */
async function loadScanner() {
    try {
        document.getElementById("scannerTable").innerHTML =
            `<tr><td colspan="8" style="text-align:center;padding:20px">🔍 Scanning NIFTY 500… this may take 30-60s</td></tr>`;

        let res  = await fetch(`${API}/scan?limit=50&min_upside=5`);
        let data = await res.json();

        let html = "";
        data.forEach((s, i) => {
            const sc = signalClass(s.recommendation || s.signal);
            const ss = sentimentClass(s.sentiment_label);
            html += `
              <tr id="${s.symbol}" onclick="loadStock('${s.symbol}')">
                <td>${i+1}</td>
                <td><b>${s.symbol.replace(".NS","")}</b></td>
                <td>${cr(s.price)}</td>
                <td>${cr(s.intrinsic_value)}</td>
                <td class="${s.upside_pct>=0?'green':'red'}">${pct(s.upside_pct)}</td>
                <td>${s.fundamental_score ?? "—"}/100 <small>(${s.grade})</small></td>
                <td class="${ss}">${s.sentiment_label ?? "—"}</td>
                <td><span class="signal-badge ${sc}">${s.recommendation || s.signal}</span></td>
              </tr>`;
        });

        document.getElementById("scannerTable").innerHTML = html || `<tr><td colspan="8">No undervalued stocks found</td></tr>`;

        // Ticker tape
        let tickerText = data.slice(0,15).map(s =>
            `${s.symbol.replace(".NS","")} ₹${Number(s.price).toFixed(0)} (${pct(s.upside_pct)}↑)`
        ).join("   •   ");
        const te = document.getElementById("tickerText");
        if (te) te.innerText = tickerText;

    } catch(e) {
        console.error("Scanner error:", e);
        document.getElementById("scannerTable").innerHTML =
            `<tr><td colspan="8" style="color:#ef4444">Backend not reachable — run: uvicorn app:app --reload</td></tr>`;
    }
}

function loadStock(symbol) {
    document.getElementById("symbol").value = symbol.replace(".NS","");
    analyze();
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function highlightStock(symbol) {
    document.querySelectorAll("tr.selected").forEach(r => r.classList.remove("selected"));
    let row = document.getElementById(symbol);
    if (row) row.classList.add("selected");
}

/* ── Init ───────────────────────────────────────────────────── */
loadScanner();
