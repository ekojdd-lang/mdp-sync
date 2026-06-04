"use client";

import { useMemo, useState, useCallback } from "react";

import type {
  Product,
  CartItem,
} from "../types/product";

/**
 * ✅ Cart hook avec:
 * - gencod comme clé unique (string)
 * - useMemo pour calculations
 * - useCallback pour callbacks
 * - Proper TypeScript types
 */
export function useCart() {
  const [cart, setCart] = useState<CartItem[]>([]);

  // ===== ADD TO CART =====
  const addToCart = useCallback((product: Product) => {
    setCart((prev) => {
      const existing = prev.find(
        (item) => item.gencod === product.gencod
      );

      if (existing) {
        return prev.map((item) =>
          item.gencod === product.gencod
            ? {
                ...item,
                quantity: item.quantity + 1,
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
  }, []);

  // ===== INCREASE QUANTITY =====
  const increaseQuantity = useCallback((gencod: string) => {
    setCart((prev) =>
      prev.map((item) =>
        item.gencod === gencod
          ? {
              ...item,
              quantity: item.quantity + 1,
            }
          : item
      )
    );
  }, []);

  // ===== DECREASE QUANTITY =====
  const decreaseQuantity = useCallback((gencod: string) => {
    setCart((prev) =>
      prev
        .map((item) =>
          item.gencod === gencod
            ? {
                ...item,
                quantity: Math.max(0, item.quantity - 1),
              }
            : item
        )
        .filter((item) => item.quantity > 0)
    );
  }, []);

  // ===== REMOVE FROM CART =====
  const removeFromCart = useCallback((gencod: string) => {
    setCart((prev) =>
      prev.filter((item) => item.gencod !== gencod)
    );
  }, []);

  // ===== CLEAR CART =====
  const clearCart = useCallback(() => {
    setCart([]);
  }, []);

  // ===== TOTAL PRICE (memoized) =====
  const total = useMemo(
    () =>
      cart.reduce(
        (acc, item) =>
          acc + item.prix * item.quantity,
        0
      ),
    [cart]
  );

  // ===== TOTAL ITEMS (memoized) =====
  const totalItems = useMemo(
    () =>
      cart.reduce(
        (acc, item) =>
          acc + item.quantity,
        0
      ),
    [cart]
  );

  return {
    cart,
    total,
    totalItems,

    addToCart,
    increaseQuantity,
    decreaseQuantity,
    removeFromCart,
    clearCart,
  };
}
