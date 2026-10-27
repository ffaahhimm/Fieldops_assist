/** Shared TypeScript types matching backend Pydantic schemas. */

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Customer {
  id: number;
  code: string;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
}

export interface Site {
  id: number;
  customer_id: number;
  name: string;
  address?: string;
  contact_name?: string;
  contact_phone?: string;
  notes?: string;
  created_at: string;
}

export interface Asset {
  id: number;
  asset_tag: string;
  name: string;
  category: string;
  asset_type?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  ip_address?: string;
  customer_id: number;
  site_id?: number;
  installation_date?: string;
  warranty_expiry?: string;
  last_service_date?: string;
  next_maintenance_date?: string;
  status: 'operational' | 'degraded' | 'offline' | 'retired' | 'unknown';
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ServiceTicket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  customer_id: number;
  site_id?: number;
  asset_id?: number;
  category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'assigned' | 'in_progress' | 'waiting_customer' | 'resolved' | 'closed';
  technician_id?: number;
  response_due?: string;
  resolution_notes?: string;
  closed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface TicketEvent {
  id: number;
  ticket_id: number;
  actor_name: string;
  event_type: string;
  detail?: string;
  created_at: string;
}

export interface Technician {
  id: number;
  user_id?: number;
  employee_id: string;
  phone?: string;
  is_available: boolean;
  notes?: string;
  created_at: string;
}

export interface AMCContract {
  id: number;
  contract_number: string;
  customer_id: number;
  start_date: string;
  end_date: string;
  status: string;
  maintenance_frequency_days: number;
  notes?: string;
  created_at: string;
}

export interface MaintenanceVisit {
  id: number;
  contract_id?: number;
  customer_id: number;
  site_id?: number;
  asset_id?: number;
  technician_id?: number;
  scheduled_date: string;
  maintenance_type: string;
  status: string;
  checklist?: string;
  findings?: string;
  work_performed?: string;
  completed_at?: string;
  notes?: string;
  created_at: string;
}

export interface KnowledgeDocument {
  id: number;
  title: string;
  category: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  status: 'pending' | 'indexed' | 'failed';
  error_message?: string;
  chunk_count: number;
  uploaded_at: string;
  indexed_at?: string;
}

export interface DashboardMetrics {
  total_assets: number;
  assets_with_issue: number;
  open_tickets: number;
  critical_tickets: number;
  overdue_tickets: number;
  expiring_contracts: number;
  upcoming_maintenance: number;
  overdue_maintenance: number;
  recent_tickets: Array<{
    id: number;
    ticket_number: string;
    title: string;
    status: string;
    priority: string;
    updated_at: string;
  }>;
  status_breakdown: Record<string, number>;
  priority_breakdown: Record<string, number>;
  note: string;
}

export interface AssistantSource {
  document_id: number;
  document_title: string;
  chunk_index: number;
  excerpt: string;
}

export interface AssistantResponse {
  answer: string;
  sources: AssistantSource[];
  retrieval_only: boolean;
  llm_available: boolean;
}
