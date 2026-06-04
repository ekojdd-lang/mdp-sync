"use client";

import {
  Package,
  TrendingUp,
  DollarSign,
  BarChart3,
} from "lucide-react";

import { Stats } from "../types/product";

/**
 * ✅ Dashboard KPIs avec:
 * - available_articles (correct field name)
 * - inventory_value (au lieu de valeur_catalogue)
 * - total_stock
 * - Couleurs distinctes
 */
export default function DashboardKPIs({
  stats,
}: {
  stats: Stats;
}) {
  const cards = [
    {
      title: "Produits actifs",
      value: stats.total_articles.toLocaleString(),
      icon: Package,
      color: "bg-blue-500/20 text-blue-400",
    },
    {
      title: "Disponibles",
      value: stats.available_articles.toLocaleString(),
      icon: TrendingUp,
      color: "bg-green-500/20 text-green-400",
    },
    {
      title: "Valeur catalogue",
      value: `${stats.inventory_value.toLocaleString("fr-FR", {
        maximumFractionDigits: 0,
      })} FCFA`,
      icon: DollarSign,
      color: "bg-cyan-500/20 text-cyan-400",
    },
    {
      title: "Stock total",
      value: (stats.total_stock || 0).toLocaleString(),
      icon: BarChart3,
      color: "bg-purple-500/20 text-purple-400",
    },
  ];

  return (
    <section className="grid xl:grid-cols-4 md:grid-cols-2 gap-5">
      {cards.map((item, index) => (
        <div
          key={index}
          className="bg-[#101b2d] border border-white/10 rounded-3xl p-6 hover:border-white/20 transition"
        >
          {/* ✅ Icon with background */}
          <div className={`inline-block p-3 rounded-xl ${item.color} mb-4`}>
            <item.icon size={24} />
          </div>

          {/* ✅ Title */}
          <p className="text-slate-400 text-sm">{item.title}</p>

          {/* ✅ Value */}
          <h3 className="text-2xl font-black mt-2">
            {item.value}
          </h3>
        </div>
      ))}
    </section>
  );
}