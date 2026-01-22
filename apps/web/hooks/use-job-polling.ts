"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { Job } from "@/types";
import * as api from "@/lib/api";

interface UseJobPollingOptions {
  token: string;
  jobId: string;
  interval?: number;
  onComplete?: (job: Job) => void;
  onError?: (job: Job) => void;
}

export function useJobPolling({
  token,
  jobId,
  interval = 3000,
  onComplete,
  onError,
}: UseJobPollingOptions) {
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);

  // Update refs when callbacks change
  useEffect(() => {
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  }, [onComplete, onError]);

  const fetchJob = useCallback(async () => {
    try {
      const fetchedJob = await api.getJob(token, jobId);
      setJob(fetchedJob);
      setError(null);

      // Check if job is complete
      if (fetchedJob.status === "completed") {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        onCompleteRef.current?.(fetchedJob);
      } else if (fetchedJob.status === "failed") {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        onErrorRef.current?.(fetchedJob);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch job"));
    } finally {
      setIsLoading(false);
    }
  }, [token, jobId]);

  useEffect(() => {
    // Initial fetch
    fetchJob();

    // Start polling
    intervalRef.current = setInterval(fetchJob, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchJob, interval]);

  const refetch = useCallback(() => {
    setIsLoading(true);
    fetchJob();
  }, [fetchJob]);

  return { job, isLoading, error, refetch };
}
