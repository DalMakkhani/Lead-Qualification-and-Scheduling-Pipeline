import { format } from "date-fns";
import { X, Phone, Mail, MessageCircle, MapPin, Clock, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Lead } from "@/types/lead";
import StatusBadge from "./StatusBadge";
import AudioPlayer from "./AudioPlayer";
import { cn } from "@/lib/utils";

interface LeadDetailPanelProps {
  lead: Lead;
  onClose: () => void;
}

const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins} min ${secs} sec`;
};

const LeadDetailPanel = ({ lead, onClose }: LeadDetailPanelProps) => {
  const callDate = new Date(lead.call_metadata.timestamp);

  const handleExportTranscript = () => {
    const blob = new Blob([lead.conversation_transcript], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transcript-${lead.lead_name.replace(/\s+/g, "-").toLowerCase()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm fade-in"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed bottom-0 right-0 top-0 z-50 w-full max-w-2xl bg-card shadow-2xl slide-in-right">
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-start justify-between border-b p-6">
            <div>
              <h2 className="text-xl font-semibold text-foreground">
                {lead.lead_name}
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {lead.company_name}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={onClose}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Content */}
          <ScrollArea className="flex-1 p-6">
            <div className="space-y-8">
              {/* Call Information */}
              <section>
                <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  Call Information
                </h3>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="rounded-lg border bg-muted/30 p-3">
                    <p className="text-xs text-muted-foreground">Date & Time</p>
                    <p className="mt-1 text-sm font-medium">
                      {format(callDate, "MMM d, yyyy")}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {format(callDate, "h:mm a")}
                    </p>
                  </div>
                  <div className="rounded-lg border bg-muted/30 p-3">
                    <p className="text-xs text-muted-foreground">Duration</p>
                    <p className="mt-1 text-sm font-medium">
                      {formatDuration(lead.call_metadata.duration_seconds)}
                    </p>
                  </div>
                  <div className="rounded-lg border bg-muted/30 p-3">
                    <p className="text-xs text-muted-foreground">Status</p>
                    <div className="mt-1">
                      <StatusBadge status={lead.call_metadata.call_outcome} />
                    </div>
                  </div>
                </div>
              </section>

              <Separator />

              {/* Contact Details */}
              <section>
                <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  Contact Details
                </h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="flex items-center gap-3 rounded-lg border p-3">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">Phone</p>
                      <p className="text-sm font-medium">{lead.contact_info.phone}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 rounded-lg border p-3">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">Email</p>
                      <p className="text-sm font-medium">{lead.contact_info.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 rounded-lg border p-3">
                    <MessageCircle className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">WhatsApp</p>
                      <p className="text-sm font-medium">{lead.contact_info.whatsapp}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 rounded-lg border p-3">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">Location</p>
                      <p className="text-sm font-medium">{lead.requirement.location}</p>
                    </div>
                  </div>
                </div>
              </section>

              <Separator />

              {/* Requirement Details */}
              <section>
                <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  Requirement Details
                </h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="rounded-lg border p-3">
                    <p className="text-xs text-muted-foreground">Requirement Type</p>
                    <p className="mt-1 text-sm font-medium">{lead.requirement.type}</p>
                  </div>
                  <div className="rounded-lg border p-3">
                    <p className="text-xs text-muted-foreground">Capacity</p>
                    <p className="mt-1 text-sm font-medium">{lead.requirement.capacity}</p>
                  </div>
                  <div className="rounded-lg border p-3">
                    <p className="text-xs text-muted-foreground">Platform Length</p>
                    <p className="mt-1 text-sm font-medium">{lead.requirement.platform_length}</p>
                  </div>
                  <div className="rounded-lg border p-3">
                    <p className="text-xs text-muted-foreground">Installation Type</p>
                    <p className="mt-1 text-sm font-medium">{lead.requirement.installation_type}</p>
                  </div>
                  <div className="rounded-lg border p-3">
                    <p className="text-xs text-muted-foreground">Timeline</p>
                    <p className="mt-1 text-sm font-medium">{lead.requirement.timeline}</p>
                  </div>
                  <div className="rounded-lg border p-3">
                    <p className="text-xs text-muted-foreground">Decision Maker</p>
                    <p className="mt-1 text-sm font-medium">{lead.requirement.decision_maker}</p>
                  </div>
                </div>
              </section>

              {lead.scheduled_call.preferred_day !== "N/A" && (
                <>
                  <Separator />

                  {/* Scheduled Follow-up */}
                  <section>
                    <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                      Scheduled Follow-up
                    </h3>
                    <div className="grid gap-3 sm:grid-cols-2">
                      <div className="flex items-center gap-3 rounded-lg border p-3">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-xs text-muted-foreground">Preferred Time</p>
                          <p className="text-sm font-medium">
                            {lead.scheduled_call.preferred_day}, {lead.scheduled_call.preferred_time}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 rounded-lg border p-3">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-xs text-muted-foreground">Alternate Time</p>
                          <p className="text-sm font-medium">{lead.scheduled_call.alternate_time}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 rounded-lg border p-3 sm:col-span-2">
                        <Phone className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-xs text-muted-foreground">Contact Mode</p>
                          <p className="text-sm font-medium">{lead.scheduled_call.contact_mode}</p>
                        </div>
                      </div>
                    </div>
                  </section>
                </>
              )}

              <Separator />

              {/* Call Recording */}
              <section>
                <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  Call Recording
                </h3>
                <AudioPlayer audioUrl={lead.call_metadata.audio_recording_url} />
              </section>

              <Separator />

              {/* Transcript */}
              <section>
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                    Call Transcript
                  </h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportTranscript}
                    className="gap-2"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Export
                  </Button>
                </div>
                <div className="rounded-lg border bg-muted/30 p-4">
                  <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                    {lead.conversation_transcript.split("\n\n").map((paragraph, idx) => (
                      <p
                        key={idx}
                        className={cn(
                          "mb-3 last:mb-0",
                          paragraph.startsWith("Priya") && "text-primary"
                        )}
                      >
                        {paragraph}
                      </p>
                    ))}
                  </div>
                </div>
              </section>
            </div>
          </ScrollArea>

          {/* Footer */}
          <div className="border-t p-4">
            <Button variant="outline" onClick={onClose} className="w-full">
              Close
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};

export default LeadDetailPanel;
