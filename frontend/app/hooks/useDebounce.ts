"use client";

import {
  useEffect,
  useState,
} from "react";

/**
 * ✅ Debounce hook avec:
 * - TypeScript generics
 * - Cleanup on unmount
 * - Configurable delay
 */
export function useDebounce<T>(
  value: T,
  delay = 300
): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // ✅ Set timer
    const timer = window.setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // ✅ Cleanup on change or unmount
    return () => window.clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}