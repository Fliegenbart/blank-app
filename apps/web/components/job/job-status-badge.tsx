"use client";

import { Badge } from "@/components/ui/badge";
import type { JobStatus } from "@/types";
import { Loader2 } from "lucide-react";

interface JobStatusBadgeProps {
  status: JobStatus;
  progress?: number;
}

export function JobStatusBadge({ status, progress }: JobStatusBadgeProps) {
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
    <Badge variant={variants[status]} className="gap-1">
      {status === "running" && <Loader2 className="h-3 w-3 animate-spin" />}
      {labels[status]}
    </Badge>
  );
}
