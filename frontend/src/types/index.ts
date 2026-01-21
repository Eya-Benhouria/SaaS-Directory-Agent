// API Types

export type SubmissionStatus = 
  | 'pending' 
  | 'in_progress' 
  | 'submitted' 
  | 'approved' 
  | 'rejected' 
  | 'failed' 
  | 'requires_review';

export type DirectoryStatus = 'active' | 'inactive' | 'blocked' | 'needs_update';

export interface SaaSProduct {
  id: number;
  name: string;
  website_url: string;
  tagline?: string;
  short_description?: string;
  long_description?: string;
  category?: string;
  subcategory?: string;
  tags: string[];
  contact_email: string;
  contact_name?: string;
  twitter_url?: string;
  linkedin_url?: string;
  github_url?: string;
  logo_path?: string;
  screenshot_paths: string[];
  pricing_model?: string;
  pricing_details?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SaaSProductWithStats extends SaaSProduct {
  total_submissions: number;
  pending_count: number;
  submitted_count: number;
  approved_count: number;
  failed_count: number;
}

export interface SaaSProductCreate {
  name: string;
  website_url: string;
  tagline?: string;
  short_description?: string;
  long_description?: string;
  category?: string;
  subcategory?: string;
  tags?: string[];
  contact_email: string;
  contact_name?: string;
  twitter_url?: string;
  linkedin_url?: string;
  github_url?: string;
  pricing_model?: string;
  pricing_details?: string;
}

export interface Directory {
  id: number;
  name: string;
  url: string;
  submission_url?: string;
  category?: string;
  domain_authority?: number;
  monthly_traffic?: number;
  requires_account: boolean;
  requires_approval: boolean;
  requires_payment: boolean;
  status: DirectoryStatus;
  form_schema?: object;
  last_checked_at?: string;
  success_rate: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DirectoryCreate {
  name: string;
  url: string;
  submission_url?: string;
  category?: string;
  domain_authority?: number;
  monthly_traffic?: number;
  requires_account?: boolean;
  requires_approval?: boolean;
  requires_payment?: boolean;
  notes?: string;
}

export interface Submission {
  id: number;
  saas_product_id: number;
  directory_id: number;
  status: SubmissionStatus;
  submitted_at?: string;
  approved_at?: string;
  listing_url?: string;
  attempt_count: number;
  max_attempts: number;
  last_attempt_at?: string;
  error_message?: string;
  screenshot_path?: string;
  detected_fields?: object;
  filled_fields?: object;
  created_at: string;
  updated_at: string;
}

export interface SubmissionWithDetails extends Submission {
  saas_product: SaaSProduct;
  directory: Directory;
}

export interface DashboardStats {
  total_products: number;
  total_directories: number;
  total_submissions: number;
  pending_submissions: number;
  in_progress_submissions: number;
  submitted_submissions: number;
  approved_submissions: number;
  failed_submissions: number;
  success_rate: number;
  submissions_today: number;
  submissions_this_week: number;
}

export interface SubmissionTrend {
  date: string;
  submitted: number;
  approved: number;
  failed: number;
}

export interface ActivityLog {
  id: number;
  action: string;
  entity_type?: string;
  entity_id?: number;
  message?: string;
  level: string;
  created_at: string;
}
