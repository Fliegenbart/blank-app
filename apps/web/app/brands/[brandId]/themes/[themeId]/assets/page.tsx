"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { useTheme } from "../theme-context";
import { api, getApiBaseUrl } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Download,
  Eye,
  MoreVertical,
  RefreshCw,
  Image,
  Globe,
  Mail,
  FileText,
  BookOpen,
  Film,
  Share2,
  Presentation,
  CheckCircle,
  AlertCircle,
  Loader2,
  Clock,
  ExternalLink,
  Printer,
  FileDown,
  Figma,
} from "lucide-react";
import type { ThemeAsset, AssetType, AssetStatus } from "@/types";

// Asset types that support print PDF export
const PRINTABLE_ASSET_TYPES = ["flyer", "brochure", "newsletter"];

const assetTypeIcons: Record<AssetType, React.ReactNode> = {
  website: <Globe className="h-5 w-5" />,
  landing_page: <Globe className="h-5 w-5" />,
  newsletter: <Mail className="h-5 w-5" />,
  flyer: <FileText className="h-5 w-5" />,
  brochure: <BookOpen className="h-5 w-5" />,
  teaser_script: <Film className="h-5 w-5" />,
  social_media: <Share2 className="h-5 w-5" />,
  presentation: <Presentation className="h-5 w-5" />,
  banner_ads: <Image className="h-5 w-5" />,
};

const assetTypeLabels: Record<AssetType, string> = {
  website: "Website",
  landing_page: "Landing Page",
  newsletter: "Newsletter",
  flyer: "Flyer",
  brochure: "Brochure",
  teaser_script: "Teaser Script",
  social_media: "Social Media Kit",
  presentation: "Presentation",
  banner_ads: "Banner Ads",
};

