import { Phone } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  description?: string;
}

const EmptyState = ({
  title = "No calls recorded yet",
  description = "When calls are made, they will appear here.",
}: EmptyStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
        <Phone className="h-7 w-7 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>
    </div>
  );
};

export default EmptyState;
