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
export type JobType =
  | "analyze"
  | "analyze_upload"
  | "generate_website"
  | "generate_newsletter"
  | "scrape_reference"
  | "generate_landing_page"
  | "generate_social_media"
  | "generate_email";

export interface JobLog {
  timestamp: string;
  level: string;
  message: string;
}

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
  logs?: JobLog[] | string | null;
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

// Reference types
export type ReferenceStatus = "pending" | "scraping" | "analyzing" | "completed" | "failed";

export interface Reference {
  id: string;
  brand_id: string;
  name: string;
  description: string | null;
  urls: string[];
  status: ReferenceStatus;
  error_message: string | null;
  page_count: number | null;
  total_word_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface ReferenceDetail extends Reference {
  structure: ReferenceStructure | null;
  scraped_data: ScrapedData | null;
}

export interface ScrapedSection {
  section_type: string;
  heading: string | null;
  subheading: string | null;
  content: string[];
  cta_text: string | null;
  images: string[];
  items: Record<string, any>[];
  order: number;
}

export interface ScrapedPage {
  url: string;
  title: string;
  meta_description: string | null;
  sections: ScrapedSection[];
  navigation: { text: string; url: string }[];
  word_count: number;
}

export interface ScrapedData {
  pages: ScrapedPage[];
}

export interface ReferenceStructure {
  common_sections: string[];
  section_order_pattern: string[];
  key_messaging: string[];
  navigation_structure: { text: string; url: string }[];
  content_themes: string[];
  cta_patterns: string[];
  total_word_count: number;
}

// New generation request types
export interface LandingPageGenerateRequest {
  topic: string;
  sections?: string[];
  reference_id?: string;
  profile_version?: number;
}

export type SocialMediaPlatform = "twitter" | "linkedin" | "instagram" | "facebook";

export interface SocialMediaGenerateRequest {
  topic: string;
  platforms: SocialMediaPlatform[];
  reference_id?: string;
  profile_version?: number;
}

export type EmailType = "newsletter" | "promotional" | "announcement" | "welcome" | "followup";

export interface EmailGenerateRequest {
  topic: string;
  email_type: EmailType;
  reference_id?: string;
  profile_version?: number;
}

// Theme types
export type ThemeStatus = "draft" | "ready" | "generating" | "completed";
export type AssetType =
  | "website"
  | "landing_page"
  | "newsletter"
  | "flyer"
  | "brochure"
  | "teaser_script"
  | "social_media"
  | "presentation"
  | "banner_ads";
export type AssetStatus = "pending" | "generating" | "completed" | "failed";

export interface Theme {
  id: string;
  brand_id: string;
  created_by: string;
  name: string;
  slug: string;
  description: string | null;
  status: ThemeStatus;
  context: Record<string, any> | null;
  asset_config: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface ThemeListItem {
  id: string;
  brand_id: string;
  name: string;
  slug: string;
  description: string | null;
  status: ThemeStatus;
  document_count: number;
  asset_count: number;
  created_at: string;
  updated_at: string;
}

export interface ThemeDocument {
  id: string;
  theme_id: string;
  uploaded_by: string;
  name: string;
  original_filename: string;
  document_type: string;
  file_type: string;
  file_size: number;
  status: string;
  extracted_text: string | null;
  summary: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface ThemeAsset {
  id: string;
  theme_id: string;
  job_id: string | null;
  asset_type: AssetType;
  name: string;
  status: AssetStatus;
  storage_path: string | null;
  preview_path: string | null;
  file_size: number | null;
  content_type: string | null;
  print_pdf_path: string | null;
  figma_file_key: string | null;
  variants: Record<string, any> | null;
  metadata: Record<string, any> | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ThemeJob {
  id: string;
  theme_id: string;
  created_by: string;
  status: string;
  total_assets: number;
  completed_assets: number;
  failed_assets: number;
  progress: number;
  asset_job_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface ThemeCreateRequest {
  name: string;
  slug?: string;
  description?: string;
  context?: Record<string, any>;
  asset_config?: Record<string, any>;
}

export interface ThemeUpdateRequest {
  name?: string;
  slug?: string;
  description?: string;
  status?: ThemeStatus;
  context?: Record<string, any>;
  asset_config?: Record<string, any>;
}

export interface GenerateAllAssetsRequest {
  asset_types: AssetType[];
  profile_version?: number;
}

export interface GenerateSingleAssetRequest {
  profile_version?: number;
  params?: Record<string, any>;
}

export interface RegenerateAssetRequest {
  profile_version?: number;
  params?: Record<string, any>;
}
