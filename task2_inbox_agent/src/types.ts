/**
 * Strict TypeScript Types for Task 2: The Inbox Agent.
 */

export type EmailCategory = 
  | 'Filters'
  | 'Home Page'
  | 'Domain Management'
  | 'Header'
  | 'Main Menu'
  | 'Footer'
  | 'General Settings'
  | 'Design Settings'
  | 'Managers'
  | 'how_to' 
  | 'new_project' 
  | 'refund' 
  | 'complaint' 
  | 'quote' 
  | 'follow_up';

export type UrgencyLevel = 'low' | 'medium' | 'high';

export type EmailFolder = 'inbox' | 'drafts' | 'sent' | 'spam' | 'trash' | 'starred' | 'auto_sent';

export type EmailStatus = 
  | 'unread' 
  | 'drafted' 
  | 'approved' 
  | 'edited_and_sent' 
  | 'custom_sent' 
  | 'auto_sent';

export interface KBArticleCitation {
  article_id: string;
  title: string;
  url: string;
  category: string;
  folder: string;
  snippet: string;
  score: number;
}

export interface CustomerEmail {
  id: string;
  customer_name: string;
  customer_email: string;
  company_name: string;
  category: EmailCategory;
  label_name?: string;
  parent_setting_type?: string;
  subject: string;
  body: string;
  urgency: UrgencyLevel;
  date: string;
  status: EmailStatus;
  drafted_reply?: string;
  final_sent_reply?: string;
  confidence: number;
  citations: KBArticleCitation[];
  edit_distance?: number;
  similarity_ratio?: number;
  auto_sent: boolean;
  handled_at?: string;
}

export interface ClassificationResult {
  category: EmailCategory;
  label_name: string;
  parent_setting_type: string;
  confidence: number;
  intent_summary: string;
  urgency: UrgencyLevel;
}

export interface DraftResult {
  draft: string;
  confidence: number;
  reasoning: string;
  citations: KBArticleCitation[];
  matched_rules: string[];
  prompt_version: string;
}

export interface HumanFeedback {
  id: string;
  email_id: string;
  category: EmailCategory;
  subject: string;
  original_draft: string;
  edited_reply: string;
  edit_distance: number;
  similarity_ratio: number;
  learned_rule: string;
  created_at: string;
  active: boolean;
}

export interface GraduationState {
  category: EmailCategory;
  category_label: string;
  confidence_score: number; // Per-category confidence score (0.0 to 1.0)
  consecutive_unchanged: number;
  threshold: number; // Configurable threshold X
  total_approved: number;
  total_auto_sent: number;
  auto_send_eligible: boolean;
  status: 'HUMAN_REVIEW_REQUIRED' | 'AUTO_SEND_ELIGIBLE';
  last_demotion_reason?: string;
  last_updated: string;
}

export interface LearningMetrics {
  total_feedback_events: number;
  initial_avg_similarity: number;
  current_avg_similarity: number;
  improvement_percentage: number;
  active_rules_count: number;
}

export interface GmailConfig {
  mode: 'demo' | 'live';
  gmail_address: string;
  auth_type: 'app_password' | 'oauth';
  app_password?: string;
  client_id?: string;
  client_secret?: string;
  imap_host: string;
  smtp_host: string;
  is_connected: boolean;
  last_sync: string;
}
