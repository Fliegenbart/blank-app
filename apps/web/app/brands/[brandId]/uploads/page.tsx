"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Play, Trash2, Loader2, RefreshCw } from "lucide-react";
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
import { useBrand } from "../layout";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { UploadDropzone } from "@/components/brand/upload-dropzone";
import { JobStatusBadge } from "@/components/job/job-status-badge";
import * as api from "@/lib/api";
import type { Upload, Job } from "@/types";
import { formatDate, formatBytes } from "@/lib/utils";

export default function UploadsPage() {
  const { brand, userRole } = useBrand();
  const { token } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  const [uploads, setUploads] = useState<Upload[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [analyzingUploadId, setAnalyzingUploadId] = useState<string | null>(null);
  const [deleteUploadId, setDeleteUploadId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const canEdit = userRole === "owner" || userRole === "editor";

  const loadData = async () => {
    if (!token || !brand) return;

    try {
      const [uploadsData, jobsData] = await Promise.all([
        api.getUploads(token, brand.id),
        api.getJobs(token, brand.id),
      ]);
      setUploads(uploadsData);
      setJobs(jobsData.filter((j) => j.job_type === "analyze_upload"));
    } catch (err) {
      toast({
        title: "Error loading data",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token, brand]);

  // Poll for running jobs
  useEffect(() => {
    const hasRunningJobs = jobs.some(
      (j) => j.status === "pending" || j.status === "running"
    );
    if (!hasRunningJobs) return;

    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, [jobs, token, brand]);

  const handleUploadComplete = async (upload: Upload) => {
    setUploads((prev) => [upload, ...prev]);
    toast({
      title: "Upload complete",
      description: `${upload.original_filename} uploaded successfully`,
    });
  };

  const handleAnalyze = async (uploadId: string) => {
    if (!token || !brand) return;

    setAnalyzingUploadId(uploadId);
    try {
      const job = await api.startAnalysis(token, brand.id, uploadId);
      setJobs((prev) => [job, ...prev]);
      toast({
        title: "Analysis started",
        description: "You can track the progress below",
      });
    } catch (err) {
      toast({
        title: "Failed to start analysis",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setAnalyzingUploadId(null);
    }
  };

  const handleDelete = async () => {
    if (!token || !brand || !deleteUploadId) return;

    setIsDeleting(true);
    try {
      await api.deleteUpload(token, brand.id, deleteUploadId);
      setUploads((prev) => prev.filter((u) => u.id !== deleteUploadId));
      toast({ title: "Upload deleted" });
    } catch (err) {
      toast({
        title: "Failed to delete upload",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
      setDeleteUploadId(null);
    }
  };

  const getFileIcon = (fileType: string) => {
    if (fileType === "pdf") {
      return <FileText className="h-4 w-4 text-red-500" />;
    }
    if (fileType === "pptx" || fileType === "ppt") {
      return <FileText className="h-4 w-4 text-orange-500" />;
    }
    return <FileText className="h-4 w-4 text-muted-foreground" />;
  };

  const isAnalyzed = (upload: Upload) => upload.status === "processed";

  if (!brand) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Uploads</h1>
          <p className="text-muted-foreground">
            Upload brand documents for analysis
          </p>
        </div>
        <Button variant="outline" onClick={loadData} disabled={isLoading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Upload Dropzone */}
      {canEdit && (
        <Card>
          <CardHeader>
            <CardTitle>Upload Document</CardTitle>
            <CardDescription>
              Upload PDF or PPTX files containing brand guidelines, presentations, or marketing materials
            </CardDescription>
          </CardHeader>
          <CardContent>
            <UploadDropzone
              brandId={brand.id}
              onUploadComplete={handleUploadComplete}
            />
          </CardContent>
        </Card>
      )}

      {/* Uploads Table */}
      <Card>
        <CardHeader>
          <CardTitle>Documents</CardTitle>
          <CardDescription>
            {uploads.length} document{uploads.length !== 1 ? "s" : ""} uploaded
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : uploads.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No documents uploaded yet
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Uploaded</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {uploads.map((upload) => {
                  const relatedJob = jobs.find(
                    (j) => j.input_data?.upload_id === upload.id
                  );
                  const isAnalyzing = analyzingUploadId === upload.id;

                  return (
                    <TableRow key={upload.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getFileIcon(upload.file_type)}
                          <span className="font-medium">
                            {upload.original_filename}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>{formatBytes(upload.file_size)}</TableCell>
                      <TableCell>
                        {isAnalyzed(upload) ? (
                          <Badge variant="success">Analyzed</Badge>
                        ) : relatedJob ? (
                          <JobStatusBadge status={relatedJob.status} />
                        ) : (
                          <Badge variant="secondary">Pending</Badge>
                        )}
                      </TableCell>
                      <TableCell>{formatDate(upload.created_at)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          {!isAnalyzed(upload) && canEdit && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleAnalyze(upload.id)}
                              disabled={isAnalyzing || !!relatedJob}
                            >
                              {isAnalyzing ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              ) : (
                                <Play className="mr-2 h-4 w-4" />
                              )}
                              Analyze
                            </Button>
                          )}
                          {canEdit && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setDeleteUploadId(upload.id)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Recent Jobs */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Jobs</CardTitle>
          <CardDescription>
            Recent analysis tasks for this brand
          </CardDescription>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No analysis jobs yet
            </p>
          ) : (
            <div className="space-y-2">
              {jobs.slice(0, 10).map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-muted/50"
                  onClick={() => router.push(`/jobs/${job.id}`)}
                >
                  <div className="flex items-center gap-3">
                    <JobStatusBadge status={job.status} />
                    <div>
                      <p className="font-medium text-sm">
                        {job.input_data?.filename || "Analysis"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(job.created_at)}
                      </p>
                    </div>
                  </div>
                  {job.progress !== undefined && job.progress < 100 && (
                    <span className="text-sm text-muted-foreground">
                      {job.progress}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteUploadId} onOpenChange={() => setDeleteUploadId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Upload</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this upload? This action cannot be undone.
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
    </div>
  );
}
