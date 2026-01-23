"use client";

import type { ColorValue, BrandColors } from "@/types";
import { cn } from "@/lib/utils";

interface TokenPaletteProps {
  colors: BrandColors;
}

function ColorSwatch({
  color,
  label,
  large = false,
}: {
  color: ColorValue;
  label?: string;
  large?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div
        className={cn(
          "rounded border shadow-sm",
          large ? "h-16 w-full" : "h-10 w-10"
        )}
        style={{ backgroundColor: color.hex }}
        title={`${color.hex}${color.name ? ` (${color.name})` : ""}`}
      />
      <div className="text-xs">
        {label && <span className="text-muted-foreground">{label}</span>}
        <span className="font-mono block">{color.hex}</span>
        {color.name && (
          <span className="text-muted-foreground block">{color.name}</span>
        )}
      </div>
    </div>
  );
}

export function TokenPalette({ colors }: TokenPaletteProps) {
  return (
    <div className="space-y-6">
      {/* Primary */}
      <div>
        <h4 className="text-sm font-medium mb-2">Primary</h4>
        <ColorSwatch color={colors.primary} large />
      </div>

      {/* Secondary */}
      {colors.secondary.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2">Secondary</h4>
          <div className="flex gap-3 flex-wrap">
            {colors.secondary.map((color, i) => (
              <ColorSwatch key={i} color={color} />
            ))}
          </div>
        </div>
      )}

      {/* Neutrals */}
      {colors.neutrals.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2">Neutrals</h4>
          <div className="flex gap-3 flex-wrap">
            {colors.neutrals.map((color, i) => (
              <ColorSwatch key={i} color={color} />
            ))}
          </div>
        </div>
      )}

      {/* Accent */}
      {colors.accent && (
        <div>
          <h4 className="text-sm font-medium mb-2">Accent</h4>
          <ColorSwatch color={colors.accent} />
        </div>
      )}
    </div>
  );
}
