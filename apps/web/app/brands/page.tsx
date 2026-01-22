"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Plus, Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Header } from "@/components/layout/header";
import { useToast } from "@/hooks/use-toast";
import * as api from "@/lib/api";
import type { Brand } from "@/types";
import { formatDate } from "@/lib/utils";

export default function BrandsPage() {
  const { user, token, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();

  const [brands, setBrands] = useState<Brand[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const [newBrandName, setNewBrandName] = useState("");
  const [newBrandSlug, setNewBrandSlug] = useState("");
  const [newBrandDescription, setNewBrandDescription] = useState("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (searchParams.get("new") === "true") {
      setShowCreateDialog(true);
    }
  }, [searchParams]);

  useEffect(() => {
    if (token) {
      api
        .getBrands(token)
        .then(setBrands)
        .catch((err) => {
          toast({
            title: "Error loading brands",
            description: err.message,
            variant: "destructive",
          });
        })
        .finally(() => setIsLoading(false));
    }
  }, [token, toast]);

  const handleNameChange = (name: string) => {
    setNewBrandName(name);
    // Auto-generate slug
    const slug = name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
    setNewBrandSlug(slug);
  };

  const handleCreateBrand = async () => {
    if (!token || !newBrandName || !newBrandSlug) return;

    setIsCreating(true);
    try {
      const brand = await api.createBrand(token, {
        name: newBrandName,
        slug: newBrandSlug,
        description: newBrandDescription || undefined,
      });
      setBrands([...brands, brand]);
      setShowCreateDialog(false);
      setNewBrandName("");
      setNewBrandSlug("");
      setNewBrandDescription("");
      toast({ title: "Brand created", description: `${brand.name} is ready` });
      router.push(`/brands/${brand.id}/overview`);
    } catch (err) {
      toast({
        title: "Failed to create brand",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">Brands</h1>
            <p className="text-muted-foreground">
              Manage your brand identities
            </p>
          </div>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Brand
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create new brand</DialogTitle>
                <DialogDescription>
                  Add a new brand to analyze and generate content for.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={newBrandName}
                    onChange={(e) => handleNameChange(e.target.value)}
                    placeholder="My Brand"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="slug">Slug</Label>
                  <Input
                    id="slug"
                    value={newBrandSlug}
                    onChange={(e) => setNewBrandSlug(e.target.value)}
                    placeholder="my-brand"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description (optional)</Label>
                  <Textarea
                    id="description"
                    value={newBrandDescription}
                    onChange={(e) => setNewBrandDescription(e.target.value)}
                    placeholder="Brief description of the brand..."
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setShowCreateDialog(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateBrand}
                  disabled={!newBrandName || !newBrandSlug || isCreating}
                >
                  {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Create
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : brands.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <p className="text-muted-foreground mb-4">
                No brands yet. Create your first brand to get started.
              </p>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create Brand
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {brands.map((brand) => (
              <Card
                key={brand.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => router.push(`/brands/${brand.id}/overview`)}
              >
                <CardHeader>
                  <CardTitle>{brand.name}</CardTitle>
                  <CardDescription>
                    {brand.description || `/${brand.slug}`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">
                    Created {formatDate(brand.created_at)}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
