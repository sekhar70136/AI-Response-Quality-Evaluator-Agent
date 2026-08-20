import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

function BatchCharts({ results }) {
  const verdictRef = useRef(null);
  const scoresRef = useRef(null);
  const hallucinationRef = useRef(null);
  const trendRef = useRef(null);

  useEffect(() => {
    if (!results || !verdictRef.current || !scoresRef.current || !hallucinationRef.current || !trendRef.current) return;

    const verdictCtx = verdictRef.current.getContext('2d');
    const scoresCtx = scoresRef.current.getContext('2d');
    const hallucinationCtx = hallucinationRef.current.getContext('2d');
    const trendCtx = trendRef.current.getContext('2d');

    if (verdictCtx.chart) verdictCtx.chart.destroy();
    if (scoresCtx.chart) scoresCtx.chart.destroy();
    if (hallucinationCtx.chart) hallucinationCtx.chart.destroy();
    if (trendCtx.chart) trendCtx.chart.destroy();

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

    const withHallucination = dimensionResults.filter((r) => (r.hallucination?.score ?? 0) > 0).length;
    const withoutHallucination = dimensionResults.length - withHallucination;

    hallucinationCtx.chart = new Chart(hallucinationCtx, {
      type: 'pie',
      data: {
        labels: ['With Hallucination', 'Without Hallucination'],
        datasets: [
          {
            data: [withHallucination, withoutHallucination],
            backgroundColor: ['#dc2626', '#16a34a'],
            borderWidth: 2,
            borderColor: '#ffffff',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { usePointStyle: true, padding: 16, color: '#334155' },
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const value = ctx.raw;
                const percentage = total ? Math.round((value / total) * 100) : 0;
                return `${ctx.label}: ${value} (${percentage}%)`;
              },
            },
          },
        },
      },
    });

    const trendLabels = dimensionResults.map((_, index) => `Response ${index + 1}`);
    const trendData = dimensionResults.map((r) => r.overall_score ?? 0);

    trendCtx.chart = new Chart(trendCtx, {
      type: 'line',
      data: {
        labels: trendLabels,
        datasets: [
          {
            label: 'Overall Quality Score',
            data: trendData,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.3,
            pointBackgroundColor: '#3b82f6',
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2,
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
              label: (ctx) => `Score: ${ctx.raw}/10`,
            },
          },
        },
      },
    });

    return () => {
      if (verdictCtx.chart) verdictCtx.chart.destroy();
      if (scoresCtx.chart) scoresCtx.chart.destroy();
      if (hallucinationCtx.chart) hallucinationCtx.chart.destroy();
      if (trendCtx.chart) trendCtx.chart.destroy();
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
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Hallucination Frequency</h3>
        <div className="h-64">
          <canvas ref={hallucinationRef} />
        </div>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Quality Trend</h3>
        <div className="h-64">
          <canvas ref={trendRef} />
        </div>
      </div>
    </div>
  );
}

export default BatchCharts;
