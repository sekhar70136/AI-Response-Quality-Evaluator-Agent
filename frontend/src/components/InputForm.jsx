import { useState } from 'react';

function InputForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    question: '',
    response: '',
    reference_answer: '',
    model: '',
  });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!formData.question.trim() || !formData.response.trim()) {
      alert('Please enter both question and response.');
      return;
    }

    onSubmit({
      question: formData.question,
      response: formData.response,
      reference_answer: formData.reference_answer || null,
      model: formData.model || null,
    });
  };

  const clearForm = () => {
    setFormData({ question: '', response: '', reference_answer: '', model: '' });
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-xl bg-white p-6 shadow-md">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-2">
          <span className="font-medium">Question</span>
          <textarea
            name="question"
            value={formData.question}
            onChange={handleChange}
            rows="4"
            className="rounded-lg border border-slate-300 p-3"
            placeholder="Enter the user's question"
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="font-medium">AI Response</span>
          <textarea
            name="response"
            value={formData.response}
            onChange={handleChange}
            rows="4"
            className="rounded-lg border border-slate-300 p-3"
            placeholder="Enter the AI-generated response"
          />
        </label>
      </div>

      <label className="mt-4 flex flex-col gap-2">
        <span className="font-medium">Optional Reference Answer</span>
        <textarea
          name="reference_answer"
          value={formData.reference_answer}
          onChange={handleChange}
          rows="3"
          className="rounded-lg border border-slate-300 p-3"
          placeholder="Optional reference answer"
        />
      </label>

      <label className="mt-4 flex flex-col gap-2">
        <span className="font-medium">AI System / Model Name (optional)</span>
        <input
          name="model"
          value={formData.model}
          onChange={handleChange}
          className="rounded-lg border border-slate-300 p-3"
          placeholder="e.g. llama-3.1-8b-instant, gpt-4, claude-3"
        />
      </label>

      <div className="mt-6 flex gap-3">
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? 'Evaluating...' : 'Evaluate'}
        </button>
        <button
          type="button"
          onClick={clearForm}
          className="rounded-lg bg-slate-200 px-4 py-2 font-medium text-slate-700"
        >
          Clear
        </button>
      </div>
    </form>
  );
}

export default InputForm;
