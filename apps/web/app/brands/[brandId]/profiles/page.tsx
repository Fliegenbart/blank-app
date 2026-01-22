"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Palette, Clock, ArrowRight, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useBrand } from "../layout";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import * as api from "@/lib/api";
import type { BrandProfile } from "@/types";
import { formatDate } from "@/lib/utils";

export default function ProfilesPage() {
  const { brand } = useBrand();
  const { token } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  const [profiles, setProfiles] = useState<BrandProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token || !brand) return;

    api
      .getProfiles(token, brand.id)
      .then(setProfiles)
      .catch((err) => {
        toast({
          title: "Error loading profiles",
          description: err instanceof Error ? err.message : "Unknown error",
          variant: "destructive",
        });
      })
      .finally(() => setIsLoading(false));
  }, [token, brand, toast]);

  if (!brand) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Brand Profiles</h1>
        <p className="text-muted-foreground">
          View and compare versions of your brand profile
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : profiles.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Palette className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-4 text-center">
              No brand profiles yet. Upload and analyze a document to create your first profile.
            </p>
            <Button onClick={() => router.push(`/brands/${brand.id}/uploads`)}>
              Go to Uploads
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {profiles.map((profile, index) => (
            <Card
              key={profile.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push(`/brands/${brand.id}/profiles/${profile.version}`)}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
                      <span className="text-lg font-bold text-primary">
                        v{profile.version}
                      </span>
                    </div>
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        Version {profile.version}
                        {index === 0 && (
                          <Badge variant="default">Latest</Badge>
                        )}
                      </CardTitle>
                      <CardDescription className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDate(profile.created_at)}
                      </CardDescription>
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4 text-sm">
                  {profile.tokens?.colors && (
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Colors:</span>
                      <div className="flex gap-1">
                        {profile.tokens.colors.primary && (
                          <div
                            className="w-4 h-4 rounded border"
                            style={{ backgroundColor: profile.tokens.colors.primary }}
                            title={profile.tokens.colors.primary}
                          />
                        )}
                        {profile.tokens.colors.secondary && (
                          <div
                            className="w-4 h-4 rounded border"
                            style={{ backgroundColor: profile.tokens.colors.secondary }}
                            title={profile.tokens.colors.secondary}
                          />
                        )}
                        {profile.tokens.colors.accent && (
                          <div
                            className="w-4 h-4 rounded border"
                            style={{ backgroundColor: profile.tokens.colors.accent }}
                            title={profile.tokens.colors.accent}
                          />
                        )}
                      </div>
                    </div>
                  )}
                  {profile.tokens?.typography?.primary_font && (
                    <div>
                      <span className="text-muted-foreground">Font:</span>{" "}
                      {profile.tokens.typography.primary_font}
                    </div>
                  )}
                  {profile.tone?.voice && (
                    <div>
                      <span className="text-muted-foreground">Voice:</span>{" "}
                      {profile.tone.voice}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
