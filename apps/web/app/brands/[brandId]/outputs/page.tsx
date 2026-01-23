"use client";

import { useEffect, useState } from "react";
import { FileOutput, Download, Globe, Mail, Loader2, Trash2, Eye } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useBrand } from "../layout";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import * as api from "@/lib/api";
import type { Output } from "@/types";
import { formatDate, formatBytes } from "@/lib/utils";

export default function OutputsPage() {
  const { brand, userRole } = useBrand();
  const { token } = useAuth();
  const { toast } = useToast();

  const [outputs, setOutputs] = useState<Output[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteOutputId, setDeleteOutputId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [previewOutput, setPreviewOutput] = useState<Output | null>(null);
  const [previewContent, setPreviewContent] = useState<string>("");
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);

  const canEdit = userRole === "owner" || userRole === "editor";

  useEffect(() => {
    if (!token || !brand) return;

    api
      .getOutputs(token, brand.id)
      .then(setOutputs)
      .catch((err) => {
        toast({
          title: "Error loading outputs",
          description: err instanceof Error ? err.message : "Unknown error",
          variant: "destructive",
        });
      })
      .finally(() => setIsLoading(false));
  }, [token, brand, toast]);

  const handleDownload = async (output: Output) => {
    if (!token || !brand) return;

    try {
      const blob = await api.downloadOutput(token, brand.id, output.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = output.filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast({
        title: "Download failed",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const handlePreview = async (output: Output) => {
    if (!token || !brand) return;

    // Only preview HTML files
    if (!output.content_type.includes("html") && !output.content_type.includes("text")) {
      toast({
        title: "Preview not available",
        description: "Preview is only available for HTML and text files",
      });
      return;
    }

    setPreviewOutput(output);
    setIsLoadingPreview(true);

    try {
      const blob = await api.downloadOutput(token, brand.id, output.id);
      const text = await blob.text();
      setPreviewContent(text);
    } catch (err) {
      toast({
        title: "Preview failed",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
      setPreviewOutput(null);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const handleDelete = async () => {
    if (!token || !brand || !deleteOutputId) return;

    setIsDeleting(true);
    try {
      await api.deleteOutput(token, brand.id, deleteOutputId);
      setOutputs((prev) => prev.filter((o) => o.id !== deleteOutputId));
      toast({ title: "Output deleted" });
    } catch (err) {
      toast({
        title: "Failed to delete output",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
      setDeleteOutputId(null);
    }
  };

  const getOutputIcon = (outputType: string) => {
    switch (outputType) {
      case "website":
        return <Globe className="h-4 w-4" />;
      case "newsletter":
        return <Mail className="h-4 w-4" />;
      default:
        return <FileOutput className="h-4 w-4" />;
    }
  };

  const getOutputBadgeVariant = (outputType: string) => {
    switch (outputType) {
      case "website":
        return "default";
      case "newsletter":
        return "secondary";
      default:
        return "outline";
    }
  };

  if (!brand) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Generated Outputs</h1>
        <p className="text-muted-foreground">
          Download and manage your generated content
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Outputs</CardTitle>
          <CardDescription>
            {outputs.length} output{outputs.length !== 1 ? "s" : ""} generated
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : outputs.length === 0 ? (
            <div className="text-center py-8">
              <FileOutput className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                No outputs yet. Generate content from your brand profile.
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Filename</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Profile</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {outputs.map((output) => (
                  <TableRow key={output.id}>
                    <TableCell>
                      <Badge variant={getOutputBadgeVariant(output.output_type)}>
                        <span className="flex items-center gap-1">
                          {getOutputIcon(output.output_type)}
                          {output.output_type}
                        </span>
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">{output.filename}</TableCell>
                    <TableCell>{formatBytes(output.file_size)}</TableCell>
                    <TableCell>v{output.profile_version}</TableCell>
                    <TableCell>{formatDate(output.created_at)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {(output.content_type.includes("html") ||
                          output.content_type.includes("text")) && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handlePreview(output)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(output)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        {canEdit && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => setDeleteOutputId(output.id)}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteOutputId} onOpenChange={() => setDeleteOutputId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Output</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this output? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} disabled={isDeleting}>
              {isDeleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Preview Dialog */}
      <Dialog open={!!previewOutput} onOpenChange={() => setPreviewOutput(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-auto">
          <DialogHeader>
            <DialogTitle>Preview: {previewOutput?.filename}</DialogTitle>
          </DialogHeader>
          {isLoadingPreview ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : previewOutput?.content_type.includes("html") ? (
            <div className="border rounded-lg overflow-hidden">
              <iframe
                srcDoc={previewContent}
                className="w-full h-[60vh]"
                title="Preview"
                sandbox="allow-same-origin"
              />
            </div>
          ) : (
            <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm max-h-[60vh]">
              {previewContent}
            </pre>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
