import { useState, useCallback } from 'react';
import { evaluateBatch } from '../services/api';
import BatchCharts from './BatchCharts';
import jsPDF from 'jspdf';

function BatchEvaluation() {
  const [rows, setRows] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [error, setError] = useState('');
  const [fileName, setFileName] = useState('');

  const parseCsv = (text) => {
    const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
    if (lines.length === 0) return [];
    const headers = lines[0].split(',').map((h) => h.trim().toLowerCase());
    const questionIdx = headers.findIndex((h) => h === 'question');
    const responseIdx = headers.findIndex((h) => h === 'ai_response');
    const referenceIdx = headers.findIndex((h) => h === 'reference_answer');

    if (questionIdx === -1 || responseIdx === -1) {
      throw new Error('CSV must contain "Question" and "AI_Response" columns.');
    }

    const parsed = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(',');
      const question = (cols[questionIdx] || '').trim();
      const aiResponse = (cols[responseIdx] || '').trim();
      const referenceAnswer = referenceIdx >= 0 ? (cols[referenceIdx] || '').trim() : '';
      if (!question || !aiResponse) continue;
      parsed.push({ question, aiResponse, referenceAnswer });
    }
    return parsed;
  };

  const handleFileChange = useCallback((event) => {
    const file = event.target.files[0];
    if (!file) return;
    setFileName(file.name);
    setError('');
    setResults(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = parseCsv(e.target.result);
        setRows(parsed);
      } catch (err) {
        setError(err.message);
        setRows([]);
      }
    };
    reader.readAsText(file);
  }, []);

  const handleRunBatch = async () => {
    if (!rows.length) return;
    setLoading(true);
    setError('');
    setProgress({ current: 0, total: rows.length });
    try {
      const payload = {
        items: rows.map((row) => ({
          question: row.question,
          response: row.aiResponse,
          reference_answer: row.referenceAnswer || null,
        })),
      };
      const data = await evaluateBatch(payload);
      setResults(data);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Batch evaluation failed.');
    } finally {
      setLoading(false);
      setProgress({ current: 0, total: 0 });
    }
  };

  const exportPdf = () => {
    if (!results) return;
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 15;
    const usableWidth = pageWidth - margin * 2;
    let y = margin;

    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('Batch Evaluation Report', margin, y);
    y += 8;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Generated: ${new Date().toLocaleString()}`, margin, y);
    y += 8;

    if (summary) {
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Summary', margin, y);
      y += 6;
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      const summaryLines = [
        `Total Responses: ${summary.total}`,
        `Average Overall Score: ${summary.average_overall}/10`,
        `Pass / Needs Improvement / Fail: ${summary.pass} / ${summary.needs_improvement} / ${summary.fail}`,
        `Pass Rate: ${summary.total ? Math.round((summary.pass / summary.total) * 100) : 0}%`,
      ];
      summaryLines.forEach((line) => {
        doc.text(line, margin, y);
        y += 5;
      });
      y += 4;
    }

    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Results', margin, y);
    y += 6;

    results.results.forEach((row, index) => {
      if (y > 270) {
        doc.addPage();
        y = margin;
      }

      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      const questionText = doc.splitTextToSize(`Q${index + 1}: ${row.question || ''}`, usableWidth);
      doc.text(questionText, margin, y);
      y += questionText.length * 4.5;

      doc.setFont('helvetica', 'normal');
      const scoreLine = `Overall: ${row.overall_score}/10 | Verdict: ${row.verdict} | Relevance: ${row.relevance?.score ?? '-'}/10 | Accuracy: ${row.accuracy?.score ?? '-'}/10 | Hallucination: ${row.hallucination?.score ?? '-'}/10 | Completeness: ${row.completeness?.score ?? '-'}/10`;
      const scoreLines = doc.splitTextToSize(scoreLine, usableWidth);
      doc.text(scoreLines, margin, y);
      y += scoreLines.length * 4.5;

      if (row.summary) {
        const summaryLines = doc.splitTextToSize(`Summary: ${row.summary}`, usableWidth);
        doc.text(summaryLines, margin, y);
        y += summaryLines.length * 4.2;
      }

      const details = [];
      if (row.relevance?.reasoning) details.push(`Relevance: ${row.relevance.reasoning}`);
      if (row.accuracy?.reasoning) details.push(`Accuracy: ${row.accuracy.reasoning}`);
      if (row.hallucination?.reasoning) details.push(`Hallucination: ${row.hallucination.reasoning}`);
      if (row.completeness?.reasoning) details.push(`Completeness: ${row.completeness.reasoning}`);
      if (row.hallucination?.unsupported_claims?.length) details.push(`Unsupported Claims: ${row.hallucination.unsupported_claims.join('; ')}`);
      if (row.completeness?.missing_points?.length && row.completeness.missing_points[0] !== 'None detected') details.push(`Missing Points: ${row.completeness.missing_points.join('; ')}`);

      details.forEach((detail) => {
        if (y > 270) {
          doc.addPage();
          y = margin;
        }
        const detailLines = doc.splitTextToSize(detail, usableWidth);
        doc.text(detailLines, margin, y);
        y += detailLines.length * 4.2;
      });

      y += 3;
    });

    doc.save('batch_evaluation_report.pdf');
  };

  const summary = results
    ? {
        total: results.total,
        average_overall: results.average_overall_score.toFixed(2),
        pass: results.passed,
        needs_improvement: results.needs_improvement,
        fail: results.failed,
      }
    : null;

  const verdictColor = (verdict) => {
    if (verdict === 'Pass') return 'text-green-700 bg-green-50';
    if (verdict === 'Needs Improvement') return 'text-yellow-700 bg-yellow-50';
    return 'text-red-700 bg-red-50';
  };

  const scoreColor = (score) => {
    if (score == null) return 'text-slate-500';
    if (score >= 8) return 'text-green-700';
    if (score >= 5) return 'text-yellow-700';
    return 'text-red-700';
  };

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <section className="rounded-xl bg-white p-6 shadow-md">
      <h2 className="text-2xl font-semibold">Batch Evaluation</h2>
      <p className="mt-2 text-sm text-slate-600">
        Upload a CSV file with columns: <span className="font-medium">Question</span>,{' '}
        <span className="font-medium">AI_Response</span>, and optional{' '}
        <span className="font-medium">Reference_Answer</span>.
      </p>

      <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-center">
        <label className="inline-flex cursor-pointer items-center rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700">
          Choose CSV
          <input type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
        </label>
        {fileName && <span className="text-sm text-slate-600">{fileName}</span>}
        {rows.length > 0 && !results && (
          <span className="text-sm text-slate-600">{rows.length} rows loaded</span>
        )}
        <button
          type="button"
          onClick={handleRunBatch}
          disabled={!rows.length || loading}
          className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? 'Evaluating...' : 'Run Batch Evaluation'}
        </button>
        {results && (
          <button
            type="button"
            onClick={exportPdf}
            className="rounded-lg bg-slate-700 px-4 py-2 font-medium text-white hover:bg-slate-800"
          >
            Export PDF
          </button>
        )}
      </div>

      {loading && (
        <div className="mt-6">
          <div className="flex items-center justify-between text-sm text-slate-600">
            <span>Evaluating responses...</span>
            <span>{progress.current}/{progress.total}</span>
          </div>
          <div className="mt-2 h-2 rounded-full bg-slate-200">
            <div
              className="h-2 rounded-full bg-blue-500 transition-all"
              style={{ width: progress.total ? `${(progress.current / progress.total) * 100}%` : '0%' }}
            />
          </div>
        </div>
      )}

      {error && <div className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-600">{error}</div>}

      {summary && (
        <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 className="text-sm font-medium text-slate-600">Total Responses</h3>
            <p className="text-2xl font-bold text-slate-900">{summary.total}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 className="text-sm font-medium text-slate-600">Average Overall Score</h3>
            <p className="text-2xl font-bold text-slate-900">{summary.average_overall}/10</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 className="text-sm font-medium text-slate-600">Pass / Needs Improvement / Fail</h3>
            <p className="text-lg font-bold text-slate-900">
              {summary.pass} / {summary.needs_improvement} / {summary.fail}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 className="text-sm font-medium text-slate-600">Pass Rate</h3>
            <p className="text-lg font-bold text-slate-900">
              {summary.total ? Math.round((summary.pass / summary.total) * 100) : 0}%
            </p>
          </div>
        </div>
      )}

      {!results && !loading && (
        <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-600">
          No batch evaluation results available. Upload a CSV to generate visualizations.
        </div>
      )}

      <BatchCharts results={results} />

      {results && results.results.length > 0 && (
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="px-3 py-2 font-medium text-slate-600"></th>
                <th className="px-3 py-2 font-medium text-slate-600">Question</th>
                <th className="px-3 py-2 font-medium text-slate-600">Overall</th>
                <th className="px-3 py-2 font-medium text-slate-600">Verdict</th>
                <th className="px-3 py-2 font-medium text-slate-600">Relevance</th>
                <th className="px-3 py-2 font-medium text-slate-600">Accuracy</th>
                <th className="px-3 py-2 font-medium text-slate-600">Hallucination</th>
                <th className="px-3 py-2 font-medium text-slate-600">Completeness</th>
              </tr>
            </thead>
            <tbody>
              {results.results.map((row, index) => (
                <>
                  <tr key={index} className="border-b border-slate-100 cursor-pointer hover:bg-slate-50" onClick={() => toggleExpand(index)}>
                    <td className="px-3 py-2 text-slate-500">{expandedIndex === index ? '▼' : '▶'}</td>
                    <td className="px-3 py-2 text-slate-800">{row.question}</td>
                    <td className={`px-3 py-2 font-semibold ${scoreColor(row.overall_score)}`}>{row.overall_score != null ? `${row.overall_score}/10` : '-'}</td>
                    <td className="px-3 py-2">
                      <span className={`rounded-md px-2 py-1 text-xs font-medium ${verdictColor(row.verdict)}`}>
                        {row.verdict}
                      </span>
                    </td>
                    <td className={`px-3 py-2 ${scoreColor(row.relevance?.score)}`}>{row.relevance?.score != null ? `${row.relevance.score}/10` : '-'}</td>
                    <td className={`px-3 py-2 ${scoreColor(row.accuracy?.score)}`}>{row.accuracy?.score != null ? `${row.accuracy.score}/10` : '-'}</td>
                    <td className={`px-3 py-2 ${scoreColor(row.hallucination?.score)}`}>{row.hallucination?.score != null ? `${row.hallucination.score}/10` : '-'}</td>
                    <td className={`px-3 py-2 ${scoreColor(row.completeness?.score)}`}>{row.completeness?.score != null ? `${row.completeness.score}/10` : '-'}</td>
                  </tr>
                  {expandedIndex === index && (
                    <tr className="border-b border-slate-200 bg-slate-50">
                      <td colSpan="8" className="px-3 py-4">
                        <div className="grid gap-4 lg:grid-cols-2">
                          <div>
                            <h4 className="mb-2 text-sm font-semibold text-slate-700">Agent Reasoning</h4>
                            <div className="space-y-2 text-xs text-slate-600">
                              <p><span className="font-semibold text-slate-800">Relevance:</span> {row.relevance?.reasoning}</p>
                              <p><span className="font-semibold text-slate-800">Accuracy:</span> {row.accuracy?.reasoning}</p>
                              <p><span className="font-semibold text-slate-800">Hallucination:</span> {row.hallucination?.reasoning}</p>
                              <p><span className="font-semibold text-slate-800">Completeness:</span> {row.completeness?.reasoning}</p>
                            </div>
                          </div>
                          <div>
                            <h4 className="mb-2 text-sm font-semibold text-slate-700">Details</h4>
                            <div className="space-y-2 text-xs text-slate-600">
                              {row.hallucination?.unsupported_claims?.length > 0 && (
                                <div className="rounded-lg border border-red-200 bg-red-50 p-2">
                                  <p className="font-semibold text-red-800">Unsupported Claims:</p>
                                  <ul className="mt-1 list-disc pl-4 text-red-700">
                                    {row.hallucination.unsupported_claims.map((claim, i) => (
                                      <li key={i}>{claim}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {row.completeness?.missing_points?.length > 0 && row.completeness.missing_points[0] !== 'None detected' && (
                                <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-2">
                                  <p className="font-semibold text-yellow-800">Missing Points:</p>
                                  <ul className="mt-1 list-disc pl-4 text-yellow-700">
                                    {row.completeness.missing_points.map((point, i) => (
                                      <li key={i}>{point}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {(!row.hallucination?.unsupported_claims?.length && !row.completeness?.missing_points?.length) && (
                                <p className="text-slate-500">No flagged issues.</p>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default BatchEvaluation;
