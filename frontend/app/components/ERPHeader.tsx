"use client";

import { Search, RefreshCw, ShoppingCart } from "lucide-react";

type Props = {
  search: string;
  setSearch: (value: string) => void;
  loading: boolean;
  cartCount: number;
  onRefresh: () => void;
};

/**
 * ✅ Header avec:
 * - Responsive design
 * - Focus states
 * - Disabled state pour refresh button
 */
export default function ERPHeader({
  search,
  setSearch,
  loading,
  cartCount,
  onRefresh,
}: Props) {
  return (
    <header className="sticky top-0 z-30 bg-[#0b1628]/90 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-[1800px] mx-auto px-6 py-5 flex flex-col xl:flex-row gap-4 justify-between items-start xl:items-center">
        
        {/* ✅ Title section */}
        <div>
          <h1 className="text-3xl xl:text-4xl font-black">
            Maison de la Presse ERP
          </h1>
          <p className="text-slate-400 text-sm">
            Catalogue • POS • Temps réel
          </p>
        </div>

        {/* ✅ Controls section */}
        <div className="flex flex-wrap gap-4 w-full xl:w-auto">
          
          {/* Search */}
          <div className="relative flex-1 xl:flex-none">
            <Search
              size={18}
              className="absolute left-4 top-3.5 text-slate-500"
            />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Recherche..."
              className="w-full xl:w-96 h-12 rounded-2xl bg-white/5 border border-white/10 pl-11 pr-4 outline-none focus:border-cyan-400 transition"
            />
          </div>

          {/* Cart badge */}
          <div className="h-12 px-5 rounded-2xl bg-emerald-500 flex items-center gap-3 font-black whitespace-nowrap text-white">
            <ShoppingCart size={18} />
            <span>{cartCount}</span>
          </div>

          {/* Refresh button */}
          <button
            onClick={onRefresh}
            disabled={loading}
            className="h-12 px-5 rounded-2xl bg-cyan-400 text-slate-900 font-black flex items-center gap-2 hover:bg-cyan-300 disabled:opacity-50 disabled:cursor-not-allowed transition whitespace-nowrap"
          >
            <RefreshCw
              size={18}
              className={loading ? "animate-spin" : ""}
            />
            Synchroniser
          </button>
        </div>
      </div>
    </header>
  );
}