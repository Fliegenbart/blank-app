"use client";

import { ReactNode, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import type { User } from "@/types";
import * as api from "@/lib/api";
import { AuthContext, type AuthContextType } from "@/hooks/use-auth";
import { Toaster } from "@/components/ui/toaster";

const TOKEN_KEY = "brand_engine_token";

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

function setStoredToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const storedToken = getStoredToken();
    if (storedToken) {
      setToken(storedToken);
      api
        .getCurrentUser(storedToken)
        .then((user) => {
          setUser(user);
        })
        .catch(() => {
          setStoredToken(null);
          setToken(null);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    const newToken = response.access_token;
    setStoredToken(newToken);
    setToken(newToken);
    const user = await api.getCurrentUser(newToken);
    setUser(user);
    router.push("/brands");
  };

  const register = async (email: string, password: string, fullName?: string) => {
    await api.register(email, password, fullName);
    await login(email, password);
  };

  const logout = () => {
    setStoredToken(null);
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
      <Toaster />
    </AuthProvider>
  );
}
