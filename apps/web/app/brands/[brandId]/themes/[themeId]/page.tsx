"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useTheme } from "./theme-context";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  FileText,
  Image,
  Sparkles,
  Settings,
  ArrowRight,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import type { ThemeDocument, ThemeAsset, ThemeJob, ThemeStatus, ThemeUpdateRequest } from "@/types";

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

export default function ThemeOverviewPage() {
  const params = useParams();
  const router = useRouter();
  const brandId = params.brandId as string;
  const themeId = params.themeId as string;
  const { theme, refreshTheme } = useTheme();

  const [documents, setDocuments] = useState<ThemeDocument[]>([]);
  const [assets, setAssets] = useState<ThemeAsset[]>([]);
  const [jobs, setJobs] = useState<ThemeJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editData, setEditData] = useState<ThemeUpdateRequest>({});

  useEffect(() => {
    if (theme) {
      setEditData({
        name: theme.name,
        description: theme.description || "",
      });
    }
  }, [theme]);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [docsData, assetsData, jobsData] = await Promise.all([
          api.get<ThemeDocument[]>(`/brands/${brandId}/themes/${themeId}/documents`),
          api.get<ThemeAsset[]>(`/brands/${brandId}/themes/${themeId}/assets`),
          api.get<ThemeJob[]>(`/brands/${brandId}/themes/${themeId}/jobs`),
        ]);
        setDocuments(docsData);
        setAssets(assetsData);
        setJobs(jobsData);
      } catch (err) {
        console.error("Error loading theme data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [brandId, themeId]);

  const handleSaveEdit = async () => {
    try {
      setSaving(true);
      await api.put(`/brands/${brandId}/themes/${themeId}`, editData);
      await refreshTheme();
      setIsEditOpen(false);
    } catch (err) {
      console.error("Error updating theme:", err);
    } finally {
      setSaving(false);
    }
  };

  if (!theme) return null;

  const completedAssets = assets.filter((a) => a.status === "completed").length;
  const failedAssets = assets.filter((a) => a.status === "failed").length;
  const pendingAssets = assets.filter((a) => a.status === "pending" || a.status === "generating").length;
  const activeJob = jobs.find((j) => j.status === "pending" || j.status === "queued" || j.status === "running");

  return (
    <div className="p-6 space-y-6">
      {/* Status Overview */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Badge className={statusColors[theme.status as ThemeStatus]}>
            {statusLabels[theme.status as ThemeStatus]}
          </Badge>
          <span className="text-sm text-muted-foreground">
            Created {new Date(theme.created_at).toLocaleDateString()}
          </span>
        </div>
        <Button variant="outline" size="sm" onClick={() => setIsEditOpen(true)}>
          <Settings className="h-4 w-4 mr-2" />
          Edit Theme
        </Button>
      </div>

      {/* Active Job Banner */}
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
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-yellow-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-yellow-600 transition-all"
                    style={{ width: `${activeJob.progress}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-yellow-800">
                  {Math.round(activeJob.progress)}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => router.push(`/brands/${brandId}/themes/${themeId}/context`)}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Documents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{documents.length}</span>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {documents.length === 0 ? "Add context documents" : "Reference materials"}
            </p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => router.push(`/brands/${brandId}/themes/${themeId}/generate`)}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Generate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">
                {pendingAssets > 0 ? pendingAssets : "0"}
              </span>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {pendingAssets > 0 ? "In progress" : "Start generating assets"}
            </p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => router.push(`/brands/${brandId}/themes/${themeId}/assets`)}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Image className="h-4 w-4" />
              Assets
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold">{completedAssets}</span>
                {failedAssets > 0 && (
                  <span className="text-sm text-destructive">({failedAssets} failed)</span>
                )}
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {completedAssets === 0 ? "No assets yet" : "Ready to download"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      {jobs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Jobs</CardTitle>
            <CardDescription>Asset generation history</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {jobs.slice(0, 5).map((job) => (
                <div key={job.id} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div className="flex items-center gap-3">
                    {job.status === "completed" && (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    )}
                    {job.status === "failed" && (
                      <AlertCircle className="h-4 w-4 text-destructive" />
                    )}
                    {(job.status === "pending" || job.status === "queued" || job.status === "running") && (
                      <Loader2 className="h-4 w-4 animate-spin text-yellow-600" />
                    )}
                    <div>
                      <p className="text-sm font-medium">
                        {job.total_assets} assets
                      </p>
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(job.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm">
                      {job.completed_assets}/{job.total_assets} completed
                    </p>
                    {job.failed_assets > 0 && (
                      <p className="text-xs text-destructive">{job.failed_assets} failed</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      {assets.length === 0 && documents.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="py-8">
            <div className="text-center space-y-4">
              <Sparkles className="h-12 w-12 mx-auto text-muted-foreground" />
              <div>
                <h3 className="text-lg font-semibold">Get Started</h3>
                <p className="text-muted-foreground">
                  Upload reference documents or start generating assets right away.
                </p>
              </div>
              <div className="flex items-center justify-center gap-3">
                <Link href={`/brands/${brandId}/themes/${themeId}/context`}>
                  <Button variant="outline">
                    <FileText className="h-4 w-4 mr-2" />
                    Add Documents
                  </Button>
                </Link>
                <Link href={`/brands/${brandId}/themes/${themeId}/generate`}>
                  <Button>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate Assets
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Edit Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Theme</DialogTitle>
            <DialogDescription>Update theme name and description.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Name</Label>
              <Input
                id="edit-name"
                value={editData.name || ""}
                onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={editData.description || ""}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveEdit} disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
