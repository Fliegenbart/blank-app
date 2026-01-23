"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { useTheme } from "../theme-context";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sparkles,
  Globe,
  Mail,
  FileText,
  BookOpen,
  Film,
  Share2,
  Presentation,
  Image,
  Loader2,
  CheckCircle,
  AlertCircle,
  Clock,
} from "lucide-react";
import type { AssetType, ThemeJob, ThemeAsset, BrandProfile } from "@/types";

interface AssetOption {
  type: AssetType;
  label: string;
  description: string;
  icon: React.ReactNode;
}

const assetOptions: AssetOption[] = [
  {
    type: "website",
    label: "Website",
    description: "Full responsive website with multiple pages",
    icon: <Globe className="h-5 w-5" />,
  },
  {
    type: "landing_page",
    label: "Landing Page",
    description: "Single-page campaign landing page",
    icon: <Globe className="h-5 w-5" />,
  },
  {
    type: "newsletter",
    label: "Newsletter",
    description: "Email newsletter in HTML/MJML format",
    icon: <Mail className="h-5 w-5" />,
  },
  {
    type: "flyer",
    label: "Flyer",
    description: "Print-ready A4 flyer with bleed",
    icon: <FileText className="h-5 w-5" />,
  },
  {
    type: "brochure",
    label: "Brochure",
    description: "Multi-page print brochure",
    icon: <BookOpen className="h-5 w-5" />,
  },
  {
    type: "teaser_script",
    label: "Teaser Script",
    description: "Video teaser script in markdown/PDF",
    icon: <Film className="h-5 w-5" />,
  },
  {
    type: "social_media",
    label: "Social Media Kit",
    description: "Posts for multiple platforms",
    icon: <Share2 className="h-5 w-5" />,
  },
  {
    type: "presentation",
    label: "Presentation",
    description: "PowerPoint/PPTX presentation",
    icon: <Presentation className="h-5 w-5" />,
  },
  {
    type: "banner_ads",
    label: "Banner Ads",
    description: "Digital ads in standard sizes",
    icon: <Image className="h-5 w-5" />,
  },
];

