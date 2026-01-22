"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface UploadDropzoneProps {
  onUpload: (file: File) => Promise<void>;
  accept?: Record<string, string[]>;
  maxSize?: number;
  disabled?: boolean;
}

export function UploadDropzone({
  onUpload,
  accept = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
    "application/vnd.ms-powerpoint": [".ppt"],
  },
  maxSize = 100 * 1024 * 1024, // 100MB
  disabled = false,
}: UploadDropzoneProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setIsUploading(true);
      setError(null);

      try {
        await onUpload(file);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setIsUploading(false);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize,
    maxFiles: 1,
    disabled: disabled || isUploading,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
        isDragActive && "border-primary bg-primary/5",
        isDragReject && "border-destructive bg-destructive/5",
        (disabled || isUploading) && "opacity-50 cursor-not-allowed",
        !isDragActive && !isDragReject && "border-muted-foreground/25 hover:border-primary/50"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-2">
        {isUploading ? (
          <>
            <Loader2 className="h-10 w-10 text-muted-foreground animate-spin" />
            <p className="text-sm text-muted-foreground">Uploading...</p>
          </>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <Upload className="h-10 w-10 text-muted-foreground" />
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
            <div>
              <p className="text-sm font-medium">
                {isDragActive ? "Drop the file here" : "Drag & drop a file here"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                or click to select a file (PDF, PPTX)
              </p>
            </div>
          </>
        )}
        {error && <p className="text-sm text-destructive mt-2">{error}</p>}
      </div>
    </div>
  );
}
