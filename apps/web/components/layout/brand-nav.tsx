"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Upload,
  Palette,
  Image,
  Sparkles,
  FileOutput,
  Users,
  Layers,
} from "lucide-react";

const navItems = [
  { href: "overview", label: "Overview", icon: LayoutDashboard },
  { href: "uploads", label: "Uploads & Jobs", icon: Upload },
  { href: "profiles", label: "Brand Profiles", icon: Palette },
  { href: "themes", label: "Themes", icon: Layers },
  { href: "generate", label: "Generate", icon: Sparkles },
  { href: "outputs", label: "Outputs", icon: FileOutput },
  { href: "team", label: "Team", icon: Users },
];

export function BrandNav() {
  const params = useParams();
  const pathname = usePathname();
  const brandId = params.brandId as string;

  return (
    <nav className="flex space-x-1 border-b px-6 overflow-x-auto">
      {navItems.map((item) => {
        const href = `/brands/${brandId}/${item.href}`;
        const isActive = pathname.startsWith(href);
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
  );
}
