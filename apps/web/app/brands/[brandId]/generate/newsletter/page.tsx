"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Mail, Loader2, AlertCircle } from "lucide-react";
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

export default function GenerateNewsletterPage() {
  const { brand, userRole } = useBrand();
  const { token } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  const [profiles, setProfiles] = useState<BrandProfile[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  // Form fields
  const [subject, setSubject] = useState("");
  const [preheader, setPreheader] = useState("");
  const [headline, setHeadline] = useState("");
  const [bodyContent, setBodyContent] = useState("");
  const [ctaText, setCtaText] = useState("Learn More");
  const [ctaUrl, setCtaUrl] = useState("#");
  const [footerText, setFooterText] = useState("");

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
      const job = await api.generateNewsletter(token, brand.id, {
        profile_version: parseInt(selectedVersion, 10),
        subject: subject || undefined,
        preheader: preheader || undefined,
        headline: headline || undefined,
        body_content: bodyContent || undefined,
        cta_text: ctaText || undefined,
        cta_url: ctaUrl || undefined,
        footer_text: footerText || undefined,
      });

      toast({
        title: "Generation started",
        description: "Your newsletter is being generated",
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
            <Mail className="h-6 w-6" />
            Generate Newsletter
          </h1>
          <p className="text-sm text-muted-foreground">
            Create an email-ready newsletter template
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
                <CardTitle>Email Header</CardTitle>
                <CardDescription>
                  Subject line and preview text
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="subject">Subject Line</Label>
                  <Input
                    id="subject"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="Your Monthly Update is Here!"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="preheader">Preheader Text</Label>
                  <Input
                    id="preheader"
                    value={preheader}
                    onChange={(e) => setPreheader(e.target.value)}
                    placeholder="A brief preview that appears in inbox..."
                  />
                  <p className="text-xs text-muted-foreground">
                    Appears after the subject line in email clients
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Content</CardTitle>
                <CardDescription>
                  Main newsletter content
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="headline">Headline</Label>
                  <Input
                    id="headline"
                    value={headline}
                    onChange={(e) => setHeadline(e.target.value)}
                    placeholder="Big News This Month!"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bodyContent">Body Content</Label>
                  <Textarea
                    id="bodyContent"
                    value={bodyContent}
                    onChange={(e) => setBodyContent(e.target.value)}
                    placeholder="Write your main newsletter content here. You can include multiple paragraphs..."
                    rows={8}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="ctaText">CTA Button Text</Label>
                    <Input
                      id="ctaText"
                      value={ctaText}
                      onChange={(e) => setCtaText(e.target.value)}
                      placeholder="Learn More"
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
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Footer</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label htmlFor="footerText">Footer Text</Label>
                  <Textarea
                    id="footerText"
                    value={footerText}
                    onChange={(e) => setFooterText(e.target.value)}
                    placeholder="Company Name | Address | Unsubscribe link"
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
                  <li>• HTML email template</li>
                  <li>• MJML source file</li>
                  <li>• Email client compatible</li>
                  <li>• Downloadable files</li>
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
              Generate Newsletter
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
