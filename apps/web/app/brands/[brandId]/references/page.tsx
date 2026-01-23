"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Plus, Link2, Loader2, Trash2, RefreshCw, ExternalLink, CheckCircle, XCircle, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useBrand } from "../layout";
import { api } from "@/lib/api";
import { Reference } from "@/types";

export default function ReferencesPage() {
  const { brand, userRole } = useBrand();
  const router = useRouter();
  const [references, setReferences] = useState<Reference[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [urls, setUrls] = useState("");

  const canEdit = userRole === "owner" || userRole === "editor";

  useEffect(() => {
    if (brand) {
      loadReferences();
    }
  }, [brand]);

  const loadReferences = async () => {
    if (!brand) return;
    try {
      const data = await api.get<Reference[]>(`/brands/${brand.id}/references`);
      setReferences(data);
    } catch (error) {
      console.error("Failed to load references:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!brand || !name || !urls) return;

    setIsCreating(true);
    try {
      const urlList = urls
        .split("\n")
        .map((u) => u.trim())
        .filter((u) => u.length > 0);

      await api.post(`/brands/${brand.id}/references`, {
        name,
        description: description || null,
        urls: urlList,
      });

      setIsDialogOpen(false);
      setName("");
      setDescription("");
      setUrls("");
      loadReferences();
    } catch (error) {
      console.error("Failed to create reference:", error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!brand) return;
    try {
      await api.delete(`/brands/${brand.id}/references/${id}`);
      loadReferences();
    } catch (error) {
      console.error("Failed to delete reference:", error);
    } finally {
      setDeleteId(null);
    }
  };

  const handleRescrape = async (id: string) => {
    if (!brand) return;
    try {
      await api.post(`/brands/${brand.id}/references/${id}/rescrape`);
      loadReferences();
    } catch (error) {
      console.error("Failed to rescrape reference:", error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "scraping":
      case "analyzing":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      completed: "default",
      failed: "destructive",
      scraping: "secondary",
      analyzing: "secondary",
      pending: "outline",
    };
    return (
      <Badge variant={variants[status] || "outline"}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  if (!brand) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Link2 className="h-8 w-8" />
            Reference Websites
          </h1>
          <p className="text-muted-foreground">
            Add websites to use as structure templates for content generation
          </p>
        </div>

        {canEdit && (
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Reference
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Reference Website</DialogTitle>
                <DialogDescription>
                  Enter URLs of websites to analyze for structure and content patterns.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., 2024 Summer Event"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description (optional)</Label>
                  <Input
                    id="description"
                    placeholder="Brief description of this reference"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="urls">URLs (one per line)</Label>
                  <Textarea
                    id="urls"
                    placeholder="https://example.com/event-page&#10;https://example.com/registration"
                    value={urls}
                    onChange={(e) => setUrls(e.target.value)}
                    rows={5}
                  />
                  <p className="text-sm text-muted-foreground">
                    Maximum 10 URLs per reference
                  </p>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreate} disabled={isCreating || !name || !urls}>
                  {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Create & Analyze
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : references.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Link2 className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No references yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Add reference websites to use as templates for content generation.
              <br />
              Great for recurring events or campaigns.
            </p>
            {canEdit && (
              <Button onClick={() => setIsDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Your First Reference
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {references.map((ref) => (
            <Card key={ref.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(ref.status)}
                    <div>
                      <CardTitle className="text-lg">{ref.name}</CardTitle>
                      {ref.description && (
                        <CardDescription>{ref.description}</CardDescription>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(ref.status)}
                    {canEdit && (
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRescrape(ref.id)}
                          disabled={ref.status === "scraping" || ref.status === "analyzing"}
                        >
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setDeleteId(ref.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">
                      URLs ({ref.urls.length})
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {ref.urls.map((url, i) => (
                        <a
                          key={i}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
                        >
                          <ExternalLink className="h-3 w-3" />
                          {new URL(url).hostname}
                        </a>
                      ))}
                    </div>
                  </div>

                  {ref.status === "completed" && (
                    <div className="flex gap-6 text-sm">
                      <div>
                        <span className="text-muted-foreground">Pages: </span>
                        <span className="font-medium">{ref.page_count || 0}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Words: </span>
                        <span className="font-medium">
                          {ref.total_word_count?.toLocaleString() || 0}
                        </span>
                      </div>
                    </div>
                  )}

                  {ref.status === "failed" && ref.error_message && (
                    <p className="text-sm text-destructive">{ref.error_message}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Reference?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this reference and its analyzed data.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteId && handleDelete(deleteId)}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
