"use client";

type Props = {
  search: string;
  setSearch: (value: string) => void;

  category: string;
  setCategory: (value: string) => void;

  editor: string;
  setEditor: (value: string) => void;

  categories: string[];
  editors: string[];
};

/**
 * ✅ Product filters avec:
 * - Type produit au lieu de category
 * - Editeur au lieu de publisher
 * - Focus states
 * - Disabled state si pas de données
 */
export default function ProductFilters({
  search,
  setSearch,
  category,
  setCategory,
  editor,
  setEditor,
  categories,
  editors,
}: Props) {
  return (
    <div className="grid lg:grid-cols-3 gap-4">
      
      {/* ✅ Search input */}
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Recherche par titre, auteur, code..."
        className="h-12 rounded-2xl bg-white/5 border border-white/10 px-4 outline-none focus:border-cyan-400 transition text-sm"
      />

      {/* ✅ Category/Type select */}
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="h-12 rounded-2xl bg-white/5 border border-white/10 px-4 outline-none focus:border-cyan-400 transition text-sm"
      >
        <option value="">Tous les types</option>
        {categories.length === 0 ? (
          <option disabled>Chargement...</option>
        ) : (
          categories.map((c) => (
            <option key={c} value={c}>
              {c || "Sans type"}
            </option>
          ))
        )}
      </select>

      {/* ✅ Publisher/Editeur select */}
      <select
        value={editor}
        onChange={(e) => setEditor(e.target.value)}
        className="h-12 rounded-2xl bg-white/5 border border-white/10 px-4 outline-none focus:border-cyan-400 transition text-sm"
      >
        <option value="">Tous les éditeurs</option>
        {editors.length === 0 ? (
          <option disabled>Chargement...</option>
        ) : (
          editors.map((e) => (
            <option key={e} value={e}>
              {e || "Sans éditeur"}
            </option>
          ))
        )}
      </select>
    </div>
  );
}