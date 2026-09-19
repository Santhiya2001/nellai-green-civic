export type Role = "CITIZEN" | "VOLUNTEER" | "AUTHORITY" | "ADMIN" | "SUPER_ADMIN" | "MODULE_DEVELOPER";

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  roles: Role[];
  is_active: boolean;
  is_verified: boolean;
}

export interface Category {
  id: string;
  code: string;
  name: string;
  module_id: string;
  default_severity: string;
  icon: string;
}

export interface Complaint {
  id: string;
  complaint_number: string;
  user_id: string;
  category: Category;
  description: string;
  image_url: string | null;
  latitude: number;
  longitude: number;
  address_text: string | null;
  severity: string;
  ai_category_code: string | null;
  ai_confidence: number | null;
  ai_severity: string | null;
  status: string;
  assigned_authority_id: string | null;
  deadline_at: string | null;
  escalation_level: number;
  duplicate_of_id: string | null;
  rejection_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface ComplaintListItem {
  id: string;
  complaint_number: string;
  category_code: string;
  description: string;
  severity: string;
  status: string;
  latitude: number;
  longitude: number;
  created_at: string;
  deadline_at: string | null;
}

export interface NotificationItem {
  id: string;
  title: string;
  body: string;
  type: string;
  is_read: boolean;
  related_complaint_id: string | null;
  created_at: string;
}

export interface DashboardSummary {
  total_complaints: number;
  open_complaints: number;
  resolved_complaints: number;
  overdue_complaints: number;
  escalated_complaints: number;
  high_severity_open: number;
}
