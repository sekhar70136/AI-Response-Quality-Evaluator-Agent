import { useState } from 'react';
import Navbar from './components/Navbar';
import InputForm from './components/InputForm';
import Dashboard from './components/Dashboard';
import BatchEvaluation from './components/BatchEvaluation';
import { evaluateResponse } from './services/api';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState('evaluation');

  const handleEvaluate = async (formData) => {
    setLoading(true);
    setError('');
    try {
      const response = await evaluateResponse(formData);
      setResult(response);
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || 'Evaluation failed. Please check the backend server.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const isQuotaError = error && /quota exceeded/i.test(error);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <Navbar onNavigate={setPage} currentPage={page} />
      <main className="mx-auto max-w-6xl px-4 py-8">
        {page === 'evaluation' && (
          <>
            <InputForm onSubmit={handleEvaluate} loading={loading} />
            {error && (
              <div
                className={`mt-4 rounded-lg p-4 text-sm ${
                  isQuotaError
                    ? 'bg-amber-50 text-amber-800 border border-amber-200'
                    : 'bg-red-50 text-red-600'
                }`}
              >
                {isQuotaError
                  ? 'AI API quota exceeded. Check your plan and billing.'
                  : error}
              </div>
            )}
            <Dashboard result={result} loading={loading} />
          </>
        )}
        {page === 'batch' && <BatchEvaluation />}
      </main>
    </div>
  );
}

export default App;
