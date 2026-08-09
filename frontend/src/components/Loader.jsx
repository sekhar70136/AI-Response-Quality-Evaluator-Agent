function Loader() {
  return (
    <div className="mt-6 flex items-center gap-3 text-slate-600">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      <span>Loading evaluation...</span>
    </div>
  );
}

export default Loader;
