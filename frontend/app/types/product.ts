/**
 * ✅ Product type avec tous les champs
 * alignés avec le backend FastAPI
 */
export type Product = {
  id?: number;

  // ===== CODES (clé unique) =====
  gencod: string;
  isbn?: string;
  ean?: string;
  code_article?: string;

  // ===== TITLES =====
  titre: string;
  sous_titre?: string;

  // ===== METADATA =====
  auteurs?: string;
  editeur?: string;
  collection?: string;

  // ===== PUBLICATION =====
  langue?: string;
  date_parution?: string;

  // ===== PRICING & STOCK =====
  prix: number;
  stock?: number;

  // ===== AVAILABILITY =====
  disponibilite?: string;

  // ===== PHYSICAL PROPS =====
  nombre_pages?: number;
  largeur?: string;
  hauteur?: string;
  poids?: string;

  // ===== MEDIA =====
  image_url?: string;

  // ===== CONTENT =====
  presentation?: string;

  // ===== CLASSIFICATION =====
  type_produit?: string;

  // ===== TIMESTAMPS =====
  date_sync?: string;
  created_at?: string;
  updated_at?: string;
};

/**
 * ✅ Cart item extends Product with quantity
 */
export type CartItem = Product & {
  quantity: number;
};

/**
 * ✅ Dashboard statistics
 * Aligné avec /api/stats du backend
 */
export type Stats = {
  total_articles: number;
  available_articles: number;
  inventory_value: number;

  total_stock?: number;
  average_price?: number;

  ventes_jour?: number;
  ventes_mois?: number;

  chiffre_affaire_jour?: number;
};

/**
 * ✅ API response for articles list
 * Aligné avec GET /api/articles
 */
export type ArticlesResponse = {
  items: Product[];
  page: number;
  pages: number;
  total: number;
  available?: number;
};

/**
 * ✅ API response for filters
 * Aligné avec GET /api/filters
 */
export type FiltersResponse = {
  type_produits: string[];
  publishers: string[];
};

/**
 * ✅ API response for stats
 * Aligné avec GET /api/stats
 */
export type StatsResponse = {
  total_articles: number;
  available_articles: number;
  inventory_value: number;
  total_stock: number;
  average_price: number;
};
