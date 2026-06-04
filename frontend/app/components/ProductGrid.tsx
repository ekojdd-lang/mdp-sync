"use client";

import ProductCard from "./ProductCard";
import { Product } from "../types/product";

type Props = {
  products: Product[];
  onView: (p: Product) => void;
  onAdd: (p: Product) => void;
};

/**
 * ✅ Product grid avec:
 * - Responsive grid layout
 * - gencod comme clé unique (au lieu de id)
 * - Empty state handling
 */
export default function ProductGrid({
  products,
  onView,
  onAdd,
}: Props) {
  if (!products || products.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        Aucun produit à afficher
      </div>
    );
  }

  return (
    <div className="grid 2xl:grid-cols-5 xl:grid-cols-4 lg:grid-cols-3 md:grid-cols-2 sm:grid-cols-1 gap-6">
      {products.map((product) => (
        <ProductCard
          key={product.gencod}
          product={product}
          onView={onView}
          onAdd={onAdd}
        />
      ))}
    </div>
  );
}