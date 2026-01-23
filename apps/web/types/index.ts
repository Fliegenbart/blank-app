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
  email?: string;
  full_name?: string | null;
  role: BrandRole;
  created_at: string;
  user?: {
    id: string;
    email: string;
    full_name?: string;
  };
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
export type JobType = "analyze" | "analyze_upload" | "generate_website" | "generate_newsletter";

export interface Job {
  id: string;
  brand_id: string;
  job_type: JobType;
  status: JobStatus;
  progress: number;
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
  error_message: string | null;
  logs: { timestamp: string; level: string; message: string }[];
  output_id: string | null;
  result?: {
    profile_version?: number;
    output_id?: string;
    [key: string]: unknown;
  } | null;
  input_data?: {
    upload_id?: string;
    filename?: string;
    [key: string]: unknown;
  };
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

export interface BrandImageryExtended {
  style?: string;
  subjects?: string[];
  mood?: string;
  treatments?: string[];
  photo_vs_illustration?: string;
  motifs?: string[];
  style_notes?: string | null;
}

export interface BrandTokens {
  colors?: BrandColors;
  typography?: {
    primary_font?: string;
    secondary_font?: string;
    heading_style?: string;
    body_style?: string;
  };
  spacing?: {
    base_unit?: string;
    scale?: string;
    grid_columns?: number;
  };
}

export interface BrandProfile {
  id: string;
  brand_id: string;
  version: number;
  profile?: BrandProfileData;
  summary_md: string | null;
  source_upload_id: string | null;
  created_at: string;
  // Flattened properties from BrandProfileData
  identity?: BrandIdentity;
  colors?: BrandColors;
  typography?: BrandTypography;
  layout_system?: LayoutSystem;
  imagery?: BrandImageryExtended;
  tone_of_voice?: ToneOfVoice;
  confidence?: ConfidenceScores;
  tokens?: BrandTokens;
  tone?: {
    voice?: string;
    personality?: string[];
    dos?: string[];
    donts?: string[];
    examples?: string[];
  };
  evidence?: Record<string, unknown>;
}

export interface Output {
  id: string;
  brand_id: string;
  output_type: string;
  name: string;
  filename: string;
  description: string | null;
  file_size: number;
  content_type: string;
  profile_version: number;
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
  profile_version?: number;
  page_title?: string;
  headline?: string;
  subheadline?: string;
  cta_text?: string;
  cta_url?: string;
  sections?: string[];
  additional_notes?: string;
}

export interface NewsletterGenerateRequest {
  profile_version?: number;
  subject?: string;
  preheader?: string;
  headline?: string;
  body_content?: string;
  cta_text?: string;
  cta_url?: string;
  footer_text?: string;
}
