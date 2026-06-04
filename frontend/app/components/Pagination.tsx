"use client";

type Props = {
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
};

/**
 * ✅ Pagination avec:
 * - Disabled states
 * - Hover effects
 * - Responsive design
 */
export default function Pagination({
  page,
  pages,
  onPageChange,
}: Props) {
  if (pages <= 1) {
    return null;
  }

  return (
    <div className="flex justify-center gap-4 py-6 flex-wrap">
      {/* ✅ Previous button */}
      <button
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
        className="px-5 h-11 rounded-2xl bg-white/5 border border-white/10 hover:border-white/30 disabled:opacity-30 disabled:cursor-not-allowed transition font-semibold"
      >
        ◀ Précédent
      </button>

      {/* ✅ Page info */}
      <div className="px-5 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center font-semibold">
        Page {page} / {pages}
      </div>

      {/* ✅ Next button */}
      <button
        disabled={page >= pages}
        onClick={() => onPageChange(page + 1)}
        className="px-5 h-11 rounded-2xl bg-cyan-400 text-slate-900 font-black hover:bg-cyan-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        Suivant ▶
      </button>
    </div>
  );
}