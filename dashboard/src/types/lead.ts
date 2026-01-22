export interface Lead {
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
    decision_maker: string;
  };
  call_metadata: {
    timestamp: string;
    call_outcome: "qualified" | "qualified_scheduled" | "not_interested" | "reschedule" | "wrong_contact" | "do_not_call";
    duration_seconds: number;
    audio_recording_url: string;
  };
  conversation_transcript: string;
  scheduled_call: {
    preferred_day: string;
    preferred_time: string;
    alternate_time: string;
    contact_mode: string;
  };
  status: string;
}

export type CallOutcome = Lead["call_metadata"]["call_outcome"];
