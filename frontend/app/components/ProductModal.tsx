"use client";

import { X, ShoppingCart, AlertCircle } from "lucide-react";
import { Product } from "../types/product";

type Props = {
  product: Product | null;
  onClose: () => void;
  onAddToCart: (product: Product) => void;
};

/**
 * ✅ Product modal avec:
 * - Image lazy loading
 * - Stock status badge
 * - Formatted dates
 * - Presentation text handling
 * - Add to cart button
 */
export default function ProductModal({
  product,
  onClose,
  onAddToCart,
}: Props) {
  if (!product) return null;

  const isAvailable = (product.stock || 0) > 0;

  // ✅ Format date safely
  const formatDate = (date: string | undefined) => {
    if (!date) return "";
    try {
      return new Date(date).toLocaleDateString("fr-FR");
    } catch {
      return date;
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-[#101b2d] rounded-3xl border border-white/10 overflow-hidden max-h-[90vh] overflow-y-auto">
        
        <div className="grid lg:grid-cols-[350px_1fr] gap-0">
          
          {/* ===== IMAGE SECTION ===== */}
          <div className="bg-black relative aspect-square lg:aspect-auto">
            <img
              src={product.image_url || "/placeholder.png"}
              alt={product.titre}
              className="w-full h-full object-cover"
              loading="lazy"
            />

            {/* ✅ Stock badge */}
            <div className="absolute top-3 right-3">
              <span
                className={`px-3 py-1 rounded-xl text-xs font-black ${
                  isAvailable
                    ? "bg-emerald-500 text-white"
                    : "bg-red-500 text-white"
                }`}
              >
                {isAvailable ? "✓ Stock" : "✗ Rupture"}
              </span>
            </div>
          </div>

          {/* ===== CONTENT SECTION ===== */}
          <div className="relative p-6 lg:p-8 flex flex-col">
            
            {/* Close button */}
            <button
              onClick={onClose}
              className="absolute top-5 right-5 w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 transition"
              aria-label="Fermer"
            >
              <X size={20} />
            </button>

            {/* ===== HEADER ===== */}
            <div className="pr-12 mb-6">
              <h2 className="text-3xl lg:text-4xl font-black leading-tight">
                {product.titre}
              </h2>

              {product.sous_titre && (
                <p className="text-slate-400 mt-2 text-sm lg:text-base">
                  {product.sous_titre}
                </p>
              )}

              {product.auteurs && (
                <p className="text-lg text-slate-300 mt-3">
                  <span className="text-slate-500">Par: </span>
                  {product.auteurs}
                </p>
              )}
            </div>

            {/* ===== METADATA GRID ===== */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3 mb-6">
              {[
                { label: "Code", value: product.gencod },
                { label: "ISBN", value: product.isbn },
                { label: "Éditeur", value: product.editeur },
                { label: "Collection", value: product.collection },
                { label: "Langue", value: product.langue },
                { label: "Pages", value: product.nombre_pages },
                { label: "Type", value: product.type_produit },
                { label: "Parution", value: formatDate(product.date_parution) },
                { label: "Largeur", value: product.largeur },
                { label: "Hauteur", value: product.hauteur },
                { label: "Poids", value: product.poids },
              ]
                .filter(
                  (item) =>
                    item.value !== undefined &&
                    item.value !== null &&
                    item.value !== ""
                )
                .map((item, index) => (
                  <div
                    key={index}
                    className="bg-white/5 border border-white/10 rounded-xl p-3"
                  >
                    <div className="text-xs text-slate-500 uppercase tracking-wide">
                      {item.label}
                    </div>
                    <div className="mt-1 font-semibold text-sm line-clamp-1">
                      {item.value}
                    </div>
                  </div>
                ))}
            </div>

            {/* ===== PRICE & STOCK ===== */}
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div className="bg-gradient-to-br from-cyan-500/20 to-cyan-500/5 border border-cyan-500/30 rounded-2xl p-5">
                <div className="text-sm text-cyan-400 uppercase tracking-wide">Prix</div>
                <div className="text-3xl lg:text-4xl font-black text-cyan-400 mt-2">
                  {Number(product.prix || 0).toLocaleString("fr-FR")}
                </div>
                <div className="text-xs text-slate-500 mt-1">FCFA</div>
              </div>

              <div
                className={`border rounded-2xl p-5 ${
                  isAvailable
                    ? "bg-gradient-to-br from-emerald-500/20 to-emerald-500/5 border-emerald-500/30"
                    : "bg-gradient-to-br from-red-500/20 to-red-500/5 border-red-500/30"
                }`}
              >
                <div className="text-sm uppercase tracking-wide">
                  {isAvailable ? (
                    <span className="text-emerald-400">Disponibilité</span>
                  ) : (
                    <span className="text-red-400">Statut</span>
                  )}
                </div>
                <div
                  className={`text-2xl font-black mt-2 ${
                    isAvailable
                      ? "text-emerald-400"
                      : "text-red-400"
                  }`}
                >
                  {isAvailable ? "En stock" : "Rupture"}
                </div>
                <div className="text-xs mt-1">
                  {isAvailable ? (
                    <span className="text-emerald-500">{product.stock} unité(s)</span>
                  ) : (
                    <span className="text-red-500">Non disponible</span>
                  )}
                </div>
              </div>
            </div>

            {/* ===== DESCRIPTION ===== */}
            {product.presentation && (
              <div className="mb-6">
                <h3 className="text-lg font-black mb-3">Présentation</h3>
                <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                  {product.presentation}
                </div>
              </div>
            )}

            {/* ===== LAST SYNC ===== */}
            {product.date_sync && (
              <div className="text-xs text-slate-500 mb-6">
                Dernière synchronisation: {formatDate(product.date_sync)}
              </div>
            )}

            {/* ===== ACTION BUTTON ===== */}
            <button
              onClick={() => onAddToCart(product)}
              disabled={!isAvailable}
              className="mt-auto h-13 w-full rounded-2xl bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed font-black text-lg flex items-center justify-center gap-3 transition"
            >
              <ShoppingCart size={20} />
              {isAvailable ? "Ajouter au panier" : "Indisponible"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}