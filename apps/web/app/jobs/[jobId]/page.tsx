"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  Play,
  FileText,
  AlertCircle,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Header } from "@/components/layout/header";
import { JobStatusBadge } from "@/components/job/job-status-badge";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import * as api from "@/lib/api";
import type { Job } from "@/types";
import { formatDate } from "@/lib/utils";

const JOB_STEPS = {
  analyze_upload: [
    { key: "parsing", label: "Parsing Document", description: "Extracting text and images" },
    { key: "colors", label: "Color Analysis", description: "Identifying color palette" },
    { key: "typography", label: "Typography Analysis", description: "Detecting fonts and styles" },
    { key: "layout", label: "Layout Analysis", description: "Understanding structure" },
    { key: "tone", label: "Tone Analysis", description: "Analyzing brand voice" },
    { key: "profile", label: "Building Profile", description: "Creating brand profile" },
  ],
  generate_website: [
    { key: "loading", label: "Loading Profile", description: "Fetching brand data" },
    { key: "generating", label: "Generating HTML", description: "Creating page structure" },
    { key: "styling", label: "Applying Styles", description: "Adding brand styling" },
    { key: "packaging", label: "Packaging", description: "Creating downloadable ZIP" },
  ],
  generate_newsletter: [
    { key: "loading", label: "Loading Profile", description: "Fetching brand data" },
    { key: "generating", label: "Generating Content", description: "Creating newsletter" },
    { key: "mjml", label: "Converting to MJML", description: "Building email template" },
    { key: "packaging", label: "Packaging", description: "Finalizing output" },
  ],
};

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.jobId as string;
  const { user, token, isLoading: authLoading } = useAuth();
  const { toast } = useToast();

  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/login");
    }
  }, [user, authLoading, router]);

  const loadJob = async () => {
    if (!token || !jobId) return;

    try {
      const data = await api.getJob(token, jobId);
      setJob(data);
    } catch (err) {
      toast({
        title: "Error loading job",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
      router.push("/brands");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadJob();
  }, [token, jobId]);

  // Poll while running
  useEffect(() => {
    if (!job || job.status === "completed" || job.status === "failed") return;

    const interval = setInterval(loadJob, 3000);
    return () => clearInterval(interval);
  }, [job, token, jobId]);

  const getStepStatus = (stepIndex: number, currentStep: number) => {
    if (stepIndex < currentStep) return "completed";
    if (stepIndex === currentStep) return "current";
    return "pending";
  };

  const getCurrentStep = () => {
    if (!job) return 0;
    if (job.status === "completed") {
      const steps = JOB_STEPS[job.job_type as keyof typeof JOB_STEPS] || [];
      return steps.length;
    }
    if (job.status === "failed") {
      // Return the step where it failed based on progress
      const steps = JOB_STEPS[job.job_type as keyof typeof JOB_STEPS] || [];
      return Math.floor((job.progress || 0) / (100 / steps.length));
    }
    const steps = JOB_STEPS[job.job_type as keyof typeof JOB_STEPS] || [];
    return Math.floor((job.progress || 0) / (100 / steps.length));
  };

  if (authLoading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isLoading || !job) {
    return (
      <div className="min-h-screen">
        <Header />
        <main className="container py-6">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </main>
      </div>
    );
  }

  const steps = JOB_STEPS[job.job_type as keyof typeof JOB_STEPS] || [];
  const currentStep = getCurrentStep();

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-6">
        <div className="mb-6">
          <Button variant="ghost" asChild>
            <Link href={`/brands/${job.brand_id}/uploads`}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Uploads
            </Link>
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {/* Main Content */}
          <div className="md:col-span-2 space-y-6">
            {/* Job Header */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      {job.job_type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                    </CardTitle>
                    <CardDescription>Job ID: {job.id}</CardDescription>
                  </div>
                  <JobStatusBadge status={job.status} size="lg" />
                </div>
              </CardHeader>
              <CardContent>
                {(job.status === "pending" || job.status === "running") && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Progress</span>
                      <span>{job.progress || 0}%</span>
                    </div>
                    <Progress value={job.progress || 0} />
                  </div>
                )}
                {job.status === "failed" && job.error_message && (
                  <div className="flex items-start gap-2 p-3 bg-destructive/10 rounded-lg">
                    <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                    <div>
                      <p className="font-medium text-destructive">Error</p>
                      <p className="text-sm text-muted-foreground">{job.error_message}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Steps */}
            <Card>
              <CardHeader>
                <CardTitle>Progress Steps</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {steps.map((step, index) => {
                    const status = getStepStatus(index, currentStep);
                    return (
                      <div key={step.key} className="flex items-start gap-4">
                        <div className="flex flex-col items-center">
                          <div
                            className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                              status === "completed"
                                ? "bg-green-500 border-green-500"
                                : status === "current"
                                ? "border-primary bg-primary/10"
                                : "border-muted-foreground/30"
                            }`}
                          >
                            {status === "completed" ? (
                              <CheckCircle2 className="h-5 w-5 text-white" />
                            ) : status === "current" ? (
                              job.status === "failed" ? (
                                <XCircle className="h-5 w-5 text-destructive" />
                              ) : (
                                <Loader2 className="h-4 w-4 text-primary animate-spin" />
                              )
                            ) : (
                              <span className="text-sm text-muted-foreground">
                                {index + 1}
                              </span>
                            )}
                          </div>
                          {index < steps.length - 1 && (
                            <div
                              className={`w-0.5 h-8 mt-2 ${
                                status === "completed"
                                  ? "bg-green-500"
                                  : "bg-muted-foreground/30"
                              }`}
                            />
                          )}
                        </div>
                        <div className="pt-1">
                          <p
                            className={`font-medium ${
                              status === "pending"
                                ? "text-muted-foreground"
                                : ""
                            }`}
                          >
                            {step.label}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {step.description}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Logs */}
            {job.logs && (Array.isArray(job.logs) ? job.logs.length > 0 : job.logs) && (
              <Card>
                <CardHeader>
                  <CardTitle>Logs</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted rounded-lg p-4 font-mono text-sm max-h-64 overflow-auto">
                    {Array.isArray(job.logs) ? (
                      job.logs.map((log, index) => (
                        <div key={index} className="py-0.5">
                          <span className="text-muted-foreground">
                            [{new Date(log.timestamp).toLocaleTimeString()}]
                          </span>{" "}
                          <span
                            className={
                              log.level === "error"
                                ? "text-destructive"
                                : log.level === "warning"
                                ? "text-yellow-500"
                                : ""
                            }
                          >
                            {log.message}
                          </span>
                        </div>
                      ))
                    ) : (
                      <pre className="whitespace-pre-wrap">{job.logs}</pre>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Job Details */}
            <Card>
              <CardHeader>
                <CardTitle>Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Created</p>
                  <p className="font-medium">{formatDate(job.created_at)}</p>
                </div>
                {job.started_at && (
                  <div>
                    <p className="text-sm text-muted-foreground">Started</p>
                    <p className="font-medium">{formatDate(job.started_at)}</p>
                  </div>
                )}
                {job.completed_at && (
                  <div>
                    <p className="text-sm text-muted-foreground">Completed</p>
                    <p className="font-medium">{formatDate(job.completed_at)}</p>
                  </div>
                )}
                <Separator />
                <div>
                  <p className="text-sm text-muted-foreground">Brand</p>
                  <Button variant="link" className="p-0 h-auto" asChild>
                    <Link href={`/brands/${job.brand_id}/overview`}>
                      View Brand
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Result Actions */}
            {job.status === "completed" && (
              <Card>
                <CardHeader>
                  <CardTitle>Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {job.job_type === "analyze_upload" && job.result?.profile_version && (
                    <Button className="w-full" asChild>
                      <Link href={`/brands/${job.brand_id}/profiles/${job.result.profile_version}`}>
                        View Profile v{job.result.profile_version}
                      </Link>
                    </Button>
                  )}
                  {(job.job_type === "generate_website" || job.job_type === "generate_newsletter") &&
                    job.result?.output_id && (
                      <Button className="w-full" asChild>
                        <Link href={`/brands/${job.brand_id}/outputs`}>
                          View Output
                        </Link>
                      </Button>
                    )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
