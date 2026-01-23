"use client";

import { Progress } from "@/components/ui/progress";
import type { ConfidenceScores } from "@/types";

interface ProfileConfidenceProps {
  confidence: ConfidenceScores;
}

export function ProfileConfidence({ confidence }: ProfileConfidenceProps) {
  const items = [
    { key: "colors", label: "Colors", value: confidence.colors },
    { key: "typography", label: "Typography", value: confidence.typography },
    { key: "layout", label: "Layout", value: confidence.layout },
    { key: "imagery", label: "Imagery", value: confidence.imagery },
    { key: "tone", label: "Tone", value: confidence.tone },
  ];

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium">Analysis Confidence</h4>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.key} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">{item.label}</span>
              <span className="font-medium">{Math.round(item.value * 100)}%</span>
            </div>
            <Progress value={item.value * 100} className="h-2" />
          </div>
        ))}
      </div>
    </div>
  );
}
