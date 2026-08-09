function Navbar({ onNavigate, currentPage }) {
  const navItemClasses = (page) =>
    `px-3 py-1 rounded-md text-sm font-medium transition-colors ${
      currentPage === page
        ? 'bg-slate-800 text-white'
        : 'text-slate-300 hover:text-white hover:bg-slate-800'
    }`;

  return (
    <nav className="bg-slate-900 px-4 py-4 text-white shadow-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <h1 className="text-xl font-semibold">AI Response Quality Evaluator</h1>
        <div className="flex gap-2">
          <button type="button" onClick={() => onNavigate('evaluation')} className={navItemClasses('evaluation')}>
            Evaluation
          </button>
          <button type="button" onClick={() => onNavigate('batch')} className={navItemClasses('batch')}>
            Batch Evaluation
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
