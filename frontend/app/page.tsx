"use client";

import { useEffect, useState } from "react";
import Image from "next/image";

import {
  Search,
  Bell,
  Package,
  TrendingUp,
  BarChart3,
  Building2,
  Store,
  RefreshCw,
  Eye,
  ShoppingCart,
  Trash2,
  Plus,
  Minus,
  X,
  BookOpen,
  Globe,
  Calendar,
  Layers3,
} from "lucide-react";

// ======================================================
// API
// ======================================================

const API_URL = "http://192.168.1.65:8000";

// ======================================================
// TYPES
// ======================================================

type Product = {
  id: number;

  gencod: string;
  isbn: string;

  titre: string;
  sous_titre?: string;
  auteurs: string;
  editeur: string;
  collection?: string;
  langue?: string;
  date_parution?: string;

  prix: number;
  disponibilite: string;
  stock?: number;

  pages?: number;
  largeur?: string;
  hauteur?: string;
  poids?: string;

  image_url: string;
  presentation: string;

  categorie?: string;

  date_sync: string;
};

type Stats = {
  total_articles: number;
  articles_disponibles: number;
  valeur_catalogue: number;
};

type CartItem = Product & {
  quantity: number;
};

type ArticlesResponse = {
  items: Product[];
  page: number;
  pages: number;
  total: number;
};

// ======================================================
// PAGE
// ======================================================

