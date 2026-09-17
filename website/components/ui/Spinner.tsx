export function Spinner({ label = "กำลังโหลด..." }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 py-10 text-slate-500">
      <span className="spinner h-5 w-5 rounded-full border-2 border-slate-300 border-t-brand" />
      <span>{label}</span>
    </div>
  );
}
