import { format } from "date-fns";
import { ChevronRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Lead, CallOutcome } from "@/types/lead";
import StatusBadge from "./StatusBadge";
import { cn } from "@/lib/utils";

interface LeadCardProps {
  lead: Lead;
  onClick: () => void;
}

const borderColorMap: Record<CallOutcome, string> = {
  qualified: "border-l-success",
  reschedule: "border-l-warning",
  not_interested: "border-l-destructive",
  wrong_contact: "border-l-muted-foreground",
};

const LeadCard = ({ lead, onClick }: LeadCardProps) => {
  const callDate = new Date(lead.call_metadata.timestamp);
  const outcome = lead.call_metadata.call_outcome;

  return (
    <Card
      className={cn(
        "card-shadow cursor-pointer border-l-4 transition-all duration-200 hover:card-shadow-hover hover:-translate-y-0.5",
        borderColorMap[outcome]
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h3 className="truncate text-base font-semibold text-foreground">
              {lead.lead_name}
            </h3>
            <p className="mt-0.5 truncate text-sm text-muted-foreground">
              {lead.company_name}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              {format(callDate, "MMM d, yyyy")} at {format(callDate, "h:mm a")}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={outcome} />
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default LeadCard;
