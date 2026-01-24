"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
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
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/use-auth";
import * as api from "@/lib/api";

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
  const { token } = useAuth();
  const [activeJobs, setActiveJobs] = useState(0);

  useEffect(() => {
    if (!token || !brandId) return;

    let alive = true;
    const fetchJobs = async () => {
      try {
        const jobs = await api.getJobs(token, brandId);
        if (!alive) return;
        const count = jobs.filter((job) =>
          ["pending", "queued", "running"].includes(job.status)
        ).length;
        setActiveJobs(count);
      } catch {
        if (alive) setActiveJobs(0);
      }
    };

    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => {
      alive = false;
      clearInterval(interval);
    };
  }, [token, brandId]);

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
            <span className="flex items-center gap-2">
              {item.label}
              {item.href === "uploads" && activeJobs > 0 && (
                <Badge variant="secondary" className="h-5 px-1.5">
                  {activeJobs}
                </Badge>
              )}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
