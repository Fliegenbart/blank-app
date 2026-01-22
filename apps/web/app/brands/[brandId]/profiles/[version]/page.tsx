"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Download, Loader2, FileText, Palette, Type, Image, MessageSquare, FileSearch } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { useBrand } from "../../layout";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { TokenPalette } from "@/components/profile/token-palette";
import { ProfileConfidence } from "@/components/profile/profile-confidence";
import { MarkdownViewer } from "@/components/profile/markdown-viewer";
import { JsonViewer } from "@/components/profile/json-viewer";
import * as api from "@/lib/api";
import type { BrandProfile } from "@/types";
import { formatDate } from "@/lib/utils";

export default function ProfileVersionPage() {
  const { brand } = useBrand();
  const { token } = useAuth();
  const { toast } = useToast();
  const router = useRouter();
  const params = useParams();
  const version = parseInt(params.version as string, 10);

  const [profile, setProfile] = useState<BrandProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token || !brand || isNaN(version)) return;

    api
      .getProfile(token, brand.id, version)
      .then(setProfile)
      .catch((err) => {
        toast({
          title: "Error loading profile",
          description: err instanceof Error ? err.message : "Unknown error",
          variant: "destructive",
        });
        router.push(`/brands/${brand.id}/profiles`);
      })
      .finally(() => setIsLoading(false));
  }, [token, brand, version, toast, router]);

  const handleExportJson = () => {
    if (!profile) return;
    const blob = new Blob([JSON.stringify(profile, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${brand?.slug || "brand"}-profile-v${profile.version}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!brand) return null;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Profile not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/brands/${brand.id}/profiles`}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              All Versions
            </Link>
          </Button>
          <Separator orientation="vertical" className="h-6" />
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              Brand Profile
              <Badge variant="secondary">v{profile.version}</Badge>
            </h1>
            <p className="text-sm text-muted-foreground">
              Created {formatDate(profile.created_at)}
            </p>
          </div>
        </div>
        <Button variant="outline" onClick={handleExportJson}>
          <Download className="mr-2 h-4 w-4" />
          Export JSON
        </Button>
      </div>

      {/* Confidence Overview */}
      {profile.confidence && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Confidence Scores</CardTitle>
            <CardDescription>How confident we are in each analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <ProfileConfidence confidence={profile.confidence} />
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs defaultValue="summary" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="summary" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Summary
          </TabsTrigger>
          <TabsTrigger value="tokens" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Tokens
          </TabsTrigger>
          <TabsTrigger value="imagery" className="flex items-center gap-2">
            <Image className="h-4 w-4" />
            Imagery
          </TabsTrigger>
          <TabsTrigger value="tone" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Tone
          </TabsTrigger>
          <TabsTrigger value="evidence" className="flex items-center gap-2">
            <FileSearch className="h-4 w-4" />
            Evidence
          </TabsTrigger>
        </TabsList>

        {/* Summary Tab */}
        <TabsContent value="summary">
          <Card>
            <CardHeader>
              <CardTitle>Brand Summary</CardTitle>
              <CardDescription>AI-generated overview of your brand identity</CardDescription>
            </CardHeader>
            <CardContent>
              {profile.summary_md ? (
                <MarkdownViewer content={profile.summary_md} />
              ) : (
                <p className="text-muted-foreground">No summary available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tokens Tab */}
        <TabsContent value="tokens" className="space-y-6">
          {/* Colors */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Color Palette
              </CardTitle>
              <CardDescription>Brand colors extracted from your documents</CardDescription>
            </CardHeader>
            <CardContent>
              {profile.tokens?.colors ? (
                <TokenPalette colors={profile.tokens.colors} />
              ) : (
                <p className="text-muted-foreground">No colors detected</p>
              )}
            </CardContent>
          </Card>

          {/* Typography */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Type className="h-5 w-5" />
                Typography
              </CardTitle>
              <CardDescription>Font families and styles</CardDescription>
            </CardHeader>
            <CardContent>
              {profile.tokens?.typography ? (
                <div className="grid gap-4 md:grid-cols-2">
                  {profile.tokens.typography.primary_font && (
                    <div className="p-4 border rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Primary Font</p>
                      <p
                        className="text-2xl font-semibold"
                        style={{ fontFamily: profile.tokens.typography.primary_font }}
                      >
                        {profile.tokens.typography.primary_font}
                      </p>
                    </div>
                  )}
                  {profile.tokens.typography.secondary_font && (
                    <div className="p-4 border rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Secondary Font</p>
                      <p
                        className="text-2xl"
                        style={{ fontFamily: profile.tokens.typography.secondary_font }}
                      >
                        {profile.tokens.typography.secondary_font}
                      </p>
                    </div>
                  )}
                  {profile.tokens.typography.heading_style && (
                    <div className="p-4 border rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Heading Style</p>
                      <p className="text-lg">{profile.tokens.typography.heading_style}</p>
                    </div>
                  )}
                  {profile.tokens.typography.body_style && (
                    <div className="p-4 border rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Body Style</p>
                      <p className="text-lg">{profile.tokens.typography.body_style}</p>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground">No typography detected</p>
              )}
            </CardContent>
          </Card>

          {/* Spacing & Layout */}
          {profile.tokens?.spacing && (
            <Card>
              <CardHeader>
                <CardTitle>Spacing & Layout</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  {profile.tokens.spacing.base_unit && (
                    <div className="p-4 border rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Base Unit</p>
                      <p className="text-lg font-mono">{profile.tokens.spacing.base_unit}</p>
                    </div>
                  )}
                  {profile.tokens.spacing.scale && (
                    <div className="p-4 border rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Scale</p>
                      <p className="text-lg">{profile.tokens.spacing.scale}</p>
                    </div>
                  )}
                  {profile.tokens.spacing.grid_columns && (
                    <div className="p-4 border rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Grid Columns</p>
                      <p className="text-lg">{profile.tokens.spacing.grid_columns}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Imagery Tab */}
        <TabsContent value="imagery">
          <Card>
            <CardHeader>
              <CardTitle>Imagery Guidelines</CardTitle>
              <CardDescription>Visual style preferences detected from your documents</CardDescription>
            </CardHeader>
            <CardContent>
              {profile.imagery ? (
                <div className="grid gap-6 md:grid-cols-2">
                  {profile.imagery.style && (
                    <div>
                      <h4 className="font-medium mb-2">Style</h4>
                      <p className="text-muted-foreground">{profile.imagery.style}</p>
                    </div>
                  )}
                  {profile.imagery.subjects && profile.imagery.subjects.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Common Subjects</h4>
                      <div className="flex flex-wrap gap-2">
                        {profile.imagery.subjects.map((subject, i) => (
                          <Badge key={i} variant="secondary">{subject}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {profile.imagery.mood && (
                    <div>
                      <h4 className="font-medium mb-2">Mood</h4>
                      <p className="text-muted-foreground">{profile.imagery.mood}</p>
                    </div>
                  )}
                  {profile.imagery.treatments && profile.imagery.treatments.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Treatments</h4>
                      <div className="flex flex-wrap gap-2">
                        {profile.imagery.treatments.map((treatment, i) => (
                          <Badge key={i} variant="outline">{treatment}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground">No imagery guidelines detected</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tone Tab */}
        <TabsContent value="tone">
          <Card>
            <CardHeader>
              <CardTitle>Brand Voice & Tone</CardTitle>
              <CardDescription>Communication style and personality</CardDescription>
            </CardHeader>
            <CardContent>
              {profile.tone ? (
                <div className="grid gap-6">
                  {profile.tone.voice && (
                    <div>
                      <h4 className="font-medium mb-2">Voice</h4>
                      <p className="text-lg">{profile.tone.voice}</p>
                    </div>
                  )}
                  {profile.tone.personality && profile.tone.personality.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Personality Traits</h4>
                      <div className="flex flex-wrap gap-2">
                        {profile.tone.personality.map((trait, i) => (
                          <Badge key={i} variant="secondary" className="text-base px-3 py-1">
                            {trait}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {profile.tone.dos && profile.tone.dos.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2 text-green-600">Do&apos;s</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {profile.tone.dos.map((item, i) => (
                          <li key={i} className="text-muted-foreground">{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {profile.tone.donts && profile.tone.donts.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2 text-red-600">Don&apos;ts</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {profile.tone.donts.map((item, i) => (
                          <li key={i} className="text-muted-foreground">{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {profile.tone.examples && profile.tone.examples.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Example Phrases</h4>
                      <div className="grid gap-2">
                        {profile.tone.examples.map((example, i) => (
                          <blockquote
                            key={i}
                            className="border-l-4 border-primary pl-4 italic text-muted-foreground"
                          >
                            &ldquo;{example}&rdquo;
                          </blockquote>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground">No tone analysis available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Evidence Tab */}
        <TabsContent value="evidence">
          <Card>
            <CardHeader>
              <CardTitle>Source Evidence</CardTitle>
              <CardDescription>Raw data extracted from your documents</CardDescription>
            </CardHeader>
            <CardContent>
              {profile.evidence ? (
                <JsonViewer data={profile.evidence} />
              ) : (
                <p className="text-muted-foreground">No evidence data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