export default function MaisonPresseERP() {
  const LIMIT = 20;

  // ======================================================
  // STATES
  // ======================================================

  const [products, setProducts] = useState<Product[]>([]);

  const [stats, setStats] = useState<Stats>({
    total_articles: 0,
    articles_disponibles: 0,
    valeur_catalogue: 0,
  });

  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(false);

  const [apiError, setApiError] = useState("");

  const [selectedProduct, setSelectedProduct] =
    useState<Product | null>(null);

  const [cart, setCart] = useState<CartItem[]>([]);

  const [page, setPage] = useState(1);

  const [pages, setPages] = useState(1);

  // ======================================================
  // LOAD DATA
  // ======================================================

  async function loadData(currentPage = 1) {
    try {
      setLoading(true);
      setApiError("");

      const articlesUrl =
        `${API_URL}/api/articles?page=${currentPage}&limit=${LIMIT}&search=${encodeURIComponent(search)}`;

      const statsUrl = `${API_URL}/api/stats`;

      const results = await Promise.allSettled([
        fetch(articlesUrl),
        fetch(statsUrl),
      ]);

      const articlesResult = results[0];
      const statsResult = results[1];

      // ARTICLES

      if (
        articlesResult.status === "fulfilled" &&
        articlesResult.value.ok
      ) {
        const articlesData: ArticlesResponse =
          await articlesResult.value.json();

        setProducts(
          Array.isArray(articlesData.items)
            ? articlesData.items
            : []
        );

        setPage(articlesData.page || 1);

        setPages(articlesData.pages || 1);
      } else {
        setProducts([]);
        console.error(
          "Articles API error",
          articlesResult
        );
      }

      // STATS

      if (
        statsResult.status === "fulfilled" &&
        statsResult.value.ok
      ) {
        const statsData: Stats =
          await statsResult.value.json();

        setStats({
          total_articles:
            statsData.total_articles || 0,

          articles_disponibles:
            statsData.articles_disponibles || 0,

          valeur_catalogue:
            statsData.valeur_catalogue || 0,
        });
      } else {
        console.error(
          "Stats API error",
          statsResult
        );

        setStats({
          total_articles: 0,
          articles_disponibles: 0,
          valeur_catalogue: 0,
        });
      }
    } catch (error) {
      console.error(error);

      setApiError(
        "Impossible de joindre le serveur FastAPI."
      );

      setProducts([]);
    } finally {
      setLoading(false);
    }
  }

  // ======================================================
  // EFFECTS
  // ======================================================

  useEffect(() => {
    loadData(1);
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      loadData(1);
    }, 500);

    return () => clearTimeout(timeout);
  }, [search]);

  // ======================================================
  // CART
  // ======================================================

  function addToCart(product: Product) {
    setCart((prev) => {
      const existing = prev.find(
        (item) => item.id === product.id
      );

      if (existing) {
        return prev.map((item) =>
          item.id === product.id
            ? {
                ...item,
                quantity:
                  item.quantity + 1,
              }
            : item
        );
      }

      return [
        ...prev,
        {
          ...product,
          quantity: 1,
        },
      ];
    });
  }

  function increaseQuantity(id: number) {
    setCart((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              quantity:
                item.quantity + 1,
            }
          : item
      )
    );
  }

  function decreaseQuantity(id: number) {
    setCart((prev) =>
      prev
        .map((item) =>
          item.id === id
            ? {
                ...item,
                quantity:
                  item.quantity - 1,
              }
            : item
        )
        .filter(
          (item) => item.quantity > 0
        )
    );
  }

  function removeFromCart(id: number) {
    setCart((prev) =>
      prev.filter(
        (item) => item.id !== id
      )
    );
  }

  // ======================================================
  // PDF
  // ======================================================

  async function generateQuotationPDF() {
    try {
      if (cart.length === 0) {
        alert("Le panier est vide");
        return;
      }

      const response = await fetch(
        `${API_URL}/api/devis/pdf`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            client: "Client ERP",

            articles: cart.map(
              (item) => ({
                gencod: item.gencod,
                isbn: item.isbn,
                titre: item.titre,
                auteurs: item.auteurs,
                editeur: item.editeur,
                prix: item.prix,
                disponibilite:
                  item.disponibilite,
                image_url:
                  item.image_url,
                presentation:
                  item.presentation,
                categorie:
                  item.categorie,
                langue: item.langue,
                nombre_pages:
                  item.pages,
                date_parution:
                  item.date_parution,
                stock: item.stock,
                quantity:
                  item.quantity,
              })
            ),
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Erreur génération PDF"
        );
      }

      const blob =
        await response.blob();

      const url =
        window.URL.createObjectURL(
          blob
        );

      const link =
        document.createElement("a");

      link.href = url;

      link.download =
        "devis_mdp.pdf";

      document.body.appendChild(
        link
      );

      link.click();

      link.remove();

      window.URL.revokeObjectURL(
        url
      );
    } catch (error) {
      console.error(error);

      alert(
        "Impossible de générer le PDF"
      );
    }
  }

  // ======================================================
  // TOTAL
  // ======================================================

  const cartTotal = cart.reduce(
    (total, item) =>
      total +
      item.prix * item.quantity,
    0
  );

  // ======================================================
  // RENDER
  // ======================================================

  return (
    <div className="min-h-screen bg-[#07111f] text-white">
      {/* SIDEBAR */}

      <aside className="fixed left-0 top-0 h-screen w-24 bg-[#0b1628] border-r border-white/10 hidden xl:flex flex-col items-center py-6 z-40">
        <div className="w-16 h-16 rounded-2xl bg-white flex items-center justify-center overflow-hidden shadow-2xl">
          <Image
            src="/logo.png"
            alt="Logo"
            width={44}
            height={44}
          />
        </div>

        <div className="mt-10 flex flex-col gap-4">
          {[BarChart3, Package, Store, Building2].map(
            (Icon, index) => (
              <button
                key={index}
                className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center hover:bg-cyan-400 hover:text-slate-900 transition-all duration-300"
              >
                <Icon size={22} />
              </button>
            )
          )}
        </div>

        <div className="mt-auto">
          <button className="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 flex items-center justify-center">
            <Bell size={20} />
          </button>
        </div>
      </aside>

      {/* MAIN */}

      <div className="xl:ml-24">
        {/* HEADER */}

        <header className="sticky top-0 z-30 bg-[#0b1628]/90 backdrop-blur-xl border-b border-white/10">
          <div className="max-w-[1700px] mx-auto px-6 py-5 flex flex-col xl:flex-row gap-5 xl:items-center xl:justify-between">
            <div>
              <h1 className="text-4xl font-black tracking-tight">
                Maison de la Presse ERP
              </h1>

              <p className="text-slate-400 mt-1">
                Gestion moderne du catalogue
              </p>
            </div>

            <div className="flex flex-col md:flex-row gap-4">
              {/* SEARCH */}

              <div className="relative">
                <Search
                  className="absolute left-4 top-3.5 text-slate-500"
                  size={18}
                />

                <input
                  type="text"
                  placeholder="Rechercher un livre..."
                  value={search}
                  onChange={(e) =>
                    setSearch(
                      e.target.value
                    )
                  }
                  className="w-full md:w-96 h-12 rounded-2xl bg-white/5 border border-white/10 pl-11 pr-4 outline-none focus:ring-2 focus:ring-cyan-400"
                />
              </div>

              {/* CART */}

              <div className="h-12 px-5 rounded-2xl bg-emerald-500 flex items-center gap-3 font-black">
                <ShoppingCart size={18} />
                {cart.length}
              </div>

              {/* SYNC */}

              <button
                onClick={() =>
                  loadData(page)
                }
                disabled={loading}
                className="h-12 px-5 rounded-2xl bg-cyan-400 text-slate-900 font-black flex items-center gap-3 disabled:opacity-50"
              >
                <RefreshCw
                  size={18}
                  className={
                    loading
                      ? "animate-spin"
                      : ""
                  }
                />

                {loading
                  ? "Synchronisation..."
                  : "Synchroniser"}
              </button>
            </div>
          </div>
        </header>

        {/* CONTENT */}

        <main className="max-w-[1700px] mx-auto p-6 space-y-8">
          {/* ERROR */}

          {apiError && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-2xl p-4 flex items-center gap-3">
              <X size={18} />
              {apiError}
            </div>
          )}

          {/* STATS */}

          <section className="grid xl:grid-cols-4 md:grid-cols-2 gap-5">
            {[
              {
                title:
                  "Produits actifs",
                value:
                  stats.total_articles,
                icon: Package,
              },

              {
                title:
                  "Disponibles",
                value:
                  stats.articles_disponibles,
                icon: TrendingUp,
              },

              {
                title:
                  "Valeur catalogue",
                value: `${stats.valeur_catalogue.toFixed(
                  0
                )} FCFA`,
                icon: Building2,
              },

              {
                title: "Agences",
                value: "03",
                icon: Store,
              },
            ].map((item, index) => (
              <div
                key={index}
                className="bg-[#101b2d] border border-white/10 rounded-3xl p-6"
              >
                <div className="w-14 h-14 rounded-2xl bg-cyan-400/10 flex items-center justify-center">
                  <item.icon className="text-cyan-400" />
                </div>

                <p className="text-slate-400 mt-5">
                  {item.title}
                </p>

                <h3 className="text-4xl font-black mt-2">
                  {item.value}
                </h3>
              </div>
            ))}
          </section>

          {/* PRODUCTS */}

          <section className="bg-[#101b2d] border border-white/10 rounded-3xl overflow-hidden">
            {/* TOP */}

            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-black">
                  Catalogue
                </h2>

                <p className="text-slate-400 mt-1">
                  Catalogue synchronisé
                </p>
              </div>

              <div className="text-cyan-400 font-black">
                {products.length} produits
              </div>
            </div>

            {/* LOADING */}

            {loading && (
              <div className="p-10 text-center text-slate-400">
                Chargement...
              </div>
            )}

            {/* EMPTY */}

            {!loading &&
              products.length === 0 && (
                <div className="p-10 text-center text-slate-400">
                  Aucun produit trouvé
                </div>
              )}

            {/* GRID */}

            <div className="grid 2xl:grid-cols-5 xl:grid-cols-4 lg:grid-cols-3 md:grid-cols-2 gap-6 p-6">
              {products.map((product) => (
                <div
                  key={product.id}
                  className="bg-[#131f34] border border-white/10 rounded-3xl overflow-hidden hover:border-cyan-400/40 transition-all duration-300 hover:-translate-y-1"
                >
                  {/* IMAGE */}

                  <div className="relative h-72 bg-black overflow-hidden">
                    <img
                      src={
                        product.image_url ||
                        "/placeholder.png"
                      }
                      alt={product.titre}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    />

                    <div className="absolute top-3 right-3">
                      <span
                        className={`px-3 py-1 rounded-xl text-xs font-black ${
                          product.disponibilite ===
                          "1"
                            ? "bg-emerald-500 text-white"
                            : "bg-red-500 text-white"
                        }`}
                      >
                        {product.disponibilite ===
                        "1"
                          ? "Disponible"
                          : "Rupture"}
                      </span>
                    </div>
                  </div>

                  {/* BODY */}

                  <div className="p-5">
                    <h3 className="font-black text-lg leading-tight line-clamp-2 min-h-[56px]">
                      {product.titre}
                    </h3>

                    <p className="text-slate-400 mt-2 line-clamp-1">
                      {product.auteurs}
                    </p>

                    {/* META */}

                    <div className="mt-5 space-y-3">
                      <div className="flex items-center gap-2 text-sm text-slate-300">
                        <BookOpen
                          size={16}
                          className="text-cyan-400"
                        />

                        <span className="truncate">
                          {product.editeur}
                        </span>
                      </div>

                      {product.langue && (
                        <div className="flex items-center gap-2 text-sm text-slate-300">
                          <Globe
                            size={16}
                            className="text-cyan-400"
                          />

                          {product.langue}
                        </div>
                      )}

                      {product.date_parution && (
                        <div className="flex items-center gap-2 text-sm text-slate-300">
                          <Calendar
                            size={16}
                            className="text-cyan-400"
                          />

                          {
                            product.date_parution
                          }
                        </div>
                      )}

                      {product.categorie && (
                        <div className="flex items-center gap-2 text-sm text-slate-300">
                          <Layers3
                            size={16}
                            className="text-cyan-400"
                          />

                          {
                            product.categorie
                          }
                        </div>
                      )}
                    </div>

                    {/* PRICE */}

                    <div className="mt-6 flex items-end justify-between">
                      <div>
                        <div className="text-3xl font-black text-cyan-400">
                          {product.prix?.toLocaleString()}
                        </div>

                        <div className="text-xs text-slate-500">
                          FCFA
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="text-xs text-slate-500">
                          Stock
                        </div>

                        <div className="font-black text-xl">
                          {product.stock || 0}
                        </div>
                      </div>
                    </div>

                    {/* ACTIONS */}

                    <div className="grid grid-cols-2 gap-3 mt-6">
                      <button
                        onClick={() =>
                          setSelectedProduct(
                            product
                          )
                        }
                        className="h-11 rounded-2xl bg-cyan-400 text-slate-900 font-black flex items-center justify-center gap-2"
                      >
                        <Eye size={16} />
                        Détails
                      </button>

                      <button
                        onClick={() =>
                          addToCart(product)
                        }
                        className="h-11 rounded-2xl bg-emerald-500 text-white font-black flex items-center justify-center gap-2"
                      >
                        <ShoppingCart
                          size={16}
                        />
                        Ajouter
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* PAGINATION */}

            <div className="border-t border-white/10 p-6 flex items-center justify-center gap-4">
              <button
                disabled={page <= 1}
                onClick={() =>
                  loadData(page - 1)
                }
                className="px-5 h-11 rounded-2xl bg-white/5 border border-white/10 disabled:opacity-30"
              >
                Précédent
              </button>

              <div className="px-5 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center">
                Page {page} / {pages}
              </div>

              <button
                disabled={page >= pages}
                onClick={() =>
                  loadData(page + 1)
                }
                className="px-5 h-11 rounded-2xl bg-cyan-400 text-slate-900 font-black disabled:opacity-30"
              >
                Suivant
              </button>
            </div>
          </section>

          {/* CART */}

          <section className="bg-[#101b2d] border border-white/10 rounded-3xl p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-black">
                Panier ERP
              </h2>

              <div className="text-cyan-400 font-black">
                {cart.length} article(s)
              </div>
            </div>

            <div className="mt-6 space-y-4">
              {cart.length === 0 && (
                <div className="text-slate-400">
                  Aucun article ajouté
                </div>
              )}

              {cart.map((item) => (
                <div
                  key={item.id}
                  className="bg-white/5 border border-white/10 rounded-2xl p-4 flex flex-col lg:flex-row gap-5 lg:items-center lg:justify-between"
                >
                  <div className="flex items-center gap-4">
                    <img
                      src={item.image_url}
                      alt={item.titre}
                      className="w-20 h-28 rounded-xl object-cover"
                    />

                    <div>
                      <h3 className="font-black text-lg">
                        {item.titre}
                      </h3>

                      <p className="text-slate-400 mt-1">
                        {item.auteurs}
                      </p>

                      <div className="text-cyan-400 font-black mt-3">
                        {item.prix.toLocaleString()}{" "}
                        FCFA
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {/* QUANTITY */}

                    <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-2xl px-4 py-3">
                      <button
                        onClick={() =>
                          decreaseQuantity(
                            item.id
                          )
                        }
                      >
                        <Minus size={16} />
                      </button>

                      <span className="font-black text-lg min-w-[30px] text-center">
                        {item.quantity}
                      </span>

                      <button
                        onClick={() =>
                          increaseQuantity(
                            item.id
                          )
                        }
                      >
                        <Plus size={16} />
                      </button>
                    </div>

                    {/* TOTAL */}

                    <div className="text-2xl font-black text-cyan-400 min-w-[160px] text-right">
                      {(
                        item.prix *
                        item.quantity
                      ).toLocaleString()}{" "}
                      FCFA
                    </div>

                    {/* DELETE */}

                    <button
                      onClick={() =>
                        removeFromCart(
                          item.id
                        )
                      }
                      className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 flex items-center justify-center"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {cart.length > 0 && (
              <>
                <div className="mt-8 border-t border-white/10 pt-6 flex items-center justify-between">
                  <div className="text-2xl font-black">
                    Total ERP
                  </div>

                  <div className="text-4xl font-black text-cyan-400">
                    {cartTotal.toLocaleString()}{" "}
                    FCFA
                  </div>
                </div>

                <div className="mt-6 flex flex-wrap gap-4">
                  <button
                    onClick={
                      generateQuotationPDF
                    }
                    className="h-12 px-6 rounded-2xl bg-cyan-400 text-slate-900 font-black"
                  >
                    Générer devis PDF
                  </button>

                  <button
                    onClick={() =>
                      setCart([])
                    }
                    className="h-12 px-6 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 font-black"
                  >
                    Vider panier
                  </button>
                </div>
              </>
            )}
          </section>
        </main>
      </div>

      {/* MODAL */}

      {selectedProduct && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="w-full max-w-6xl bg-[#101b2d] border border-white/10 rounded-3xl overflow-hidden">
            <div className="grid lg:grid-cols-[420px_1fr]">
              {/* IMAGE */}

              <div className="bg-black">
                <img
                  src={
                    selectedProduct.image_url
                  }
                  alt={
                    selectedProduct.titre
                  }
                  className="w-full h-full object-cover"
                />
              </div>

              {/* CONTENT */}

              <div className="p-8 relative overflow-y-auto max-h-[90vh]">
                {/* CLOSE */}

                <button
                  onClick={() =>
                    setSelectedProduct(
                      null
                    )
                  }
                  className="absolute top-5 right-5 w-11 h-11 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center"
                >
                  <X size={18} />
                </button>

                {/* TITLE */}

                <h2 className="text-4xl font-black pr-16">
                  {
                    selectedProduct.titre
                  }
                </h2>

                <p className="text-slate-400 mt-3 text-lg">
                  {
                    selectedProduct.auteurs
                  }
                </p>

                {/* INFOS */}

                <div className="grid md:grid-cols-2 gap-4 mt-8">
                  {[
                    {
                      label: "ISBN",
                      value:
                        selectedProduct.isbn ||
                        selectedProduct.gencod,
                    },

                    {
                      label: "Éditeur",
                      value:
                        selectedProduct.editeur,
                    },

                    {
                      label: "Langue",
                      value:
                        selectedProduct.langue,
                    },

                    {
                      label: "Parution",
                      value:
                        selectedProduct.date_parution,
                    },

                    {
                      label: "Pages",
                      value:
                        selectedProduct.pages,
                    },

                    {
                      label: "Stock",
                      value:
                        selectedProduct.stock,
                    },

                    {
                      label: "Catégorie",
                      value:
                        selectedProduct.categorie,
                    },
                  ]
                    .filter(
                      (item) => item.value
                    )
                    .map((item, index) => (
                      <div
                        key={index}
                        className="bg-white/5 border border-white/10 rounded-2xl p-5"
                      >
                        <p className="text-slate-500 text-sm">
                          {item.label}
                        </p>

                        <p className="font-black mt-2 text-lg">
                          {item.value}
                        </p>
                      </div>
                    ))}
                </div>

                {/* PRICE */}

                <div className="grid md:grid-cols-2 gap-4 mt-6">
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
                    <p className="text-slate-500 text-sm">
                      Prix
                    </p>

                    <div className="text-4xl font-black text-cyan-400 mt-3">
                      {
                        selectedProduct.prix
                      }{" "}
                      FCFA
                    </div>
                  </div>

                  <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
                    <p className="text-slate-500 text-sm">
                      Disponibilité
                    </p>

                    <div
                      className={`text-2xl font-black mt-3 ${
                        selectedProduct.disponibilite ===
                        "1"
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      {selectedProduct.disponibilite ===
                      "1"
                        ? "Disponible"
                        : "Rupture"}
                    </div>
                  </div>
                </div>

                {/* PRESENTATION */}

                <div className="mt-8">
                  <h3 className="text-2xl font-black mb-4">
                    Présentation
                  </h3>

                  <div className="bg-white/5 border border-white/10 rounded-2xl p-5 text-slate-300 leading-relaxed whitespace-pre-line">
                    {
                      selectedProduct.presentation
                    }
                  </div>
                </div>

                {/* BTN */}

                <button
                  onClick={() =>
                    addToCart(
                      selectedProduct
                    )
                  }
                  className="w-full h-14 mt-8 rounded-2xl bg-emerald-500 text-white font-black flex items-center justify-center gap-3 text-lg"
                >
                  <ShoppingCart
                    size={20}
                  />

                  Ajouter au panier
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}