const statusColors: Record<AssetStatus, string> = {
  pending: "bg-gray-100 text-gray-800",
  generating: "bg-yellow-100 text-yellow-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

const statusIcons: Record<AssetStatus, React.ReactNode> = {
  pending: <Clock className="h-3 w-3" />,
  generating: <Loader2 className="h-3 w-3 animate-spin" />,
  completed: <CheckCircle className="h-3 w-3" />,
  failed: <AlertCircle className="h-3 w-3" />,
};

export default function ThemeAssetsPage() {
  const params = useParams();
  const brandId = params.brandId as string;
  const themeId = params.themeId as string;
  const { theme } = useTheme();

  const [assets, setAssets] = useState<ThemeAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [previewAsset, setPreviewAsset] = useState<ThemeAsset | null>(null);
  const [regenerating, setRegenerating] = useState<string | null>(null);
  const [exportingPrint, setExportingPrint] = useState<string | null>(null);
  const [figmaDialogAsset, setFigmaDialogAsset] = useState<ThemeAsset | null>(null);
  const [figmaToken, setFigmaToken] = useState("");
  const [figmaFileName, setFigmaFileName] = useState("");
  const [exportingFigma, setExportingFigma] = useState(false);
  const [downloadingAll, setDownloadingAll] = useState(false);

  const loadAssets = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.get<ThemeAsset[]>(`/brands/${brandId}/themes/${themeId}/assets`);
      setAssets(data);
    } catch (err) {
      console.error("Error loading assets:", err);
    } finally {
      setLoading(false);
    }
  }, [brandId, themeId]);

  useEffect(() => {
    loadAssets();
  }, [loadAssets]);

  // Poll for generating assets
  useEffect(() => {
    const generatingAssets = assets.filter(
      (a) => a.status === "pending" || a.status === "generating"
    );
    if (generatingAssets.length === 0) return;

    const interval = setInterval(loadAssets, 5000);
    return () => clearInterval(interval);
  }, [assets, loadAssets]);

  const handleDownload = async (asset: ThemeAsset) => {
    if (!asset.storage_path) return;

    try {
      // Get download URL from API
      const token = localStorage.getItem("brand_engine_token");
      const downloadUrl = `${getApiBaseUrl()}/brands/${brandId}/themes/${themeId}/assets/${asset.id}/download`;

      // Create a temporary link to trigger download
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.setAttribute("download", asset.name);
      // Add auth header via fetch and blob
      const response = await fetch(downloadUrl, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        link.href = url;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error("Error downloading asset:", err);
    }
  };

  const handleRegenerate = async (asset: ThemeAsset) => {
    try {
      setRegenerating(asset.id);
      await api.post(`/brands/${brandId}/themes/${themeId}/generate/regenerate/${asset.id}`, {});
      await loadAssets();
    } catch (err) {
      console.error("Error regenerating asset:", err);
    } finally {
      setRegenerating(null);
    }
  };

  const handleExportPrintPdf = async (asset: ThemeAsset) => {
    try {
      setExportingPrint(asset.id);
      await api.post(`/brands/${brandId}/themes/${themeId}/export/print/${asset.id}`, {
        format: "pdf",
        bleed_mm: 3,
        crop_marks: true,
        color_profile: "CMYK",
      });
      // The export creates a background job, so we poll for updates
      await loadAssets();
    } catch (err) {
      console.error("Error exporting print PDF:", err);
    } finally {
      setExportingPrint(null);
    }
  };

  const handleExportFigma = async () => {
    if (!figmaDialogAsset || !figmaToken) return;

    try {
      setExportingFigma(true);
      await api.post(`/brands/${brandId}/themes/${themeId}/export/figma/${figmaDialogAsset.id}`, {
        figma_access_token: figmaToken,
        file_name: figmaFileName || figmaDialogAsset.name,
      });
      setFigmaDialogAsset(null);
      setFigmaToken("");
      setFigmaFileName("");
      await loadAssets();
    } catch (err) {
      console.error("Error exporting to Figma:", err);
    } finally {
      setExportingFigma(false);
    }
  };

  const handleDownloadPrintPdf = async (asset: ThemeAsset) => {
    if (!asset.print_pdf_path) return;

    try {
      const token = localStorage.getItem("brand_engine_token");
      const response = await fetch(
        `${getApiBaseUrl()}/files/${asset.print_pdf_path}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `${asset.name}-print.pdf`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error("Error downloading print PDF:", err);
    }
  };

  const handleDownloadAll = async () => {
    try {
      setDownloadingAll(true);
      const token = localStorage.getItem("brand_engine_token");
      const response = await fetch(
        `${getApiBaseUrl()}/brands/${brandId}/themes/${themeId}/export/download-all`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `${theme?.slug || themeId}-assets.zip`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error("Error downloading all assets:", err);
    } finally {
      setDownloadingAll(false);
    }
  };

  const openFigmaDialog = (asset: ThemeAsset) => {
    setFigmaDialogAsset(asset);
    setFigmaFileName(asset.name);
  };

  const formatFileSize = (bytes: number | null): string => {
    if (!bytes) return "—";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!theme) return null;

  const completedAssets = assets.filter((a) => a.status === "completed");
  const pendingAssets = assets.filter((a) => a.status === "pending" || a.status === "generating");
  const failedAssets = assets.filter((a) => a.status === "failed");

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Generated Assets</h2>
          <p className="text-muted-foreground">
            {completedAssets.length} completed, {pendingAssets.length} in progress
            {failedAssets.length > 0 && `, ${failedAssets.length} failed`}
          </p>
        </div>
        {completedAssets.length > 0 && (
          <Button
            variant="outline"
            onClick={handleDownloadAll}
            disabled={downloadingAll}
          >
            {downloadingAll ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <FileDown className="h-4 w-4 mr-2" />
            )}
            {downloadingAll ? "Downloading..." : "Download All (ZIP)"}
          </Button>
        )}
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : assets.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Image className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No assets yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Go to the Generate tab to create assets for this theme.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {assets.map((asset) => (
            <Card key={asset.id} className="overflow-hidden">
              {/* Preview Area */}
              <div
                className="h-32 bg-muted flex items-center justify-center cursor-pointer hover:bg-muted/80 transition-colors"
                onClick={() => asset.status === "completed" && setPreviewAsset(asset)}
              >
                {asset.preview_path ? (
                  <img
                    src={`${getApiBaseUrl()}/files/${asset.preview_path}`}
                    alt={asset.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-muted-foreground">
                    {asset.status === "generating" || asset.status === "pending" ? (
                      <Loader2 className="h-8 w-8 animate-spin" />
                    ) : asset.status === "failed" ? (
                      <AlertCircle className="h-8 w-8 text-destructive" />
                    ) : (
                      assetTypeIcons[asset.asset_type as AssetType]
                    )}
                  </div>
                )}
              </div>

              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">
                      {assetTypeIcons[asset.asset_type as AssetType]}
                    </span>
                    <CardTitle className="text-base">
                      {assetTypeLabels[asset.asset_type as AssetType]}
                    </CardTitle>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {asset.status === "completed" && (
                        <>
                          <DropdownMenuItem onClick={() => setPreviewAsset(asset)}>
                            <Eye className="h-4 w-4 mr-2" />
                            Preview
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleDownload(asset)}>
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </DropdownMenuItem>
                          {asset.print_pdf_path && (
                            <DropdownMenuItem onClick={() => handleDownloadPrintPdf(asset)}>
                              <Printer className="h-4 w-4 mr-2" />
                              Download Print PDF
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuSeparator />
                          {/* Export Options */}
                          {PRINTABLE_ASSET_TYPES.includes(asset.asset_type) && !asset.print_pdf_path && (
                            <DropdownMenuItem
                              onClick={() => handleExportPrintPdf(asset)}
                              disabled={exportingPrint === asset.id}
                            >
                              {exportingPrint === asset.id ? (
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              ) : (
                                <Printer className="h-4 w-4 mr-2" />
                              )}
                              Export Print PDF
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem onClick={() => openFigmaDialog(asset)}>
                            <Figma className="h-4 w-4 mr-2" />
                            Export to Figma
                          </DropdownMenuItem>
                          {asset.figma_file_key && (
                            <DropdownMenuItem asChild>
                              <a
                                href={`https://www.figma.com/file/${asset.figma_file_key}`}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <ExternalLink className="h-4 w-4 mr-2" />
                                Open in Figma
                              </a>
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuSeparator />
                        </>
                      )}
                      <DropdownMenuItem
                        onClick={() => handleRegenerate(asset)}
                        disabled={regenerating === asset.id}
                      >
                        <RefreshCw
                          className={`h-4 w-4 mr-2 ${
                            regenerating === asset.id ? "animate-spin" : ""
                          }`}
                        />
                        Regenerate
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>

              <CardContent>
                <div className="flex items-center justify-between">
                  <Badge className={statusColors[asset.status as AssetStatus]}>
                    {statusIcons[asset.status as AssetStatus]}
                    <span className="ml-1 capitalize">{asset.status}</span>
                  </Badge>
                  {asset.file_size && (
                    <span className="text-xs text-muted-foreground">
                      {formatFileSize(asset.file_size)}
                    </span>
                  )}
                </div>

                {/* Export availability badges */}
                {asset.status === "completed" && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {asset.print_pdf_path && (
                      <Badge variant="secondary" className="text-xs">
                        <Printer className="h-3 w-3 mr-1" />
                        Print Ready
                      </Badge>
                    )}
                    {asset.figma_file_key && (
                      <Badge variant="secondary" className="text-xs">
                        <Figma className="h-3 w-3 mr-1" />
                        In Figma
                      </Badge>
                    )}
                  </div>
                )}

                {asset.error_message && (
                  <p className="text-xs text-destructive mt-2 line-clamp-2">
                    {asset.error_message}
                  </p>
                )}

                {asset.variants && Object.keys(asset.variants).length > 0 && (
                  <p className="text-xs text-muted-foreground mt-2">
                    {Object.keys(asset.variants).length} variants available
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Preview Dialog */}
      <Dialog open={!!previewAsset} onOpenChange={() => setPreviewAsset(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {previewAsset && assetTypeIcons[previewAsset.asset_type as AssetType]}
              {previewAsset?.name}
            </DialogTitle>
            <DialogDescription>
              Preview of {previewAsset && assetTypeLabels[previewAsset.asset_type as AssetType]}
            </DialogDescription>
          </DialogHeader>

          {previewAsset && (
            <div className="space-y-4">
              {/* Preview Content */}
              <div className="border rounded-lg overflow-hidden bg-white">
                {previewAsset.preview_path ? (
                  <img
                    src={`${getApiBaseUrl()}/files/${previewAsset.preview_path}`}
                    alt={previewAsset.name}
                    className="w-full"
                  />
                ) : (
                  <div className="h-96 flex items-center justify-center text-muted-foreground">
                    <p>Preview not available</p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  {previewAsset.file_size && (
                    <span>Size: {formatFileSize(previewAsset.file_size)}</span>
                  )}
                  {previewAsset.content_type && (
                    <span className="ml-4">Type: {previewAsset.content_type}</span>
                  )}
                </div>
                <div className="flex gap-2">
                  {previewAsset.print_pdf_path && (
                    <Button variant="outline" onClick={() => handleDownloadPrintPdf(previewAsset)}>
                      <Printer className="h-4 w-4 mr-2" />
                      Print PDF
                    </Button>
                  )}
                  <Button onClick={() => handleDownload(previewAsset)}>
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Figma Export Dialog */}
      <Dialog open={!!figmaDialogAsset} onOpenChange={() => setFigmaDialogAsset(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Figma className="h-5 w-5" />
              Export to Figma
            </DialogTitle>
            <DialogDescription>
              Export "{figmaDialogAsset?.name}" to your Figma account.
              You'll need a Figma personal access token.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="figma-token">Figma Access Token</Label>
              <Input
                id="figma-token"
                type="password"
                placeholder="figd_..."
                value={figmaToken}
                onChange={(e) => setFigmaToken(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Get your token from{" "}
                <a
                  href="https://www.figma.com/developers/api#access-tokens"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  Figma Settings → Personal access tokens
                </a>
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="figma-filename">File Name</Label>
              <Input
                id="figma-filename"
                placeholder="My Asset"
                value={figmaFileName}
                onChange={(e) => setFigmaFileName(e.target.value)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setFigmaDialogAsset(null)}>
              Cancel
            </Button>
            <Button onClick={handleExportFigma} disabled={!figmaToken || exportingFigma}>
              {exportingFigma ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Figma className="h-4 w-4 mr-2" />
                  Export
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
