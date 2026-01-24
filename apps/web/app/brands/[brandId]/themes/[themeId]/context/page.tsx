"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import { useTheme } from "../theme-context";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Upload,
  FileText,
  File,
  Trash2,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
} from "lucide-react";
import type { ThemeDocument } from "@/types";

const documentTypeLabels: Record<string, string> = {
  brief: "Brief / Description",
  reference: "Reference Material",
  brand_guide: "Brand Guidelines",
  content: "Content / Copy",
  images: "Images / Assets",
  other: "Other",
};

const fileTypeIcons: Record<string, string> = {
  pdf: "📄",
  doc: "📝",
  docx: "📝",
  ppt: "📊",
  pptx: "📊",
  xls: "📈",
  xlsx: "📈",
  jpg: "🖼️",
  jpeg: "🖼️",
  png: "🖼️",
  gif: "🖼️",
  txt: "📃",
  md: "📃",
};

export default function ThemeContextPage() {
  const params = useParams();
  const brandId = params.brandId as string;
  const themeId = params.themeId as string;
  const { theme } = useTheme();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [documents, setDocuments] = useState<ThemeDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState("");
  const [uploadType, setUploadType] = useState("other");

  const loadDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.get<ThemeDocument[]>(`/brands/${brandId}/themes/${themeId}/documents`);
      setDocuments(data);
    } catch (err) {
      console.error("Error loading documents:", err);
    } finally {
      setLoading(false);
    }
  }, [brandId, themeId]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  useEffect(() => {
    const hasActive = documents.some((doc) =>
      ["queued", "processing"].includes(doc.status)
    );
    if (!hasActive) return;
    const interval = setInterval(loadDocuments, 4000);
    return () => clearInterval(interval);
  }, [documents, loadDocuments]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadFile(file);
      setUploadName(file.name.replace(/\.[^/.]+$/, ""));
      setIsUploadOpen(true);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile || !uploadName.trim()) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("name", uploadName);
      formData.append("document_type", uploadType);

      const newDoc = await api.upload<ThemeDocument>(
        `/brands/${brandId}/themes/${themeId}/documents`,
        formData
      );
      setDocuments([newDoc, ...documents]);
      setIsUploadOpen(false);
      setUploadFile(null);
      setUploadName("");
      setUploadType("other");
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      console.error("Error uploading document:", err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;

    try {
      await api.delete(`/brands/${brandId}/themes/${themeId}/documents/${docId}`);
      setDocuments(documents.filter((d) => d.id !== docId));
    } catch (err) {
      console.error("Error deleting document:", err);
    }
  };

  const handleRetryExtract = async (docId: string) => {
    try {
      await api.post(`/brands/${brandId}/themes/${themeId}/documents/${docId}/extract`, {});
      await loadDocuments();
    } catch (err) {
      console.error("Error retrying extraction:", err);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!theme) return null;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Documents</h2>
          <p className="text-muted-foreground">
            Upload reference materials, briefs, and other context for this theme.
          </p>
        </div>
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.md,.jpg,.jpeg,.png,.gif"
          />
          <Button onClick={() => fileInputRef.current?.click()}>
            <Upload className="h-4 w-4 mr-2" />
            Upload Document
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : documents.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No documents yet</h3>
            <p className="text-muted-foreground text-center mb-4 max-w-md">
              Upload briefs, reference materials, or brand guidelines to provide context
              for asset generation.
            </p>
            <Button onClick={() => fileInputRef.current?.click()}>
              <Upload className="h-4 w-4 mr-2" />
              Upload Document
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {documents.map((doc) => (
            <Card key={doc.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">
                      {fileTypeIcons[doc.file_type] || "📄"}
                    </span>
                    <div>
                      <CardTitle className="text-base">{doc.name}</CardTitle>
                      <CardDescription className="text-xs">
                        {doc.original_filename}
                      </CardDescription>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive hover:text-destructive"
                    onClick={() => handleDelete(doc.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-4 text-muted-foreground">
                    <Badge variant="outline">
                      {documentTypeLabels[doc.document_type] || doc.document_type}
                    </Badge>
                    <span>{formatFileSize(doc.file_size)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    {doc.status === "uploaded" && (
                      <>
                        <CheckCircle className="h-3 w-3 text-green-600" />
                        <span className="text-xs">Uploaded</span>
                      </>
                    )}
                    {doc.status === "queued" && (
                      <>
                        <Clock className="h-3 w-3" />
                        <span className="text-xs">Queued</span>
                      </>
                    )}
                    {doc.status === "processing" && (
                      <>
                        <Loader2 className="h-3 w-3 animate-spin" />
                        <span className="text-xs">Processing</span>
                      </>
                    )}
                    {doc.status === "completed" && (
                      <>
                        <CheckCircle className="h-3 w-3 text-green-600" />
                        <span className="text-xs">Complete</span>
                      </>
                    )}
                    {doc.status === "failed" && (
                      <>
                        <AlertCircle className="h-3 w-3 text-destructive" />
                        <span className="text-xs">Failed</span>
                      </>
                    )}
                    {doc.status === "failed" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 px-2 text-xs"
                        onClick={() => handleRetryExtract(doc.id)}
                      >
                        <RefreshCw className="h-3 w-3 mr-1" />
                        Retry
                      </Button>
                    )}
                  </div>
                </div>
                {doc.extracted_text && (
                  <p className="text-sm text-muted-foreground mt-3 line-clamp-3">
                    {doc.extracted_text}
                  </p>
                )}
                {!doc.extracted_text && doc.summary && (
                  <p className="text-sm text-muted-foreground mt-3 line-clamp-2">
                    {typeof doc.summary === "string" ? doc.summary : JSON.stringify(doc.summary)}
                  </p>
                )}
                <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {new Date(doc.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Upload Dialog */}
      <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
            <DialogDescription>
              Add a reference document for this theme.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {uploadFile && (
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <File className="h-8 w-8 text-muted-foreground" />
                <div>
                  <p className="font-medium">{uploadFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(uploadFile.size)}
                  </p>
                </div>
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="doc-name">Document Name</Label>
              <Input
                id="doc-name"
                value={uploadName}
                onChange={(e) => setUploadName(e.target.value)}
                placeholder="Enter a name for this document"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="doc-type">Document Type</Label>
              <Select value={uploadType} onValueChange={setUploadType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(documentTypeLabels).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsUploadOpen(false);
                setUploadFile(null);
                setUploadName("");
                if (fileInputRef.current) {
                  fileInputRef.current.value = "";
                }
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleUpload} disabled={uploading || !uploadName.trim()}>
              {uploading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
