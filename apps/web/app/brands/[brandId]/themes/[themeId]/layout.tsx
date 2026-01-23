"use client";

import { ReactNode } from "react";
import { useParams, usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { ThemeProvider, useTheme } from "./theme-context";
import { LayoutDashboard, FileText, Sparkles, Image, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

const themeNavItems = [
  { href: "", label: "Overview", icon: LayoutDashboard },
  { href: "/context", label: "Documents", icon: FileText },
  { href: "/generate", label: "Generate", icon: Sparkles },
  { href: "/assets", label: "Assets", icon: Image },
];

function ThemeLayoutContent({ children }: { children: ReactNode }) {
  const params = useParams();
  const pathname = usePathname();
  const brandId = params.brandId as string;
  const themeId = params.themeId as string;
  const { theme, loading, error } = useTheme();

  const basePath = `/brands/${brandId}/themes/${themeId}`;

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-64 bg-muted rounded" />
          <div className="h-10 w-full bg-muted rounded" />
          <div className="h-96 bg-muted rounded-lg" />
        </div>
      </div>
    );
  }

  if (error || !theme) {
    return (
      <div className="p-6">
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          {error || "Theme not found"}
        </div>
        <Link href={`/brands/${brandId}/themes`}>
          <Button variant="outline" className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Themes
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      {/* Theme Header */}
      <div className="border-b bg-muted/30 px-6 py-4">
        <div className="flex items-center gap-4">
          <Link href={`/brands/${brandId}/themes`}>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-xl font-semibold">{theme.name}</h1>
            {theme.description && (
              <p className="text-sm text-muted-foreground">{theme.description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Theme Navigation */}
      <nav className="flex space-x-1 border-b px-6 overflow-x-auto">
        {themeNavItems.map((item) => {
          const href = `${basePath}${item.href}`;
          const isActive = item.href === ""
            ? pathname === basePath
            : pathname.startsWith(href);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={href}
              className={cn(
                "flex items-center gap-2 px-3 py-2 text-sm font-medium transition-colors hover:text-primary border-b-2 -mb-[2px]",
                isActive
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Page Content */}
      <div>{children}</div>
    </div>
  );
}

export default function ThemeLayout({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <ThemeLayoutContent>{children}</ThemeLayoutContent>
    </ThemeProvider>
  );
}
