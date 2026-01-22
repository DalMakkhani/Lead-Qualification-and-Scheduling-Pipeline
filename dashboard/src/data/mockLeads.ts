import { Lead } from "@/types/lead";

export const mockLeads: Lead[] = [
  {
    id: "lead-001",
    lead_name: "Rajesh Kumar",
    company_name: "Kumar Weighing Solutions Pvt Ltd",
    contact_info: {
      phone: "+91 98765 43210",
      email: "rajesh@kumarweighing.com",
      whatsapp: "+91 98765 43210",
    },
    requirement: {
      type: "New Installation",
      capacity: "60 ton",
      platform_length: "18 meter",
      installation_type: "Pit",
      location: "Pune, Maharashtra",
      timeline: "1-3 months",
      decision_maker: "Self - Owner",
    },
    call_metadata: {
      timestamp: "2026-01-21T10:30:00Z",
      call_outcome: "qualified",
      duration_seconds: 323,
      audio_recording_url: "https://example.com/recordings/lead-001.mp3",
    },
    conversation_transcript: `Priya: Hello, am I speaking with Mr. Rajesh Kumar from Kumar Weighing Solutions?

Rajesh: Yes, this is Rajesh speaking. Who is this?

Priya: Good morning, Mr. Kumar. I'm Priya calling from SquadStack on behalf of our weighbridge solutions partner. I understand you may be looking for weighbridge equipment?

Rajesh: Oh yes, actually we are expanding our facility and need a new weighbridge installation.

Priya: That's great to hear! May I know what capacity you're looking for?

Rajesh: We need around 60 tons capacity. Our trucks are quite heavy with construction materials.

Priya: Understood. And what platform length would work best for your facility?

Rajesh: I think 18 meters should be sufficient based on our longest trucks.

Priya: Perfect. Would you prefer a pit type or pitless installation?

Rajesh: Pit type would be better for our location. We have the space for it.

Priya: Excellent. What's your expected timeline for this installation?

Rajesh: We're looking to get this done within the next 1-3 months ideally.

Priya: That sounds very feasible. Are you the decision maker for this purchase?

Rajesh: Yes, I'm the owner so I make the final decisions.

Priya: Wonderful, Mr. Kumar. I'll have our technical team reach out to you with a detailed proposal. What would be the best time to connect?

Rajesh: Mornings are better for me, between 10 AM to 12 PM on weekdays.

Priya: Perfect. Thank you for your time, Mr. Kumar. You'll hear from us soon!

Rajesh: Thank you, looking forward to it.`,
    scheduled_call: {
      preferred_day: "Monday - Friday",
      preferred_time: "10:00 AM - 12:00 PM",
      alternate_time: "3:00 PM - 5:00 PM",
      contact_mode: "Phone",
    },
    status: "qualified",
  },
  {
    id: "lead-002",
    lead_name: "Amit Sharma",
    company_name: "Sharma Transport & Logistics",
    contact_info: {
      phone: "+91 87654 32109",
      email: "amit.sharma@sharmatransport.in",
      whatsapp: "+91 87654 32109",
    },
    requirement: {
      type: "Replacement",
      capacity: "40 ton",
      platform_length: "12 meter",
      installation_type: "Pitless",
      location: "Ahmedabad, Gujarat",
      timeline: "3-6 months",
      decision_maker: "Self - Managing Director",
    },
    call_metadata: {
      timestamp: "2026-01-21T09:15:00Z",
      call_outcome: "reschedule",
      duration_seconds: 187,
      audio_recording_url: "https://example.com/recordings/lead-002.mp3",
    },
    conversation_transcript: `Priya: Hello, is this Mr. Amit Sharma from Sharma Transport?

Amit: Yes, speaking. But I'm in a meeting right now, can you call back?

Priya: Of course, Mr. Sharma. I'm calling regarding weighbridge solutions. When would be a convenient time to reach you?

Amit: Maybe tomorrow afternoon? Around 3 PM?

Priya: Tomorrow at 3 PM works. Shall I call on this same number?

Amit: Yes, this number is fine. I do need a replacement for our old weighbridge.

Priya: Understood, we'll discuss all details tomorrow. Thank you for your time!

Amit: Okay, bye.`,
    scheduled_call: {
      preferred_day: "Tomorrow",
      preferred_time: "3:00 PM",
      alternate_time: "4:00 PM - 5:00 PM",
      contact_mode: "Phone",
    },
    status: "reschedule",
  },
  {
    id: "lead-003",
    lead_name: "Priya Patel",
    company_name: "Patel Industries",
    contact_info: {
      phone: "+91 76543 21098",
      email: "priya.p@patelindustries.com",
      whatsapp: "+91 76543 21098",
    },
    requirement: {
      type: "New Installation",
      capacity: "80 ton",
      platform_length: "24 meter",
      installation_type: "Pit",
      location: "Surat, Gujarat",
      timeline: "Immediate",
      decision_maker: "Committee Decision",
    },
    call_metadata: {
      timestamp: "2026-01-20T15:45:00Z",
      call_outcome: "qualified",
      duration_seconds: 456,
      audio_recording_url: "https://example.com/recordings/lead-003.mp3",
    },
    conversation_transcript: `Priya (Agent): Good afternoon, may I speak with Ms. Priya Patel?

Priya Patel: Yes, this is Priya.

Priya (Agent): Hi Ms. Patel, I'm calling from SquadStack regarding industrial weighbridge solutions. We understand Patel Industries might be looking for weighing equipment?

Priya Patel: Yes, actually we've been looking for a heavy-duty weighbridge for our new manufacturing unit.

Priya (Agent): That's exactly what we specialize in. What capacity are you looking for?

Priya Patel: We need at least 80 tons. We handle very heavy machinery and raw materials.

Priya (Agent): 80 tons, noted. And the platform length?

Priya Patel: Our longest trailers are about 22 meters, so maybe 24 meters to be safe.

Priya (Agent): Smart choice. Pit or pitless installation?

Priya Patel: Pit type. We've already prepared the civil work for it.

Priya (Agent): Excellent planning! When do you need this operational?

Priya Patel: As soon as possible. We're losing money every day without proper weighing.

Priya (Agent): Understood. Who would be involved in the final decision?

Priya Patel: It would be a committee decision with our board, but I'm leading the evaluation.

Priya (Agent): Perfect. We can definitely help expedite this. When can we schedule a site visit?

Priya Patel: Can your team come this week? Friday would be ideal.

Priya (Agent): We'll confirm Friday with our technical team. Thank you, Ms. Patel!`,
    scheduled_call: {
      preferred_day: "Friday",
      preferred_time: "11:00 AM",
      alternate_time: "2:00 PM",
      contact_mode: "WhatsApp",
    },
    status: "qualified",
  },
  {
    id: "lead-004",
    lead_name: "Vikram Singh",
    company_name: "Singh Agricultural Products",
    contact_info: {
      phone: "+91 65432 10987",
      email: "vikram@singhagri.co.in",
      whatsapp: "+91 65432 10987",
    },
    requirement: {
      type: "New Installation",
      capacity: "30 ton",
      platform_length: "10 meter",
      installation_type: "Pitless",
      location: "Jaipur, Rajasthan",
      timeline: "Not decided",
      decision_maker: "N/A",
    },
    call_metadata: {
      timestamp: "2026-01-20T11:20:00Z",
      call_outcome: "not_interested",
      duration_seconds: 95,
      audio_recording_url: "https://example.com/recordings/lead-004.mp3",
    },
    conversation_transcript: `Priya: Hello, is this Mr. Vikram Singh?

Vikram: Yes, who's calling?

Priya: Good morning sir, I'm Priya from SquadStack. We provide weighbridge solutions and—

Vikram: Sorry, we already have a weighbridge supplier we work with.

Priya: I understand, sir. May I ask if you're satisfied with their service?

Vikram: Yes, we've been with them for 10 years. Not looking to change.

Priya: No problem at all, Mr. Singh. If you ever need a second option, please keep us in mind.

Vikram: Sure, goodbye.

Priya: Thank you for your time. Have a good day!`,
    scheduled_call: {
      preferred_day: "N/A",
      preferred_time: "N/A",
      alternate_time: "N/A",
      contact_mode: "N/A",
    },
    status: "not_interested",
  },
  {
    id: "lead-005",
    lead_name: "Deepak Verma",
    company_name: "Verma Steel Works",
    contact_info: {
      phone: "+91 54321 09876",
      email: "deepak.verma@vermasteel.com",
      whatsapp: "+91 54321 09876",
    },
    requirement: {
      type: "Replacement",
      capacity: "100 ton",
      platform_length: "22 meter",
      installation_type: "Pit",
      location: "Raipur, Chhattisgarh",
      timeline: "6-12 months",
      decision_maker: "Board Approval Required",
    },
    call_metadata: {
      timestamp: "2026-01-19T14:00:00Z",
      call_outcome: "qualified",
      duration_seconds: 512,
      audio_recording_url: "https://example.com/recordings/lead-005.mp3",
    },
    conversation_transcript: `Priya: Good afternoon, may I speak with Mr. Deepak Verma from Verma Steel Works?

Deepak: Yes, this is Deepak.

Priya: Hello Mr. Verma, I'm Priya calling about industrial weighbridge solutions. Your company was referred to us as possibly needing weighing equipment upgrades?

Deepak: Actually, yes. Our current weighbridge is nearly 15 years old and giving us problems.

Priya: I see. What issues are you facing with the current setup?

Deepak: Accuracy issues mainly. And the load cells need frequent replacement.

Priya: Those are common issues with older systems. What capacity is your current one?

Deepak: It's 80 tons but we need to upgrade to 100 tons now.

Priya: And the platform length?

Deepak: 22 meters should work for us.

Priya: Pit or pitless?

Deepak: We'll stick with pit since the foundation is already there.

Priya: Smart approach. What's your timeline for this replacement?

Deepak: We're looking at 6-12 months. Need to get board approval first.

Priya: Understood. Would you like us to prepare a proposal for the board?

Deepak: Yes, that would be helpful. Can you email me the details?

Priya: Absolutely. I'll send a comprehensive proposal this week. Thank you, Mr. Verma!`,
    scheduled_call: {
      preferred_day: "Next week",
      preferred_time: "Afternoon",
      alternate_time: "Flexible",
      contact_mode: "Email first, then Phone",
    },
    status: "qualified",
  },
  {
    id: "lead-006",
    lead_name: "Unknown",
    company_name: "ABC Enterprises",
    contact_info: {
      phone: "+91 43210 98765",
      email: "info@abcent.com",
      whatsapp: "+91 43210 98765",
    },
    requirement: {
      type: "N/A",
      capacity: "N/A",
      platform_length: "N/A",
      installation_type: "N/A",
      location: "Delhi",
      timeline: "N/A",
      decision_maker: "N/A",
    },
    call_metadata: {
      timestamp: "2026-01-19T10:30:00Z",
      call_outcome: "wrong_contact",
      duration_seconds: 45,
      audio_recording_url: "https://example.com/recordings/lead-006.mp3",
    },
    conversation_transcript: `Priya: Hello, may I speak with the purchase department regarding weighbridge requirements?

Unknown: Sorry, you have the wrong number. This is the HR department.

Priya: Oh, I apologize for the confusion. Do you have the correct number for the purchase team?

Unknown: I don't have it handy. You can try the main office line.

Priya: Thank you, I'll do that. Sorry for the inconvenience.`,
    scheduled_call: {
      preferred_day: "N/A",
      preferred_time: "N/A",
      alternate_time: "N/A",
      contact_mode: "N/A",
    },
    status: "wrong_contact",
  },
  {
    id: "lead-007",
    lead_name: "Suresh Reddy",
    company_name: "Reddy Mining Corporation",
    contact_info: {
      phone: "+91 32109 87654",
      email: "suresh.r@reddymining.com",
      whatsapp: "+91 32109 87654",
    },
    requirement: {
      type: "New Installation",
      capacity: "120 ton",
      platform_length: "24 meter",
      installation_type: "Pit",
      location: "Hyderabad, Telangana",
      timeline: "1-3 months",
      decision_maker: "Self - CEO",
    },
    call_metadata: {
      timestamp: "2026-01-18T16:20:00Z",
      call_outcome: "qualified",
      duration_seconds: 398,
      audio_recording_url: "https://example.com/recordings/lead-007.mp3",
    },
    conversation_transcript: `Priya: Hello, is this Mr. Suresh Reddy from Reddy Mining?

Suresh: Yes, speaking.

Priya: Good afternoon, Mr. Reddy. I'm Priya from SquadStack, calling about heavy-duty weighbridge solutions.

Suresh: Perfect timing. We're setting up a new mining site and need a proper weighbridge.

Priya: Excellent! Mining operations require robust equipment. What capacity are you looking at?

Suresh: 120 tons minimum. Our dumpers are massive.

Priya: We have excellent options in that range. Platform length preference?

Suresh: 24 meters. Standard for our operations.

Priya: Installation type?

Suresh: Pit type. Better for dusty environments.

Priya: Very practical choice. Timeline?

Suresh: We need it operational within 2-3 months max. The site is almost ready.

Priya: We can work with that. Shall I arrange a site visit this week?

Suresh: Yes, Thursday or Friday would work.

Priya: I'll coordinate with the team and confirm. Thank you, Mr. Reddy!`,
    scheduled_call: {
      preferred_day: "Thursday/Friday",
      preferred_time: "Any time",
      alternate_time: "Flexible",
      contact_mode: "Phone",
    },
    status: "qualified",
  },
  {
    id: "lead-008",
    lead_name: "Meera Krishnan",
    company_name: "Krishnan Foods Processing",
    contact_info: {
      phone: "+91 21098 76543",
      email: "meera@krishnanfoods.co.in",
      whatsapp: "+91 21098 76543",
    },
    requirement: {
      type: "New Installation",
      capacity: "20 ton",
      platform_length: "8 meter",
      installation_type: "Pitless",
      location: "Chennai, Tamil Nadu",
      timeline: "Immediate",
      decision_maker: "Self - Director",
    },
    call_metadata: {
      timestamp: "2026-01-18T11:45:00Z",
      call_outcome: "qualified",
      duration_seconds: 276,
      audio_recording_url: "https://example.com/recordings/lead-008.mp3",
    },
    conversation_transcript: `Priya: Good morning, is this Ms. Meera Krishnan?

Meera: Yes, speaking. How can I help you?

Priya: Hi Ms. Krishnan, I'm Priya calling about weighbridge solutions. I understand Krishnan Foods might need weighing equipment?

Meera: Oh yes! We were just discussing this yesterday. We need a small weighbridge for our trucks.

Priya: Great timing then! What capacity would suit your needs?

Meera: Around 20 tons should be enough. We deal with food products, not heavy machinery.

Priya: And platform length?

Meera: 8 meters would be sufficient.

Priya: Would you prefer pit or pitless installation?

Meera: Pitless please. We need to keep the area clean for food safety compliance.

Priya: Excellent choice for food processing. When do you need this?

Meera: ASAP actually. We're losing business without proper weighing.

Priya: We can expedite this. Are you the decision maker?

Meera: Yes, I'm the Director. I can approve immediately.

Priya: Perfect. I'll have our team contact you with a quote today. Thank you, Ms. Krishnan!`,
    scheduled_call: {
      preferred_day: "Today",
      preferred_time: "4:00 PM - 6:00 PM",
      alternate_time: "Tomorrow morning",
      contact_mode: "WhatsApp",
    },
    status: "qualified",
  },
];
