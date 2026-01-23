"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { LayoutTemplate, Loader2, ArrowLeft, Link2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useBrand } from "../../layout";
import { api } from "@/lib/api";
import { Reference, BrandProfile, Job } from "@/types";

const SECTION_OPTIONS = [
  { id: "hero", label: "Hero Section" },
  { id: "features", label: "Features" },
  { id: "testimonials", label: "Testimonials" },
  { id: "cta", label: "Call to Action" },
  { id: "pricing", label: "Pricing" },
  { id: "faq", label: "FAQ" },
  { id: "contact", label: "Contact" },
];

export default function LandingPageGeneratePage() {
  const { brand, userRole } = useBrand();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [references, setReferences] = useState<Reference[]>([]);
  const [profiles, setProfiles] = useState<BrandProfile[]>([]);
  const [loadingData, setLoadingData] = useState(true);

  // Form state
  const [topic, setTopic] = useState("");
  const [selectedSections, setSelectedSections] = useState<string[]>(["hero", "features", "cta"]);
  const [referenceId, setReferenceId] = useState<string>("");
  const [profileVersion, setProfileVersion] = useState<string>("");

  const canEdit = userRole === "owner" || userRole === "editor";

  useEffect(() => {
    if (brand) {
      loadData();
    }
  }, [brand]);

  const loadData = async () => {
    if (!brand) return;
    try {
      const [refsData, profilesData] = await Promise.all([
        api.get<Reference[]>(`/brands/${brand.id}/references`),
        api.get<BrandProfile[]>(`/brands/${brand.id}/profiles`),
      ]);
      setReferences(refsData.filter((r) => r.status === "completed"));
      setProfiles(profilesData);
      if (profilesData.length > 0) {
        setProfileVersion(profilesData[0].version.toString());
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const handleGenerate = async () => {
    if (!brand || !topic) return;

    setIsLoading(true);
    try {
      const job = await api.post<Job>(`/brands/${brand.id}/generate/landing-page`, {
        topic,
        sections: selectedSections.length > 0 ? selectedSections : undefined,
        reference_id: referenceId || undefined,
        profile_version: profileVersion ? parseInt(profileVersion) : undefined,
      });

      router.push(`/jobs/${job.id}`);
    } catch (error) {
      console.error("Failed to start generation:", error);
      setIsLoading(false);
    }
  };

  const toggleSection = (sectionId: string) => {
    setSelectedSections((prev) =>
      prev.includes(sectionId)
        ? prev.filter((s) => s !== sectionId)
        : [...prev, sectionId]
    );
  };

  if (!brand) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <LayoutTemplate className="h-8 w-8" />
            Generate Landing Page
          </h1>
          <p className="text-muted-foreground">
            Create an AI-powered landing page with your brand styling
          </p>
        </div>
      </div>

      {!canEdit ? (
        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="pt-6">
            <p className="text-sm text-yellow-600 dark:text-yellow-400">
              You need editor access to generate content.
            </p>
          </CardContent>
        </Card>
      ) : profiles.length === 0 ? (
        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="pt-6">
            <p className="text-sm text-yellow-600 dark:text-yellow-400">
              Please analyze a brand document first to create a brand profile.
            </p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => router.push(`/brands/${brand.id}/uploads`)}
            >
              Go to Uploads
            </Button>
          </CardContent>
        </Card>
      ) : loadingData ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Content Details</CardTitle>
              <CardDescription>
                Define what your landing page should be about
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="topic">Topic / Page Title</Label>
                <Input
                  id="topic"
                  placeholder="e.g., Summer Event 2025, Product Launch, Service Offering"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Sections</Label>
                <div className="grid grid-cols-2 gap-2">
                  {SECTION_OPTIONS.map((section) => (
                    <div key={section.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={section.id}
                        checked={selectedSections.includes(section.id)}
                        onCheckedChange={() => toggleSection(section.id)}
                      />
                      <label
                        htmlFor={section.id}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        {section.label}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Generation Options</CardTitle>
              <CardDescription>
                Configure how the content is generated
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="profile">Brand Profile Version</Label>
                <Select value={profileVersion} onValueChange={setProfileVersion}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select profile version" />
                  </SelectTrigger>
                  <SelectContent>
                    {profiles.map((profile) => (
                      <SelectItem key={profile.version} value={profile.version.toString()}>
                        Version {profile.version} -{" "}
                        {new Date(profile.created_at).toLocaleDateString()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="reference" className="flex items-center gap-2">
                  <Link2 className="h-4 w-4" />
                  Reference Website (Optional)
                </Label>
                <Select value={referenceId} onValueChange={setReferenceId}>
                  <SelectTrigger>
                    <SelectValue placeholder="No reference - generate fresh content" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No reference</SelectItem>
                    {references.map((ref) => (
                      <SelectItem key={ref.id} value={ref.id}>
                        {ref.name} ({ref.page_count} pages)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Using a reference will base the structure and content themes on the analyzed website.
                </p>
              </div>

              {references.length === 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push(`/brands/${brand.id}/references`)}
                >
                  <Link2 className="mr-2 h-4 w-4" />
                  Add Reference Websites
                </Button>
              )}
            </CardContent>
          </Card>

          <div className="lg:col-span-2">
            <Button
              size="lg"
              className="w-full"
              onClick={handleGenerate}
              disabled={isLoading || !topic}
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Generate Landing Page
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
