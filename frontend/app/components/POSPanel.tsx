"use client";

interface Props {
  total: number;
  onCheckout: () => Promise<void>;
  loading?: boolean;
}

export default function POSPanel({
  total,
  onCheckout,
  loading = false,
}: Props) {
  return (
    <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-lg p-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">Total: {total.toFixed(2)} FCFA</h2>
          <p className="text-green-100 text-sm">Cliquez pour valider la vente</p>
        </div>

        <button
          onClick={onCheckout}
          disabled={loading || total === 0}
          className="bg-white text-green-700 font-bold px-8 py-4 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? "⏳ Validation..." : "✅ Valider la vente"}
        </button>
      </div>
    </div>
  );
}