// API service for connecting to Python backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export interface ApiLead {
  id: string;
  lead_name: string;
  company_name: string;
  contact_info: {
    phone: string;
    email: string;
    whatsapp: string;
  };
  requirement: {
    type: string;
    capacity: string;
    platform_length: string;
    installation_type: string;
    location: string;
    timeline: string;
    decision_maker?: string;
  };
  call_metadata: {
    timestamp: string;
    call_outcome: "qualified" | "not_interested" | "reschedule" | "wrong_contact";
    duration_seconds: number;
    audio_recording_id: string | null;
  };
  conversation_transcript: string;
  scheduled_call: {
    preferred_day: string;
    preferred_time: string;
    alternate_time: string;
    contact_mode?: string;
  };
  status: string;
}

export interface ApiMetrics {
  totalCalls: number;
  successRate: number;
  todaysCalls: number;
}

export interface LeadsQueryParams {
  date_range?: '7days' | '30days' | 'all';
  status?: 'qualified' | 'not_interested' | 'reschedule' | 'wrong_contact' | 'all';
  search?: string;
  sort?: 'newest' | 'oldest' | 'name';
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async fetchLeads(params: LeadsQueryParams = {}): Promise<ApiLead[]> {
    const queryString = new URLSearchParams(
      Object.entries(params).filter(([_, v]) => v != null) as [string, string][]
    ).toString();

    const url = `${this.baseUrl}/leads${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch leads: ${response.statusText}`);
    }
    
    return response.json();
  }

  async fetchLeadById(id: string): Promise<ApiLead> {
    const response = await fetch(`${this.baseUrl}/leads/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch lead: ${response.statusText}`);
    }
    
    return response.json();
  }

  async fetchMetrics(dateRange: '7days' | '30days' | 'all' = 'all'): Promise<ApiMetrics> {
    const url = `${this.baseUrl}/metrics?date_range=${dateRange}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch metrics: ${response.statusText}`);
    }
    
    return response.json();
  }

  getAudioUrl(recordingId: string | null): string | null {
    if (!recordingId || recordingId === 'null') {
      return null;
    }
    return `${this.baseUrl}/audio/${recordingId}`;
  }

  getTranscriptExportUrl(leadId: string): string {
    return `${this.baseUrl}/export/transcript/${leadId}`;
  }

  async checkHealth(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('API health check failed');
    }
    return response.json();
  }
}

export const apiService = new ApiService();