export default function ThemeGeneratePage() {
  const params = useParams();
  const router = useRouter();
  const brandId = params.brandId as string;
  const themeId = params.themeId as string;
  const { theme, refreshTheme } = useTheme();

  const [selectedAssets, setSelectedAssets] = useState<AssetType[]>([]);
  const [profiles, setProfiles] = useState<BrandProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>("latest");
  const [generating, setGenerating] = useState(false);
  const [activeJob, setActiveJob] = useState<ThemeJob | null>(null);
  const [existingAssets, setExistingAssets] = useState<ThemeAsset[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Load profiles and existing assets
  useEffect(() => {
    const loadData = async () => {
      try {
        const [profilesData, assetsData, jobsData] = await Promise.all([
          api.get<BrandProfile[]>(`/brands/${brandId}/profiles`),
          api.get<ThemeAsset[]>(`/brands/${brandId}/themes/${themeId}/assets`),
          api.get<ThemeJob[]>(`/brands/${brandId}/themes/${themeId}/jobs`),
        ]);
        setProfiles(profilesData);
        setExistingAssets(assetsData);

        // Check for active job
        const active = jobsData.find(
          (j) => j.status === "pending" || j.status === "queued" || j.status === "running"
        );
        if (active) {
          setActiveJob(active);
        }
      } catch (err) {
        console.error("Error loading data:", err);
      }
    };
    loadData();
  }, [brandId, themeId]);

  // Poll for active job status
  useEffect(() => {
    if (!activeJob) return;

    const interval = setInterval(async () => {
      try {
        const jobsData = await api.get<ThemeJob[]>(`/brands/${brandId}/themes/${themeId}/jobs`);
        const job = jobsData.find((j) => j.id === activeJob.id);
        if (job) {
          setActiveJob(job);
          if (job.status === "completed" || job.status === "failed") {
            // Refresh assets
            const assetsData = await api.get<ThemeAsset[]>(`/brands/${brandId}/themes/${themeId}/assets`);
            setExistingAssets(assetsData);
            refreshTheme();
            if (job.status === "completed") {
              setActiveJob(null);
            }
          }
        }
      } catch (err) {
        console.error("Error polling job status:", err);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [activeJob, brandId, themeId, refreshTheme]);

  const toggleAsset = (type: AssetType) => {
    setSelectedAssets((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const selectAll = () => {
    setSelectedAssets(assetOptions.map((o) => o.type));
  };

  const deselectAll = () => {
    setSelectedAssets([]);
  };

  const handleGenerate = async () => {
    if (selectedAssets.length === 0) return;

    try {
      setGenerating(true);
      setError(null);

      const response = await api.post<ThemeJob>(
        `/brands/${brandId}/themes/${themeId}/generate/all`,
        {
          asset_types: selectedAssets,
          profile_version: selectedProfile === "latest" ? undefined : parseInt(selectedProfile),
        }
      );

      setActiveJob(response);
      setSelectedAssets([]);
    } catch (err: any) {
      console.error("Error starting generation:", err);
      setError(err.message || "Failed to start generation");
    } finally {
      setGenerating(false);
    }
  };

  const getAssetStatus = (type: AssetType) => {
    const asset = existingAssets.find((a) => a.asset_type === type);
    return asset?.status;
  };

  if (!theme) return null;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Generate Assets</h2>
        <p className="text-muted-foreground">
          Select which assets to generate for this theme.
        </p>
      </div>

      {/* Active Job Progress */}
      {activeJob && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Loader2 className="h-5 w-5 animate-spin text-yellow-600" />
                <div>
                  <p className="font-medium text-yellow-800">Generation in Progress</p>
                  <p className="text-sm text-yellow-700">
                    {activeJob.completed_assets} of {activeJob.total_assets} assets completed
                    {activeJob.failed_assets > 0 && (
                      <span className="text-red-600 ml-2">
                        ({activeJob.failed_assets} failed)
                      </span>
                    )}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-40 h-2 bg-yellow-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-yellow-600 transition-all"
                    style={{ width: `${activeJob.progress}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-yellow-800 w-12">
                  {Math.round(activeJob.progress)}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {/* Profile Selection */}
      {profiles.length > 0 && (
        <div className="flex items-center gap-4">
          <Label>Brand Profile Version:</Label>
          <Select value={selectedProfile} onValueChange={setSelectedProfile}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="latest">Latest (v{profiles[0]?.version})</SelectItem>
              {profiles.map((profile) => (
                <SelectItem key={profile.id} value={profile.version.toString()}>
                  Version {profile.version}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {profiles.length === 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardContent className="py-4">
            <p className="text-orange-800">
              No brand profile found. Please analyze a brand document first to create a profile.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Asset Selection */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">Select Assets to Generate</h3>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={selectAll}>
              Select All
            </Button>
            <Button variant="outline" size="sm" onClick={deselectAll}>
              Deselect All
            </Button>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {assetOptions.map((option) => {
            const isSelected = selectedAssets.includes(option.type);
            const status = getAssetStatus(option.type);

            return (
              <Card
                key={option.type}
                className={`cursor-pointer transition-all ${
                  isSelected ? "border-primary ring-1 ring-primary" : ""
                }`}
                onClick={() => toggleAsset(option.type)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={() => toggleAsset(option.type)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">{option.icon}</span>
                        <span className="font-medium">{option.label}</span>
                        {status && (
                          <Badge
                            variant="outline"
                            className={
                              status === "completed"
                                ? "text-green-600 border-green-600"
                                : status === "failed"
                                ? "text-red-600 border-red-600"
                                : status === "generating"
                                ? "text-yellow-600 border-yellow-600"
                                : ""
                            }
                          >
                            {status === "completed" && <CheckCircle className="h-3 w-3 mr-1" />}
                            {status === "failed" && <AlertCircle className="h-3 w-3 mr-1" />}
                            {status === "generating" && <Loader2 className="h-3 w-3 mr-1 animate-spin" />}
                            {status === "pending" && <Clock className="h-3 w-3 mr-1" />}
                            {status}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {option.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex items-center justify-between pt-4 border-t">
        <p className="text-sm text-muted-foreground">
          {selectedAssets.length} asset{selectedAssets.length !== 1 ? "s" : ""} selected
        </p>
        <Button
          size="lg"
          onClick={handleGenerate}
          disabled={
            generating ||
            selectedAssets.length === 0 ||
            profiles.length === 0 ||
            !!activeJob
          }
        >
          {generating ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Starting...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4 mr-2" />
              Generate {selectedAssets.length > 0 ? `${selectedAssets.length} Assets` : "Assets"}
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
