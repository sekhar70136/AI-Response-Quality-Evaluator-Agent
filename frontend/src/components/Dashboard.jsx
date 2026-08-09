import ScoreCard from './ScoreCard';
import Loader from './Loader';
import DashboardCharts from './DashboardCharts';

function Dashboard({ result, loading }) {
  if (loading) {
    return <Loader />;
  }

  if (!result) {
    return null;
  }

  const verdictColor =
    result.verdict === 'Pass'
      ? 'text-green-600 bg-green-50 border-green-200'
      : result.verdict === 'Needs Improvement'
        ? 'text-yellow-700 bg-yellow-50 border-yellow-200'
        : 'text-red-700 bg-red-50 border-red-200';

  return (
    <section className="mt-8 rounded-xl bg-white p-6 shadow-md">
      <h2 className="text-2xl font-semibold">Evaluation Result</h2>

      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <ScoreCard
          label="Relevance"
          score={result.relevance.score}
          reasoning={result.relevance.reasoning}
        />
        <ScoreCard
          label="Accuracy"
          score={result.accuracy.score}
          reasoning={result.accuracy.reasoning}
        />
        <ScoreCard
          label="Hallucination"
          score={result.hallucination.score}
          reasoning={result.hallucination.reasoning}
          unsupportedClaims={result.hallucination.unsupported_claims}
        />
        <ScoreCard
          label="Completeness"
          score={result.completeness.score}
          reasoning={result.completeness.reasoning}
          missingPoints={result.completeness.missing_points}
        />
      </div>

      <DashboardCharts result={result} />

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-200 p-4 lg:col-span-2">
          <h3 className="font-semibold">Overall Score</h3>
          <p className="text-3xl font-bold text-slate-900">{result.overall_score}/10</p>
          <p className="mt-1 text-sm text-slate-600">Weighted: Relevance 25% | Accuracy 35% | Hallucination 20% | Completeness 20%</p>
        </div>

        <div className={`rounded-xl border p-4 ${verdictColor}`}>
          <h3 className="font-semibold">Verdict</h3>
          <p className="text-2xl font-bold">{result.verdict}</p>
          <p className="mt-1 text-xs">
            {result.verdict === 'Pass'
              ? 'Meets quality standards'
              : result.verdict === 'Needs Improvement'
                ? 'Usable with notable weaknesses'
                : 'Critical quality issues'}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 p-4">
          <h3 className="font-semibold">Retrieved Context</h3>
          <ul className="mt-2 list-disc pl-5 text-sm text-slate-600">
            {result.retrieved_context.map((item, index) => (
              <li key={index} className="mt-2">{item}</li>
            ))}
          </ul>
        </div>

        <div className="rounded-xl border border-slate-200 p-4">
          <h3 className="font-semibold">Final Summary</h3>
          <p className="mt-2 text-sm text-slate-600">{result.summary}</p>
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
