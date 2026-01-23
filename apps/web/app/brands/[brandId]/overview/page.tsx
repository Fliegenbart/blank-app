"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Palette, Upload, FileOutput, Users, ArrowRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useBrand } from "../layout";
import { useAuth } from "@/hooks/use-auth";
import * as api from "@/lib/api";
import type { BrandProfile, Upload as UploadType, Output, Job } from "@/types";
import { formatDate } from "@/lib/utils";

export default function BrandOverviewPage() {
  const { brand, userRole } = useBrand();
  const { token } = useAuth();
  const router = useRouter();

  const [latestProfile, setLatestProfile] = useState<BrandProfile | null>(null);
  const [uploads, setUploads] = useState<UploadType[]>([]);
  const [outputs, setOutputs] = useState<Output[]>([]);
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);

  useEffect(() => {
    if (!token || !brand) return;

    // Load overview data
    api.getProfiles(token, brand.id).then((profiles) => {
      if (profiles.length > 0) {
        setLatestProfile(profiles[0]);
      }
    });

    api.getUploads(token, brand.id).then(setUploads);
    api.getOutputs(token, brand.id).then(setOutputs);
    api.getJobs(token, brand.id).then((jobs) => setRecentJobs(jobs.slice(0, 5)));
  }, [token, brand]);

  if (!brand) return null;

  const canEdit = userRole === "owner" || userRole === "editor";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{brand.name}</h1>
          {brand.description && (
            <p className="text-muted-foreground mt-1">{brand.description}</p>
          )}
        </div>
        <Badge variant="secondary">{userRole}</Badge>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Profile Version</CardTitle>
            <Palette className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {latestProfile ? `v${latestProfile.version}` : "None"}
            </div>
            <p className="text-xs text-muted-foreground">
              {latestProfile
                ? `Updated ${formatDate(latestProfile.created_at)}`
                : "No profile yet"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uploads</CardTitle>
            <Upload className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{uploads.length}</div>
            <p className="text-xs text-muted-foreground">Source documents</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Outputs</CardTitle>
            <FileOutput className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{outputs.length}</div>
            <p className="text-xs text-muted-foreground">Generated assets</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{brand.members?.length || 1}</div>
            <p className="text-xs text-muted-foreground">Collaborators</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Get Started</CardTitle>
            <CardDescription>
              {latestProfile
                ? "Your brand profile is ready"
                : "Upload a document to analyze your brand"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {!latestProfile ? (
              <Button
                className="w-full"
                onClick={() => router.push(`/brands/${brand.id}/uploads`)}
                disabled={!canEdit}
              >
                Upload Document
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() =>
                    router.push(`/brands/${brand.id}/profiles/${latestProfile.version}`)
                  }
                >
                  View Brand Profile
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
                <Button
                  className="w-full"
                  onClick={() => router.push(`/brands/${brand.id}/generate`)}
                  disabled={!canEdit}
                >
                  Generate Content
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Jobs</CardTitle>
            <CardDescription>Latest analysis and generation tasks</CardDescription>
          </CardHeader>
          <CardContent>
            {recentJobs.length === 0 ? (
              <p className="text-sm text-muted-foreground">No jobs yet</p>
            ) : (
              <div className="space-y-2">
                {recentJobs.map((job) => (
                  <div
                    key={job.id}
                    className="flex items-center justify-between text-sm cursor-pointer hover:bg-muted p-2 rounded"
                    onClick={() => router.push(`/jobs/${job.id}`)}
                  >
                    <span>{job.job_type.replace("_", " ")}</span>
                    <Badge
                      variant={
                        job.status === "completed"
                          ? "success"
                          : job.status === "failed"
                          ? "destructive"
                          : "secondary"
                      }
                    >
                      {job.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
