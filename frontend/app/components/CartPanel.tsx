"use client";

import type { CartItem } from "../types/product";

interface Props {
  cart: CartItem[];
  total: number;
  increaseQuantity: (gencod: string) => void;  // ✅ gencod: string
  decreaseQuantity: (gencod: string) => void;  // ✅ gencod: string
  removeFromCart: (gencod: string) => void;    // ✅ gencod: string
  clearCart: () => void;
  generateQuotationPDF: () => void;
  loading?: boolean;
}

export default function CartPanel({
  cart,
  total,
  increaseQuantity,
  decreaseQuantity,
  removeFromCart,
  clearCart,
  generateQuotationPDF,
  loading = false,
}: Props) {
  if (cart.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 text-center text-gray-400">
        Panier vide
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 space-y-4">
      <h2 className="text-xl font-bold">Panier ({cart.length})</h2>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {cart.map((item) => (
          <div
            key={item.gencod}
            className="flex justify-between items-center bg-gray-700 p-3 rounded"
          >
            <div>
              <p className="font-semibold">{item.titre}</p>
              <p className="text-sm text-gray-400">{item.gencod}</p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => decreaseQuantity(item.gencod)}
                disabled={loading}
                className="px-2 py-1 bg-red-600 rounded"
              >
                −
              </button>
              <span className="w-8 text-center">{item.quantity}</span>
              <button
                onClick={() => increaseQuantity(item.gencod)}
                disabled={loading}
                className="px-2 py-1 bg-green-600 rounded"
              >
                +
              </button>
              <button
                onClick={() => removeFromCart(item.gencod)}
                disabled={loading}
                className="px-2 py-1 bg-gray-600 rounded text-sm"
              >
                ✕
              </button>
            </div>

            <div className="text-right">
              <p className="font-semibold">{(item.prix * item.quantity).toFixed(2)} FCFA</p>
              <p className="text-sm text-gray-400">{item.prix} FCFA × {item.quantity}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-gray-600 pt-4">
        <div className="flex justify-between text-lg font-bold mb-4">
          <span>Total:</span>
          <span>{total.toFixed(2)} FCFA</span>
        </div>

        <div className="flex gap-2">
          <button
            onClick={clearCart}
            disabled={loading}
            className="flex-1 bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded disabled:opacity-50"
          >
            Vider
          </button>
          <button
            onClick={generateQuotationPDF}
            disabled={loading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded disabled:opacity-50"
          >
            📄 PDF
          </button>
        </div>
      </div>
    </div>
  );
}