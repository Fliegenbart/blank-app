"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Layers, FileText, Image, Sparkles, MoreVertical, Pencil, Trash2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { ThemeListItem, ThemeCreateRequest, ThemeStatus } from "@/types";

const statusColors: Record<ThemeStatus, string> = {
  draft: "bg-gray-100 text-gray-800",
  ready: "bg-blue-100 text-blue-800",
  generating: "bg-yellow-100 text-yellow-800",
  completed: "bg-green-100 text-green-800",
};

const statusLabels: Record<ThemeStatus, string> = {
  draft: "Draft",
  ready: "Ready",
  generating: "Generating...",
  completed: "Completed",
};

export default function ThemesPage() {
  const params = useParams();
  const router = useRouter();
  const brandId = params.brandId as string;

  const [themes, setThemes] = useState<ThemeListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newTheme, setNewTheme] = useState<ThemeCreateRequest>({
    name: "",
    description: "",
  });

  const loadThemes = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.get<ThemeListItem[]>(`/brands/${brandId}/themes`);
      setThemes(data);
      setError(null);
    } catch (err) {
      console.error("Error loading themes:", err);
      setError("Failed to load themes");
    } finally {
      setLoading(false);
    }
  }, [brandId]);

  useEffect(() => {
    loadThemes();
  }, [loadThemes]);

  const handleCreateTheme = async () => {
    if (!newTheme.name.trim()) return;

    try {
      setCreating(true);
      const created = await api.post<ThemeListItem>(`/brands/${brandId}/themes`, newTheme);
      setThemes([created, ...themes]);
      setIsCreateOpen(false);
      setNewTheme({ name: "", description: "" });
      // Navigate to the new theme
      router.push(`/brands/${brandId}/themes/${created.id}`);
    } catch (err) {
      console.error("Error creating theme:", err);
      setError("Failed to create theme");
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteTheme = async (themeId: string) => {
    if (!confirm("Are you sure you want to delete this theme? This will also delete all associated documents and assets.")) {
      return;
    }

    try {
      await api.delete(`/brands/${brandId}/themes/${themeId}`);
      setThemes(themes.filter((t) => t.id !== themeId));
    } catch (err) {
      console.error("Error deleting theme:", err);
      setError("Failed to delete theme");
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 bg-muted rounded" />
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-muted rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Themes</h1>
          <p className="text-muted-foreground">
            Create campaign-specific themes and generate all assets at once.
          </p>
        </div>
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Theme
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Theme</DialogTitle>
              <DialogDescription>
                A theme groups all assets for a specific campaign or event.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  placeholder="e.g. NeX26, eTruckathon, Summer Campaign"
                  value={newTheme.name}
                  onChange={(e) => setNewTheme({ ...newTheme, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Brief description of this campaign or event..."
                  value={newTheme.description || ""}
                  onChange={(e) => setNewTheme({ ...newTheme, description: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateTheme} disabled={creating || !newTheme.name.trim()}>
                {creating ? "Creating..." : "Create Theme"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {themes.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Layers className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No themes yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Create your first theme to start generating campaign assets.
            </p>
            <Button onClick={() => setIsCreateOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Theme
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {themes.map((theme) => (
            <Card
              key={theme.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push(`/brands/${brandId}/themes/${theme.id}`)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{theme.name}</CardTitle>
                    {theme.description && (
                      <CardDescription className="line-clamp-2 mt-1">
                        {theme.description}
                      </CardDescription>
                    )}
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/brands/${brandId}/themes/${theme.id}`);
                        }}
                      >
                        <Pencil className="h-4 w-4 mr-2" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteTheme(theme.id);
                        }}
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <FileText className="h-4 w-4" />
                      {theme.document_count} docs
                    </span>
                    <span className="flex items-center gap-1">
                      <Image className="h-4 w-4" />
                      {theme.asset_count} assets
                    </span>
                  </div>
                  <Badge className={statusColors[theme.status]}>
                    {statusLabels[theme.status]}
                  </Badge>
                </div>
                {theme.status === "generating" && (
                  <div className="mt-3 flex items-center gap-2 text-sm text-yellow-700">
                    <Sparkles className="h-4 w-4 animate-pulse" />
                    Generating assets...
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
