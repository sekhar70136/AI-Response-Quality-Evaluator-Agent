import { useEffect, useRef } from 'react';

function DashboardCharts({ result }) {
  const radarRef = useRef(null);
  const barRef = useRef(null);

  const labels = ['Relevance', 'Accuracy', 'Hallucination', 'Completeness'];
  const scores = [
    result.relevance.score,
    result.accuracy.score,
    result.hallucination.score,
    result.completeness.score,
  ];
  const maxScore = 10;

  useEffect(() => {
    if (!radarRef.current || !barRef.current) return;

    const radarCtx = radarRef.current.getContext('2d');
    const barCtx = barRef.current.getContext('2d');

    if (radarCtx.chart) radarCtx.chart.destroy();
    if (barCtx.chart) barCtx.chart.destroy();

    const verdictColor =
      result.verdict === 'Pass'
        ? '#16a34a'
        : result.verdict === 'Needs Improvement'
          ? '#ca8a04'
          : '#dc2626';

    radarCtx.chart = new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels,
        datasets: [
          {
            label: 'Score',
            data: scores,
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
            borderColor: '#3b82f6',
            pointBackgroundColor: '#3b82f6',
            borderWidth: 2,
          },
          {
            label: 'Max',
            data: [maxScore, maxScore, maxScore, maxScore],
            backgroundColor: 'rgba(148, 163, 184, 0.1)',
            borderColor: '#cbd5e1',
            borderDash: [5, 5],
            pointRadius: 0,
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true,
            max: maxScore,
            ticks: { stepSize: 2, display: false },
            pointLabels: { font: { size: 12, weight: '600' }, color: '#334155' },
            grid: { color: '#e2e8f0' },
            angleLines: { color: '#e2e8f0' },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${ctx.raw}/10`,
            },
          },
        },
      },
    });

    barCtx.chart = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Score',
            data: scores,
            backgroundColor: scores.map((s) => (s >= 8 ? '#16a34a' : s >= 5 ? '#ca8a04' : '#dc2626')),
            borderRadius: 6,
            barThickness: 28,
          },
        ],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            beginAtZero: true,
            max: maxScore,
            grid: { color: '#f1f5f9' },
            ticks: { callback: (v) => `${v}/10`, color: '#64748b' },
          },
          y: {
            grid: { display: false },
            ticks: { color: '#334155', font: { weight: '600' } },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `Score: ${ctx.raw}/10`,
            },
          },
        },
      },
    });

    return () => {
      if (radarCtx.chart) radarCtx.chart.destroy();
      if (barCtx.chart) barCtx.chart.destroy();
    };
  }, [result, scores, labels]);

  return (
    <div className="mt-6 grid gap-4 lg:grid-cols-2">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Dimension Radar</h3>
        <div className="h-64">
          <canvas ref={radarRef} />
        </div>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Score Breakdown</h3>
        <div className="h-64">
          <canvas ref={barRef} />
        </div>
      </div>
    </div>
  );
}

export default DashboardCharts;
