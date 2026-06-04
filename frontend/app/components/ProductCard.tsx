"use client";

import {
  ShoppingCart,
  Eye,
  BookOpen,
  Globe,
  Calendar,
  Layers3,
} from "lucide-react";

import { Product } from "../types/product";

type Props = {
  product: Product;
  onView: (p: Product) => void;
  onAdd: (p: Product) => void;
};

/**
 * ✅ Product card avec:
 * - Image lazy loading
 * - Stock display
 * - Availability badge
 * - Metadata display
 */
export default function ProductCard({
  product,
  onView,
  onAdd,
}: Props) {
  const isAvailable = (product.stock || 0) > 0;

  return (
    <div className="bg-[#131f34] border border-white/10 rounded-3xl overflow-hidden hover:border-cyan-400/40 transition group">
      
      {/* ✅ Image section */}
      <div className="relative h-72 bg-black overflow-hidden">
        <img
          src={product.image_url || "/placeholder.png"}
          alt={product.titre}
          className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
          loading="lazy"
        />

        {/* ✅ Availability badge */}
        <div className="absolute top-3 right-3">
          <span
            className={`px-3 py-1 rounded-xl text-xs font-black ${
              isAvailable
                ? "bg-emerald-500 text-white"
                : "bg-red-500 text-white"
            }`}
          >
            {isAvailable ? "✓ Disponible" : "✗ Rupture"}
          </span>
        </div>
      </div>

      {/* ✅ Content section */}
      <div className="p-5 flex flex-col h-full">
        
        {/* Title */}
        <h3 className="font-black text-lg line-clamp-2">
          {product.titre}
        </h3>

        {/* Authors */}
        {product.auteurs && (
          <p className="text-slate-400 text-sm mt-1">
            {product.auteurs}
          </p>
        )}

        {/* Metadata */}
        <div className="mt-4 space-y-1 text-sm text-slate-400 flex-grow">
          {product.editeur && (
            <div className="flex gap-2 items-center">
              <BookOpen size={14} />
              <span className="truncate">{product.editeur}</span>
            </div>
          )}

          {product.langue && (
            <div className="flex gap-2 items-center">
              <Globe size={14} />
              <span>{product.langue}</span>
            </div>
          )}

          {product.date_parution && (
            <div className="flex gap-2 items-center">
              <Calendar size={14} />
              <span>{product.date_parution}</span>
            </div>
          )}

          {product.type_produit && (
            <div className="flex gap-2 items-center">
              <Layers3 size={14} />
              <span className="truncate">{product.type_produit}</span>
            </div>
          )}
        </div>

        {/* Price and stock */}
        <div className="mt-5 flex justify-between items-end pb-4 border-b border-white/10">
          <div>
            <div className="text-cyan-400 text-3xl font-black">
              {product.prix?.toLocaleString()}
            </div>
            <div className="text-xs text-slate-500">FCFA</div>
          </div>

          <div className="text-right">
            <div className="text-xs text-slate-400">Stock</div>
            <span className="font-black text-lg">
              {product.stock || 0}
            </span>
          </div>
        </div>

        {/* Action buttons */}
        <div className="grid grid-cols-2 gap-3 mt-5">
          <button
            onClick={() => onView(product)}
            className="h-11 rounded-2xl bg-cyan-400 text-slate-900 font-black flex items-center justify-center gap-2 hover:bg-cyan-300 transition"
          >
            <Eye size={16} />
            Détails
          </button>

          <button
            onClick={() => onAdd(product)}
            disabled={!isAvailable}
            className="h-11 rounded-2xl bg-emerald-500 font-black flex items-center justify-center gap-2 hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ShoppingCart size={16} />
            Ajouter
          </button>
        </div>
      </div>
    </div>
  );
}