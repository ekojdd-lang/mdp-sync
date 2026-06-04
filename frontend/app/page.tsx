'use client';

import { useEffect, useState, useRef, useCallback } from 'react';

import ERPHeader from './components/ERPHeader';
import DashboardKPIs from './components/DashboardKPIs';
import ProductFilters from './components/ProductFilters';
import ProductGrid from './components/ProductGrid';
import ProductModal from './components/ProductModal';
import CartPanel from './components/CartPanel';
import POSPanel from './components/POSPanel';
import Pagination from './components/Pagination';
import RealtimeStatus from './components/RealtimeStatus';

import { Product, Stats } from './types/product';

import { useCart } from './hooks/useCart';
import { useDebounce } from './hooks/useDebounce';
import { useWebSocket } from './hooks/useWebSocket';

// =========================================================
// CONFIG
// =========================================================
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const LIMIT = 20;
const REQUEST_TIMEOUT = 10000; // 10s

// =========================================================
// TYPES
// =========================================================
interface LoadDataOptions {
  page?: number;
  preservePage?: boolean;
}

// =========================================================
// MAIN COMPONENT
// =========================================================
export default function MaisonPresseERP() {
  // ===== STATE =====
  const [products, setProducts] = useState<Product[]>([]);
  const [stats, setStats] = useState<Stats>({
    total_articles: 0,
    available_articles: 0,
    inventory_value: 0,
  });

  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);

  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [publisher, setPublisher] = useState('');

  const [categories, setCategories] = useState<string[]>([]);
  const [publishers, setPublishers] = useState<string[]>([]);

  // ===== REFS =====
  const abortControllerRef = useRef<AbortController | null>(null);
  const loadTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ===== HOOKS =====
  const debouncedSearch = useDebounce(search, 400);

  const {
    cart,
    total: cartTotal,
    addToCart,
    increaseQuantity,
    decreaseQuantity,
    removeFromCart,
    clearCart,
  } = useCart();

  const { connected, lastMessage } = useWebSocket(
    API_URL.replace('http', 'ws') + '/ws/catalog'
  );

  // =========================================================
  // FETCH WITH TIMEOUT & RETRY
  // =========================================================
  async function fetchWithTimeout(
    url: string,
    options: RequestInit = {},
    retries = 2
  ): Promise<Response> {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...options.headers,
          },
          mode: 'cors',
          credentials: 'include',
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          // ✅ Properly throw error with message
          const errorMsg = `HTTP ${response.status}: ${response.statusText}`;
          throw new Error(errorMsg);
        }

        return response;

      } catch (err: unknown) {
        // ✅ Properly handle error type
        const errorMessage = err instanceof Error ? err.message : String(err);

        if (loadTimeoutRef.current) {
          clearTimeout(loadTimeoutRef.current);
        }

        if (errorMessage.includes('AbortError') || errorMessage.includes('abort')) {
          throw new Error('Requête timeout');
        }

        if (attempt < retries) {
          console.warn(`⚠️ Tentative ${attempt} échouée, retry...`);
          await new Promise(r => setTimeout(r, 1000 * attempt));
          continue;
        }

        throw new Error(errorMessage);
      }
    }

    throw new Error('Impossible de joindre le serveur');
  }

  // =========================================================
  // LOAD DATA
  // =========================================================
  const loadData = useCallback(
    async (options: LoadDataOptions = {}) => {
      const currentPage = options.page || 1;

      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
      }

      try {
        setLoading(true);
        setApiError('');

        const url = new URL(`${API_URL}/api/articles`);
        url.searchParams.set('page', String(currentPage));
        url.searchParams.set('limit', String(LIMIT));

        if (debouncedSearch) {
          url.searchParams.set('search', debouncedSearch);
        }

        if (category) {
          url.searchParams.set('type_produit', category);
        }

        if (publisher) {
          url.searchParams.set('editeur', publisher);
        }

        console.log('📡 Loading from:', url.toString());

        const [articlesRes, statsRes, filtersRes] = await Promise.all([
          fetchWithTimeout(url.toString()),
          fetchWithTimeout(`${API_URL}/api/stats`),
          fetchWithTimeout(`${API_URL}/api/filters`),
        ]);

        // ✅ Parse articles
        const articleData = await articlesRes.json();
        setProducts(articleData.items || []);
        setPage(articleData.page || 1);
        setPages(articleData.pages || 1);

        // ✅ Parse stats
        const statsData = await statsRes.json();
        setStats({
          total_articles: statsData.total_articles || 0,
          available_articles: statsData.available_articles || 0,
          inventory_value: statsData.inventory_value || 0,
          total_stock: statsData.total_stock,
          average_price: statsData.average_price,
        });

        // ✅ Parse filters
        const filtersData = await filtersRes.json();
        setCategories(
          (filtersData.type_produits || [])
            .filter((c: string) => c)
            .sort()
        );
        setPublishers(
          (filtersData.publishers || [])
            .filter((p: string) => p)
            .sort()
        );

      } catch (err: unknown) {
        // ✅ Properly handle error type
        const errorMessage = err instanceof Error ? err.message : String(err);
        console.error('❌ Load error:', errorMessage);

        let displayError = 'Erreur de connexion';

        if (errorMessage.includes('timeout')) {
          displayError = 'Serveur indisponible (timeout)';
        } else if (errorMessage.includes('HTTP')) {
          displayError = `Erreur serveur: ${errorMessage}`;
        } else if (errorMessage.includes('Failed to fetch')) {
          displayError = 'CORS error - Vérifiez votre configuration';
        }

        setApiError(displayError);
        setProducts([]);

      } finally {
        setLoading(false);
      }
    },
    [debouncedSearch, category, publisher]
  );

  // =========================================================
  // WEBSOCKET HANDLER
  // =========================================================
  useEffect(() => {
    if (!lastMessage) return;

    try {
      const payload = JSON.parse(lastMessage);

      console.log('📩 WebSocket message:', payload.type);

      if (payload.type === 'sync_completed') {
        console.log('🔄 Sync completed, reloading data...');
        loadData({ preservePage: true });
      } else if (payload.type === 'stock_updated') {
        console.log('📦 Stock updated, reloading...');
        loadData({ preservePage: true });
      }

    } catch (e) {
      console.debug('⏭️ WebSocket message ignored (not JSON)');
    }

  }, [lastMessage, loadData]);

  // =========================================================
  // INIT: Load data on mount
  // =========================================================
  useEffect(() => {
    loadData({ page: 1 });

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
      }
    };

  }, []);

  // =========================================================
  // RELOAD ON FILTERS
  // =========================================================
  useEffect(() => {
    loadData({ page: 1 });
  }, [debouncedSearch, category, publisher, loadData]);

  // =========================================================
  // VALIDATE SALE
  // =========================================================
  async function validateSale() {
    if (cart.length === 0) {
      alert('Panier vide');
      return;
    }

    try {
      setLoading(true);

      const response = await fetchWithTimeout(
        `${API_URL}/api/pos/sale`,
        {
          method: 'POST',
          body: JSON.stringify({
            articles: cart,
            total: cartTotal,
          }),
        }
      );

      const result = await response.json();

      clearCart();
      loadData({ preservePage: true });

      alert(
        `✅ Vente enregistrée\n${result.articles_updated} article(s)`
      );

    } catch (err: unknown) {
      // ✅ Properly handle error type
      const errorMessage = err instanceof Error ? err.message : String(err);
      console.error('Sale error:', errorMessage);
      alert(`❌ Erreur: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  }

  // =========================================================
  // GENERATE PDF
  // =========================================================
  async function generateQuotationPDF() {
    if (cart.length === 0) {
      alert('Panier vide');
      return;
    }

    try {
      setLoading(true);

      const response = await fetchWithTimeout(
        `${API_URL}/api/devis/pdf`,
        {
          method: 'POST',
          body: JSON.stringify({
            client: 'Client Standard',
            articles: cart,
          }),
        }
      );

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `devis_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (err: unknown) {
      // ✅ Properly handle error type
      const errorMessage = err instanceof Error ? err.message : String(err);
      console.error('PDF error:', errorMessage);
      alert(`❌ Erreur génération PDF: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  }

  // =========================================================
  // RENDER
  // =========================================================
  return (
    <div className="min-h-screen bg-[#07111f] text-white">

      <ERPHeader
        search={search}
        setSearch={setSearch}
        loading={loading}
        cartCount={cart.length}
        onRefresh={() => loadData({ preservePage: true })}
      />

      <main className="max-w-[1800px] mx-auto p-6 space-y-6">

        <RealtimeStatus connected={connected} />

        <DashboardKPIs stats={stats} />

        <ProductFilters
          search={search}
          setSearch={setSearch}
          category={category}
          setCategory={setCategory}
          editor={publisher}
          setEditor={setPublisher}
          categories={categories}
          editors={publishers}
        />

        {loading && <div className="text-center">Chargement...</div>}

        {!loading && products.length === 0 && !apiError && (
          <div className="text-center text-gray-400">
            Aucun produit trouvé
          </div>
        )}

        {!loading && products.length > 0 && (
          <>
            <ProductGrid
              products={products}
              onView={setSelectedProduct}
              onAdd={addToCart}
            />

            <Pagination
              page={page}
              pages={pages}
              onPageChange={(newPage) => loadData({ page: newPage })}
            />
          </>
        )}

        <POSPanel
          total={cartTotal}
          onCheckout={validateSale}
          loading={loading}
        />

        <CartPanel
          cart={cart}
          total={cartTotal}
          increaseQuantity={increaseQuantity}
          decreaseQuantity={decreaseQuantity}
          removeFromCart={removeFromCart}
          clearCart={clearCart}
          generateQuotationPDF={generateQuotationPDF}
          loading={loading}
        />

        <ProductModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
          onAddToCart={addToCart}
        />

        {apiError && (
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 text-red-200">
            ⚠️ {apiError}
          </div>
        )}

      </main>
    </div>
  );
}