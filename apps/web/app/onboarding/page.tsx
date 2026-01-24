"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, CheckCircle, FileText, Loader2, Sparkles, Upload } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import * as api from "@/lib/api";
import type { Brand, BrandProfile, Job, Upload as UploadType } from "@/types";

type Step = 1 | 2 | 3 | 4;

export default function OnboardingPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  const [step, setStep] = useState<Step>(1);
  const [brand, setBrand] = useState<Brand | null>(null);
  const [upload, setUpload] = useState<UploadType | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [profile, setProfile] = useState<BrandProfile | null>(null);

  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  useEffect(() => {
    if (name.trim().length === 0) {
      setSlug("");
      return;
    }
    const next = name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
    setSlug(next);
  }, [name]);

  const stepLabel = useMemo(() => {
    switch (step) {
      case 1:
        return "Create brand";
      case 2:
        return "Upload document";
      case 3:
        return "Analyze";
      case 4:
        return "Next steps";
      default:
        return "";
    }
  }, [step]);

  const handleCreateBrand = async () => {
    if (!token || !name || !slug) return;
    setIsBusy(true);
    try {
      const created = await api.createBrand(token, {
        name,
        slug,
        description: description || undefined,
      });
      setBrand(created);
      setStep(2);
      toast({ title: "Brand created", description: created.name });
    } catch (err) {
      toast({
        title: "Failed to create brand",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsBusy(false);
    }
  };

  const handleUseDemo = async () => {
    try {
      const res = await fetch("/demo/sample.pptx");
      const blob = await res.blob();
      setFile(new File([blob], "demo-sample.pptx", { type: blob.type || "application/vnd.openxmlformats-officedocument.presentationml.presentation" }));
    } catch (err) {
      toast({
        title: "Failed to load demo file",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const handleUpload = async () => {
    if (!token || !brand || !file) return;
    setIsBusy(true);
    try {
      const uploadResp = await api.uploadFile(token, brand.id, file);
      setUpload(uploadResp);
      setStep(3);
      toast({ title: "Document uploaded", description: uploadResp.original_filename });
    } catch (err) {
      toast({
        title: "Upload failed",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsBusy(false);
    }
  };

  const handleAnalyze = async () => {
    if (!token || !brand || !upload) return;
    setIsBusy(true);
    try {
      const jobResp = await api.startAnalysis(token, brand.id, upload.id);
      setJob(jobResp);
      toast({ title: "Analysis started", description: "We are extracting your brand DNA." });

      let current = jobResp;
      for (let i = 0; i < 30; i += 1) {
        const refreshed = await api.getJob(token, current.id);
        setJob(refreshed);
        if (refreshed.status === "completed") {
          const latest = await api.getProfiles(token, brand.id);
          if (latest.length > 0) {
            setProfile(latest[0]);
          }
          setStep(4);
          toast({ title: "Profile ready", description: "Your brand profile is ready." });
          return;
        }
        if (refreshed.status === "failed") {
          throw new Error(refreshed.error_message || "Analysis failed");
        }
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
      throw new Error("Analysis is taking longer than expected. Check Jobs.");
    } catch (err) {
      toast({
        title: "Analysis failed",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsBusy(false);
    }
  };

  if (isLoading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Guided Setup</h1>
          <p className="text-muted-foreground">
            Follow the steps to create your first brand profile.
          </p>
        </div>
        <Badge variant="secondary">Step {step} of 4: {stepLabel}</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {["Create brand", "Upload doc", "Analyze", "Next steps"].map((label, index) => {
          const idx = (index + 1) as Step;
          const active = step === idx;
          const done = step > idx;
          return (
            <Card key={label} className={active ? "border-primary" : ""}>
              <CardContent className="py-4 flex items-center justify-between">
                <span className={done ? "text-muted-foreground" : "font-medium"}>{label}</span>
                {done && <CheckCircle className="h-4 w-4 text-green-600" />}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Create your brand</CardTitle>
            <CardDescription>This will be your workspace for documents and outputs.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="brand-name">Brand name</Label>
              <Input id="brand-name" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="brand-slug">Slug</Label>
              <Input id="brand-slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="brand-desc">Description (optional)</Label>
              <Textarea id="brand-desc" value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>
            <div className="flex justify-end">
              <Button onClick={handleCreateBrand} disabled={!name || !slug || isBusy}>
                {isBusy ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Create brand
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Upload a brand document</CardTitle>
            <CardDescription>Use a deck or PDF so we can extract design tokens.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <Input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              <Button variant="outline" onClick={handleUseDemo}>
                <FileText className="h-4 w-4 mr-2" />
                Use demo file
              </Button>
            </div>
            {file && (
              <div className="text-sm text-muted-foreground">
                Selected: {file.name}
              </div>
            )}
            <div className="flex justify-end">
              <Button onClick={handleUpload} disabled={!file || isBusy}>
                {isBusy ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
                Upload
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Analyze your document</CardTitle>
            <CardDescription>We’ll extract colors, typography, layout, and tone.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-sm text-muted-foreground">
              Upload: {upload?.original_filename}
            </div>
            <Button onClick={handleAnalyze} disabled={isBusy} className="w-full">
              {isBusy ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Sparkles className="h-4 w-4 mr-2" />}
              Start analysis
            </Button>
            {job && (
              <div className="text-sm text-muted-foreground">
                Status: {job.status}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {step === 4 && brand && (
        <Card>
          <CardHeader>
            <CardTitle>Next steps</CardTitle>
            <CardDescription>Your brand profile is ready. What would you like to do?</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              variant="outline"
              className="w-full justify-between"
              onClick={() => router.push(`/brands/${brand.id}/profiles/${profile?.version || 1}`)}
            >
              View brand profile
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button
              className="w-full justify-between"
              onClick={() => router.push(`/brands/${brand.id}/generate`)}
            >
              Generate content
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
              className="w-full justify-between"
              onClick={() => router.push(`/brands/${brand.id}/themes?new=true`)}
            >
              Create a theme
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
