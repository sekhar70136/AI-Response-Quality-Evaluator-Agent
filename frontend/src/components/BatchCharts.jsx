import { useEffect, useRef } from 'react';

function BatchCharts({ results }) {
  const verdictRef = useRef(null);
  const scoresRef = useRef(null);

  useEffect(() => {
    if (!results || !verdictRef.current || !scoresRef.current) return;

    const verdictCtx = verdictRef.current.getContext('2d');
    const scoresCtx = scoresRef.current.getContext('2d');

    if (verdictCtx.chart) verdictCtx.chart.destroy();
    if (scoresCtx.chart) scoresCtx.chart.destroy();

    const verdictData = [
      results.passed || 0,
      results.needs_improvement || 0,
      results.failed || 0,
    ];

    verdictCtx.chart = new Chart(verdictCtx, {
      type: 'doughnut',
      data: {
        labels: ['Pass', 'Needs Improvement', 'Fail'],
        datasets: [
          {
            data: verdictData,
            backgroundColor: ['#16a34a', '#ca8a04', '#dc2626'],
            borderWidth: 2,
            borderColor: '#ffffff',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { usePointStyle: true, padding: 16, color: '#334155' },
          },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.label}: ${ctx.raw} responses`,
            },
          },
        },
      },
    });

    const dimensionResults = results.results || [];
    const avgScores = [0, 0, 0, 0];
    dimensionResults.forEach((r) => {
      if (r.relevance?.score != null) avgScores[0] += r.relevance.score;
      if (r.accuracy?.score != null) avgScores[1] += r.accuracy.score;
      if (r.hallucination?.score != null) avgScores[2] += r.hallucination.score;
      if (r.completeness?.score != null) avgScores[3] += r.completeness.score;
    });
    const count = dimensionResults.length || 1;
    avgScores.forEach((_, i) => {
      avgScores[i] = Math.round((avgScores[i] / count) * 100) / 100;
    });

    scoresCtx.chart = new Chart(scoresCtx, {
      type: 'bar',
      data: {
        labels: ['Relevance', 'Accuracy', 'Hallucination', 'Completeness'],
        datasets: [
          {
            label: 'Average Score',
            data: avgScores,
            backgroundColor: ['#3b82f6', '#3b82f6', '#3b82f6', '#3b82f6'],
            borderRadius: 6,
            barThickness: 32,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 10,
            grid: { color: '#f1f5f9' },
            ticks: { callback: (v) => `${v}/10`, color: '#64748b' },
          },
          x: {
            grid: { display: false },
            ticks: { color: '#334155', font: { weight: '600' } },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `Avg: ${ctx.raw}/10`,
            },
          },
        },
      },
    });

    return () => {
      if (verdictCtx.chart) verdictCtx.chart.destroy();
      if (scoresCtx.chart) scoresCtx.chart.destroy();
    };
  }, [results]);

  if (!results) return null;

  return (
    <div className="mt-6 grid gap-4 lg:grid-cols-2">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Verdict Distribution</h3>
        <div className="h-64">
          <canvas ref={verdictRef} />
        </div>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Average Dimension Scores</h3>
        <div className="h-64">
          <canvas ref={scoresRef} />
        </div>
      </div>
    </div>
  );
}

export default BatchCharts;
