"use client";

import { useRouter } from "next/navigation";
import { Globe, Mail, FileOutput, ArrowRight, Sparkles } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useBrand } from "../layout";

const generators = [
  {
    id: "website",
    title: "Website",
    description: "Generate a branded landing page with HTML, CSS, and assets",
    icon: Globe,
    href: "/generate/website",
    badge: "Popular",
  },
  {
    id: "newsletter",
    title: "Newsletter",
    description: "Create email-ready newsletter templates in HTML and MJML",
    icon: Mail,
    href: "/generate/newsletter",
    badge: null,
  },
];

export default function GeneratePage() {
  const { brand, userRole } = useBrand();
  const router = useRouter();

  const canEdit = userRole === "owner" || userRole === "editor";

  if (!brand) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Sparkles className="h-8 w-8" />
          Generate Content
        </h1>
        <p className="text-muted-foreground">
          Use your brand profile to generate on-brand content
        </p>
      </div>

      {!canEdit && (
        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="pt-6">
            <p className="text-sm text-yellow-600 dark:text-yellow-400">
              You have viewer access to this brand. Contact an owner or editor to generate content.
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {generators.map((generator) => (
          <Card
            key={generator.id}
            className={`relative ${canEdit ? "cursor-pointer hover:shadow-lg transition-shadow" : "opacity-60"}`}
            onClick={() => canEdit && router.push(`/brands/${brand.id}${generator.href}`)}
          >
            {generator.badge && (
              <Badge className="absolute top-4 right-4" variant="secondary">
                {generator.badge}
              </Badge>
            )}
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
                  <generator.icon className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle>{generator.title}</CardTitle>
                  <CardDescription>{generator.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full"
                disabled={!canEdit}
                onClick={(e) => {
                  e.stopPropagation();
                  router.push(`/brands/${brand.id}${generator.href}`);
                }}
              >
                Generate {generator.title}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Outputs Quick Link */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileOutput className="h-5 w-5" />
            Recent Outputs
          </CardTitle>
          <CardDescription>
            View and download your generated content
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            onClick={() => router.push(`/brands/${brand.id}/outputs`)}
          >
            View All Outputs
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
