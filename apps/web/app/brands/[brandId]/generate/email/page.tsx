"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Mail, Loader2, ArrowLeft, Link2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useBrand } from "../../layout";
import { api } from "@/lib/api";
import { Reference, BrandProfile, Job, EmailType } from "@/types";

const EMAIL_TYPES: { id: EmailType; label: string; description: string }[] = [
  {
    id: "newsletter",
    label: "Newsletter",
    description: "Regular updates and content for subscribers",
  },
  {
    id: "promotional",
    label: "Promotional",
    description: "Special offers, discounts, and sales",
  },
  {
    id: "announcement",
    label: "Announcement",
    description: "News, updates, and important information",
  },
  {
    id: "welcome",
    label: "Welcome Email",
    description: "Onboarding new subscribers or customers",
  },
  {
    id: "followup",
    label: "Follow-up",
    description: "Post-event or post-purchase communication",
  },
];

export default function EmailGeneratePage() {
  const { brand, userRole } = useBrand();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [references, setReferences] = useState<Reference[]>([]);
  const [profiles, setProfiles] = useState<BrandProfile[]>([]);
  const [loadingData, setLoadingData] = useState(true);

  // Form state
  const [topic, setTopic] = useState("");
  const [emailType, setEmailType] = useState<EmailType>("newsletter");
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
      const job = await api.post<Job>(`/brands/${brand.id}/generate/email`, {
        topic,
        email_type: emailType,
        reference_id: referenceId && referenceId !== "none" ? referenceId : undefined,
        profile_version: profileVersion ? parseInt(profileVersion) : undefined,
      });

      router.push(`/jobs/${job.id}`);
    } catch (error) {
      console.error("Failed to start generation:", error);
      setIsLoading(false);
    }
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
            <Mail className="h-8 w-8" />
            Generate Email Template
          </h1>
          <p className="text-muted-foreground">
            Create professional email templates in your brand style
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
              <CardTitle>Email Details</CardTitle>
              <CardDescription>
                Define your email topic and type
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="topic">Topic / Subject</Label>
                <Input
                  id="topic"
                  placeholder="e.g., Summer Event Registration, Product Update, Weekly Digest"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Email Type</Label>
                <div className="grid gap-2">
                  {EMAIL_TYPES.map((type) => (
                    <div
                      key={type.id}
                      className={`flex items-start space-x-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        emailType === type.id
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50"
                      }`}
                      onClick={() => setEmailType(type.id)}
                    >
                      <div
                        className={`mt-0.5 h-4 w-4 rounded-full border-2 flex items-center justify-center ${
                          emailType === type.id
                            ? "border-primary"
                            : "border-muted-foreground/30"
                        }`}
                      >
                        {emailType === type.id && (
                          <div className="h-2 w-2 rounded-full bg-primary" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{type.label}</p>
                        <p className="text-sm text-muted-foreground">
                          {type.description}
                        </p>
                      </div>
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
                Configure how the email is generated
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
                    <SelectItem value="none">No reference</SelectItem>
                    {references.map((ref) => (
                      <SelectItem key={ref.id} value={ref.id}>
                        {ref.name} ({ref.page_count} pages)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Using a reference will align content themes with your campaign messaging.
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

              <div className="pt-4 border-t">
                <h4 className="text-sm font-medium mb-2">Output includes:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>- Ready-to-use HTML email</li>
                  <li>- MJML source for customization</li>
                  <li>- Plain text version</li>
                  <li>- Subject line and preview text</li>
                </ul>
              </div>
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
              Generate Email Template
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
