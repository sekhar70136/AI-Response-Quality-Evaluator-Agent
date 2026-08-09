function ScoreCard({ label, score, reasoning, missingPoints, unsupportedClaims }) {
  const getScoreColor = (s) => {
    if (s >= 8) return 'text-green-600';
    if (s >= 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getBarColor = (s) => {
    if (s >= 8) return 'bg-green-500';
    if (s >= 5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold text-slate-700">{label}</h3>
        <span className={`text-xl font-bold ${getScoreColor(score)}`}>{score}/10</span>
      </div>
      <div className="h-2 rounded-full bg-slate-200">
        <div className={`h-2 rounded-full ${getBarColor(score)}`} style={{ width: `${(score / 10) * 100}%` }} />
      </div>
      <p className="mt-3 text-sm text-slate-600">{reasoning}</p>

      {missingPoints && missingPoints.length > 0 && missingPoints[0] !== 'None detected' && (
        <div className="mt-3 rounded-lg border border-yellow-200 bg-yellow-50 p-3">
          <p className="text-xs font-medium text-yellow-800">Missing Points</p>
          <ul className="mt-1 list-disc pl-4 text-xs text-yellow-700">
            {missingPoints.map((point, i) => (
              <li key={i}>{point}</li>
            ))}
          </ul>
        </div>
      )}

      {unsupportedClaims && unsupportedClaims.length > 0 && (
        <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3">
          <p className="text-xs font-medium text-red-800">Unsupported Claims</p>
          <ul className="mt-1 list-disc pl-4 text-xs text-red-700">
            {unsupportedClaims.map((claim, i) => (
              <li key={i}>{claim}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ScoreCard;
