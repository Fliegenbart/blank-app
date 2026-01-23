"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Theme } from "@/types";

interface ThemeContextType {
  theme: Theme | null;
  loading: boolean;
  error: string | null;
  refreshTheme: () => Promise<void>;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: null,
  loading: true,
  error: null,
  refreshTheme: async () => {},
});

export const useTheme = () => useContext(ThemeContext);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const params = useParams();
  const brandId = params.brandId as string;
  const themeId = params.themeId as string;

  const [theme, setTheme] = useState<Theme | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTheme = async () => {
    try {
      setLoading(true);
      const data = await api.get<Theme>(`/brands/${brandId}/themes/${themeId}`);
      setTheme(data);
      setError(null);
    } catch (err) {
      console.error("Error loading theme:", err);
      setError("Failed to load theme");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTheme();
  }, [brandId, themeId]);

  return (
    <ThemeContext.Provider value={{ theme, loading, error, refreshTheme: loadTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
