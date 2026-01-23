"use client";

import { Badge } from "@/components/ui/badge";
import type { JobStatus } from "@/types";
import { Loader2 } from "lucide-react";

interface JobStatusBadgeProps {
  status: JobStatus;
  progress?: number;
  size?: "default" | "lg";
}

export function JobStatusBadge({ status, progress, size = "default" }: JobStatusBadgeProps) {
  const variants: Record<JobStatus, "default" | "secondary" | "success" | "destructive" | "warning"> = {
    pending: "secondary",
    queued: "secondary",
    running: "warning",
    completed: "success",
    failed: "destructive",
  };

  const labels: Record<JobStatus, string> = {
    pending: "Pending",
    queued: "Queued",
    running: progress !== undefined ? `Running ${Math.round(progress * 100)}%` : "Running",
    completed: "Completed",
    failed: "Failed",
  };

  return (
    <Badge
      variant={variants[status]}
      className={`gap-1 ${size === "lg" ? "text-sm px-3 py-1" : ""}`}
    >
      {status === "running" && <Loader2 className={`animate-spin ${size === "lg" ? "h-4 w-4" : "h-3 w-3"}`} />}
      {labels[status]}
    </Badge>
  );
}
