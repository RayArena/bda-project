/* =========================================================
   SentimentScope dashboard charts (Chart.js 4)
   ========================================================= */
(function () {
    if (typeof Chart === "undefined") return;

    const COLORS = {
        Negative:   "#ef4444",
        Positive:   "#22c55e",
        Neutral:    "#3b82f6",
        Irrelevant: "#f59e0b",
    };
    const GRID = "rgba(100, 116, 139, 0.15)";
    const TICK = "#475569";

    // Chart.js global defaults -> match the dark theme
    Chart.defaults.color = TICK;
    Chart.defaults.font.family = "'Poppins', sans-serif";

    function readJSON(id, fallback) {
        const el = document.getElementById(id);
        if (!el) return fallback;
        try { return JSON.parse(el.textContent); } catch (e) { return fallback; }
    }

    const counts  = readJSON("counts-data", {});
    const confAvg = readJSON("conf-data", {});
    const hist    = readJSON("hist-data", {});

    const labels      = Object.keys(counts);
    const countVals   = Object.values(counts);
    const classColors = labels.map(l => COLORS[l] || "#8b5cf6");

    const noAxisLegend = {
        plugins: { legend: { display: false } },
        maintainAspectRatio: false,
    };

    // 1) Sentiment distribution (doughnut)
    const pie = document.getElementById("pieChart");
    if (pie) {
        new Chart(pie, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{ data: countVals, backgroundColor: classColors, borderColor: "#ffffff", borderWidth: 3 }],
            },
            options: {
                maintainAspectRatio: false,
                cutout: "62%",
                plugins: { legend: { position: "right", labels: { usePointStyle: true, padding: 16 } } },
            },
        });
    }

    // 2) Tweets per class (vertical bar)
    const bar = document.getElementById("barChart");
    if (bar) {
        new Chart(bar, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{ data: countVals, backgroundColor: classColors, borderRadius: 8, maxBarThickness: 70 }],
            },
            options: {
                ...noAxisLegend,
                scales: {
                    y: { beginAtZero: true, grid: { color: GRID }, ticks: { precision: 0 } },
                    x: { grid: { display: false } },
                },
            },
        });
    }

    // 3) Average accuracy per class (horizontal bar, 0-100%)
    const conf = document.getElementById("confChart");
    if (conf) {
        new Chart(conf, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    data: labels.map(l => confAvg[l] || 0),
                    backgroundColor: classColors,
                    borderRadius: 8,
                    maxBarThickness: 44,
                }],
            },
            options: {
                ...noAxisLegend,
                indexAxis: "y",
                scales: {
                    x: { beginAtZero: true, max: 100, grid: { color: GRID }, ticks: { callback: v => v + "%" } },
                    y: { grid: { display: false } },
                },
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: ctx => " " + ctx.parsed.x + "% avg accuracy" } },
                },
            },
        });
    }

    // 4) Confidence distribution (histogram-style bar)
    const histEl = document.getElementById("histChart");
    if (histEl) {
        const hlabels = Object.keys(hist);
        new Chart(histEl, {
            type: "bar",
            data: {
                labels: hlabels,
                datasets: [{
                    data: Object.values(hist),
                    backgroundColor: "#8b5cf6",
                    borderRadius: 8,
                    maxBarThickness: 70,
                }],
            },
            options: {
                ...noAxisLegend,
                scales: {
                    y: { beginAtZero: true, grid: { color: GRID }, ticks: { precision: 0 } },
                    x: { grid: { display: false } },
                },
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: ctx => " " + ctx.parsed.y + " tweets" } },
                },
            },
        });
    }
})();
