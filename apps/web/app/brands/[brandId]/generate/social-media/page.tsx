"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Share2, Loader2, ArrowLeft, Link2, Twitter, Linkedin, Instagram } from "lucide-react";
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
import { Reference, BrandProfile, Job, SocialMediaPlatform } from "@/types";

const PLATFORM_OPTIONS: { id: SocialMediaPlatform; label: string; icon: any }[] = [
  { id: "twitter", label: "Twitter/X", icon: Twitter },
  { id: "linkedin", label: "LinkedIn", icon: Linkedin },
  { id: "instagram", label: "Instagram", icon: Instagram },
  { id: "facebook", label: "Facebook", icon: Share2 },
];

export default function SocialMediaGeneratePage() {
  const { brand, userRole } = useBrand();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [references, setReferences] = useState<Reference[]>([]);
  const [profiles, setProfiles] = useState<BrandProfile[]>([]);
  const [loadingData, setLoadingData] = useState(true);

  // Form state
  const [topic, setTopic] = useState("");
  const [selectedPlatforms, setSelectedPlatforms] = useState<SocialMediaPlatform[]>(["twitter", "linkedin", "instagram"]);
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
    if (!brand || !topic || selectedPlatforms.length === 0) return;

    setIsLoading(true);
    try {
      const job = await api.post<Job>(`/brands/${brand.id}/generate/social-media`, {
        topic,
        platforms: selectedPlatforms,
        reference_id: referenceId || undefined,
        profile_version: profileVersion ? parseInt(profileVersion) : undefined,
      });

      router.push(`/jobs/${job.id}`);
    } catch (error) {
      console.error("Failed to start generation:", error);
      setIsLoading(false);
    }
  };

  const togglePlatform = (platformId: SocialMediaPlatform) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platformId)
        ? prev.filter((p) => p !== platformId)
        : [...prev, platformId]
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
            <Share2 className="h-8 w-8" />
            Generate Social Media Content
          </h1>
          <p className="text-muted-foreground">
            Create on-brand posts for multiple platforms
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
                Define what your social media posts should be about
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="topic">Topic / Campaign</Label>
                <Input
                  id="topic"
                  placeholder="e.g., New Product Launch, Summer Sale, Event Announcement"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Platforms</Label>
                <div className="grid grid-cols-2 gap-3">
                  {PLATFORM_OPTIONS.map((platform) => (
                    <div
                      key={platform.id}
                      className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedPlatforms.includes(platform.id)
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50"
                      }`}
                      onClick={() => togglePlatform(platform.id)}
                    >
                      <Checkbox
                        id={platform.id}
                        checked={selectedPlatforms.includes(platform.id)}
                        onCheckedChange={() => togglePlatform(platform.id)}
                      />
                      <platform.icon className="h-5 w-5" />
                      <label
                        htmlFor={platform.id}
                        className="text-sm font-medium leading-none cursor-pointer"
                      >
                        {platform.label}
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
                  Using a reference will help align content themes with your campaign.
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
              disabled={isLoading || !topic || selectedPlatforms.length === 0}
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Generate Social Media Content
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
