"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Check, ChevronsUpDown, PlusCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/use-auth";
import * as api from "@/lib/api";
import type { Brand } from "@/types";

interface BrandSwitcherProps {
  className?: string;
}

export function BrandSwitcher({ className }: BrandSwitcherProps) {
  const { token } = useAuth();
  const router = useRouter();
  const params = useParams();
  const currentBrandId = params.brandId as string | undefined;

  const [brands, setBrands] = useState<Brand[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);

  useEffect(() => {
    if (!token) return;

    api
      .getBrands(token)
      .then((data) => {
        setBrands(data);
        if (currentBrandId) {
          const current = data.find((b) => b.id === currentBrandId);
          setSelectedBrand(current || null);
        }
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [token, currentBrandId]);

  const handleSelect = (brand: Brand) => {
    setSelectedBrand(brand);
    router.push(`/brands/${brand.id}/overview`);
  };

  const handleCreateNew = () => {
    router.push("/brands?new=true");
  };

  if (isLoading) {
    return (
      <Button variant="outline" className={cn("w-[200px] justify-start", className)} disabled>
        Loading...
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          className={cn("w-[200px] justify-between", className)}
        >
          {selectedBrand ? selectedBrand.name : "Select brand..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[200px]">
        <DropdownMenuLabel>Brands</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {brands.map((brand) => (
          <DropdownMenuItem
            key={brand.id}
            onClick={() => handleSelect(brand)}
            className="cursor-pointer"
          >
            <Check
              className={cn(
                "mr-2 h-4 w-4",
                selectedBrand?.id === brand.id ? "opacity-100" : "opacity-0"
              )}
            />
            {brand.name}
          </DropdownMenuItem>
        ))}
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleCreateNew} className="cursor-pointer">
          <PlusCircle className="mr-2 h-4 w-4" />
          Create new brand
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
