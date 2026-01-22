export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  organization_id: string;
  created_at: string;
  updated_at: string;
  members?: BrandMember[];
}

export type BrandRole = "owner" | "editor" | "viewer";

export interface BrandMember {
  id: string;
  user_id: string;
  email: string;
  full_name: string | null;
  role: BrandRole;
  created_at: string;
}

export interface Upload {
  id: string;
  brand_id: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: string;
  created_at: string;
}

export type JobStatus = "pending" | "queued" | "running" | "completed" | "failed";
export type JobType = "analyze" | "generate_website" | "generate_newsletter";

export interface Job {
  id: string;
  brand_id: string;
  job_type: JobType;
  status: JobStatus;
  progress: number;
  created_at: string;
  updated_at: string;
  error_message: string | null;
  logs: string | null;
  output_id: string | null;
  result: Record<string, any> | null;
}

export interface ColorValue {
  hex: string;
  name: string | null;
  usage: string | null;
}

export interface BrandColors {
  primary: ColorValue;
  secondary: ColorValue[];
  neutrals: ColorValue[];
  accent: ColorValue | null;
}

export interface FontScale {
  h1: string;
  h2: string;
  h3?: string;
  body: string;
  caption: string;
}

export interface BrandTypography {
  heading_font: string;
  body_font: string;
  scale: FontScale;
  weights: Record<string, number>;
}

export interface Margins {
  top: string;
  right: string;
  bottom: string;
  left: string;
}

export interface LayoutSystem {
  margins: Margins;
  grid_unit: string;
  max_width: string;
  columns: number;
}

export interface BrandImagery {
  photo_vs_illustration: string;
  motifs: string[];
  mood: string[];
  style_notes: string | null;
}

export interface ToneOfVoice {
  attributes: string[];
  do: string[];
  dont: string[];
  example_phrases: string[];
}

export interface ConfidenceScores {
  colors: number;
  typography: number;
  layout: number;
  imagery: number;
  tone: number;
}

export interface BrandIdentity {
  name: string;
  sources: string[];
}

export interface BrandProfileData {
  identity: BrandIdentity;
  colors: BrandColors;
  typography: BrandTypography;
  layout_system: LayoutSystem;
  imagery: BrandImagery;
  tone_of_voice: ToneOfVoice;
  confidence: ConfidenceScores;
}

export interface BrandProfile {
  id: string;
  brand_id: string;
  version: number;
  profile: BrandProfileData;
  summary_md: string | null;
  source_upload_id: string | null;
  created_at: string;
}

export interface Output {
  id: string;
  brand_id: string;
  output_type: string;
  name: string;
  description: string | null;
  file_size: number | null;
  content_type: string | null;
  created_at: string;
  download_url: string | null;
  metadata: Record<string, any> | null;
}

export interface PageConfig {
  slug: string;
  title: string;
  description?: string;
  sections?: string[];
}

export interface WebsiteGenerateRequest {
  topic: string;
  pages: PageConfig[];
  brief?: string;
  profile_version?: number;
}

export interface NewsletterGenerateRequest {
  topic: string;
  offer?: string;
  cta: string;
  subject_line?: string;
  preview_text?: string;
  profile_version?: number;
}
