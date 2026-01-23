"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Globe, Loader2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { useBrand } from "../../layout";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import * as api from "@/lib/api";
import type { BrandProfile } from "@/types";

export default function GenerateWebsitePage() {
  const { brand, userRole } = useBrand();
  const { token } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  const [profiles, setProfiles] = useState<BrandProfile[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  // Form fields
  const [pageTitle, setPageTitle] = useState("");
  const [headline, setHeadline] = useState("");
  const [subheadline, setSubheadline] = useState("");
  const [ctaText, setCtaText] = useState("Get Started");
  const [ctaUrl, setCtaUrl] = useState("#");
  const [sections, setSections] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");

  const canEdit = userRole === "owner" || userRole === "editor";

  useEffect(() => {
    if (!token || !brand) return;

    api
      .getProfiles(token, brand.id)
      .then((data) => {
        setProfiles(data);
        if (data.length > 0) {
          setSelectedVersion(data[0].version.toString());
        }
      })
      .catch((err) => {
        toast({
          title: "Error loading profiles",
          description: err instanceof Error ? err.message : "Unknown error",
          variant: "destructive",
        });
      })
      .finally(() => setIsLoading(false));
  }, [token, brand, toast]);

  const handleGenerate = async () => {
    if (!token || !brand || !selectedVersion) return;

    setIsGenerating(true);
    try {
      const job = await api.generateWebsite(token, brand.id, {
        profile_version: parseInt(selectedVersion, 10),
        page_title: pageTitle || undefined,
        headline: headline || undefined,
        subheadline: subheadline || undefined,
        cta_text: ctaText || undefined,
        cta_url: ctaUrl || undefined,
        sections: sections ? sections.split("\n").filter(Boolean) : undefined,
        additional_notes: additionalNotes || undefined,
      });

      toast({
        title: "Generation started",
        description: "Your website is being generated",
      });

      router.push(`/jobs/${job.id}`);
    } catch (err) {
      toast({
        title: "Failed to start generation",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  if (!brand) return null;

  if (!canEdit) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" asChild>
          <Link href={`/brands/${brand.id}/generate`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Generate
          </Link>
        </Button>
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <p>You don&apos;t have permission to generate content for this brand.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href={`/brands/${brand.id}/generate`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Link>
        </Button>
        <Separator orientation="vertical" className="h-6" />
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Globe className="h-6 w-6" />
            Generate Website
          </h1>
          <p className="text-sm text-muted-foreground">
            Create a branded landing page
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : profiles.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-yellow-600">
              <AlertCircle className="h-5 w-5" />
              <p>No brand profiles found. Upload and analyze a document first.</p>
            </div>
            <Button className="mt-4" onClick={() => router.push(`/brands/${brand.id}/uploads`)}>
              Go to Uploads
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-3">
          {/* Form */}
          <div className="md:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Page Content</CardTitle>
                <CardDescription>
                  Customize your landing page content
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="pageTitle">Page Title</Label>
                  <Input
                    id="pageTitle"
                    value={pageTitle}
                    onChange={(e) => setPageTitle(e.target.value)}
                    placeholder="Welcome to Our Brand"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="headline">Headline</Label>
                  <Input
                    id="headline"
                    value={headline}
                    onChange={(e) => setHeadline(e.target.value)}
                    placeholder="Transform Your Business Today"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="subheadline">Subheadline</Label>
                  <Textarea
                    id="subheadline"
                    value={subheadline}
                    onChange={(e) => setSubheadline(e.target.value)}
                    placeholder="Discover how our solution can help you achieve your goals..."
                    rows={2}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="ctaText">CTA Button Text</Label>
                    <Input
                      id="ctaText"
                      value={ctaText}
                      onChange={(e) => setCtaText(e.target.value)}
                      placeholder="Get Started"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="ctaUrl">CTA Button URL</Label>
                    <Input
                      id="ctaUrl"
                      value={ctaUrl}
                      onChange={(e) => setCtaUrl(e.target.value)}
                      placeholder="https://..."
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sections">Sections (one per line)</Label>
                  <Textarea
                    id="sections"
                    value={sections}
                    onChange={(e) => setSections(e.target.value)}
                    placeholder="Features&#10;Benefits&#10;Testimonials&#10;Pricing&#10;FAQ"
                    rows={4}
                  />
                  <p className="text-xs text-muted-foreground">
                    Optional: List the sections you want on your page
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Additional Notes</Label>
                  <Textarea
                    id="notes"
                    value={additionalNotes}
                    onChange={(e) => setAdditionalNotes(e.target.value)}
                    placeholder="Any specific requirements or preferences..."
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Settings Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Brand Profile Version</Label>
                  <Select value={selectedVersion} onValueChange={setSelectedVersion}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select version" />
                    </SelectTrigger>
                    <SelectContent>
                      {profiles.map((profile) => (
                        <SelectItem key={profile.version} value={profile.version.toString()}>
                          Version {profile.version}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    The brand profile to use for styling
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Output</CardTitle>
                <CardDescription>What you&apos;ll receive</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-2 text-muted-foreground">
                  <li>• index.html with responsive layout</li>
                  <li>• styles.css with brand colors & fonts</li>
                  <li>• Downloadable ZIP file</li>
                </ul>
              </CardContent>
            </Card>

            <Button
              className="w-full"
              size="lg"
              onClick={handleGenerate}
              disabled={isGenerating || !selectedVersion}
            >
              {isGenerating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Generate Website
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
