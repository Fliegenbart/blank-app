"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { Header } from "@/components/layout/header";
import { BrandNav } from "@/components/layout/brand-nav";
import * as api from "@/lib/api";
import type { Brand, BrandRole } from "@/types";

interface BrandContextValue {
  brand: Brand | null;
  userRole: BrandRole | null;
  refetch: () => void;
}

import { createContext, useContext, ReactNode } from "react";

export const BrandContext = createContext<BrandContextValue>({
  brand: null,
  userRole: null,
  refetch: () => {},
});

export function useBrand() {
  return useContext(BrandContext);
}

export default function BrandLayout({ children }: { children: ReactNode }) {
  const { user, token, isLoading: authLoading } = useAuth();
  const params = useParams();
  const router = useRouter();
  const brandId = params.brandId as string;

  const [brand, setBrand] = useState<Brand | null>(null);
  const [userRole, setUserRole] = useState<BrandRole | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchBrand = async () => {
    if (!token || !brandId) return;

    try {
      const data = await api.getBrand(token, brandId);
      setBrand(data);

      // Find user's role
      if (data.members && user) {
        const membership = data.members.find((m) => m.user_id === user.id);
        setUserRole(membership?.role || null);
      }
    } catch (err) {
      console.error("Failed to load brand", err);
      router.push("/brands");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/login");
      return;
    }

    fetchBrand();
  }, [token, brandId, authLoading, user]);

  if (authLoading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <BrandContext.Provider value={{ brand, userRole, refetch: fetchBrand }}>
      <div className="min-h-screen flex flex-col">
        <Header />
        <BrandNav />
        <main className="flex-1 container py-6">{children}</main>
      </div>
    </BrandContext.Provider>
  );
}
