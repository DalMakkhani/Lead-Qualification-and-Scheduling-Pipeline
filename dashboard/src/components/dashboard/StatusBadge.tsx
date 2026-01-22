import { cn } from "@/lib/utils";
import { CallOutcome } from "@/types/lead";

interface StatusBadgeProps {
  status: CallOutcome;
  className?: string;
}

const statusConfig: Record<
  CallOutcome,
  { label: string; className: string }
> = {
  qualified: {
    label: "Qualified",
    className: "bg-success/10 text-success border-success/20",
  },
  qualified_scheduled: {
    label: "Qualified & Scheduled",
    className: "bg-success/10 text-success border-success/20",
  },
  reschedule: {
    label: "Reschedule",
    className: "bg-warning/10 text-warning border-warning/20",
  },
  not_interested: {
    label: "Not Interested",
    className: "bg-destructive/10 text-destructive border-destructive/20",
  },
  wrong_contact: {
    label: "Wrong Contact",
    className: "bg-muted text-muted-foreground border-muted",
  },
  do_not_call: {
    label: "Do Not Call",
    className: "bg-destructive/10 text-destructive border-destructive/20",
  },
};

const StatusBadge = ({ status, className }: StatusBadgeProps) => {
  const config = statusConfig[status];

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  );
};

export default StatusBadge;
