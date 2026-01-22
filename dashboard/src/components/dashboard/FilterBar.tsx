import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CallOutcome } from "@/types/lead";

interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  statusFilter: CallOutcome | "all";
  onStatusFilterChange: (value: CallOutcome | "all") => void;
  sortOrder: "newest" | "oldest" | "name";
  onSortOrderChange: (value: "newest" | "oldest" | "name") => void;
  onClearFilters: () => void;
  hasActiveFilters: boolean;
}

const FilterBar = ({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  sortOrder,
  onSortOrderChange,
  onClearFilters,
  hasActiveFilters,
}: FilterBarProps) => {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search by lead name or company..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9"
        />
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Select
          value={statusFilter}
          onValueChange={(value) => onStatusFilterChange(value as CallOutcome | "all")}
        >
          <SelectTrigger className="w-[160px] bg-card">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="qualified">Qualified</SelectItem>
            <SelectItem value="reschedule">Reschedule</SelectItem>
            <SelectItem value="not_interested">Not Interested</SelectItem>
            <SelectItem value="wrong_contact">Wrong Contact</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={sortOrder}
          onValueChange={(value) => onSortOrderChange(value as "newest" | "oldest" | "name")}
        >
          <SelectTrigger className="w-[160px] bg-card">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="newest">Newest First</SelectItem>
            <SelectItem value="oldest">Oldest First</SelectItem>
            <SelectItem value="name">Lead Name A-Z</SelectItem>
          </SelectContent>
        </Select>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearFilters}
            className="gap-1.5 text-muted-foreground hover:text-foreground"
          >
            <X className="h-3.5 w-3.5" />
            Clear Filters
          </Button>
        )}
      </div>
    </div>
  );
};

export default FilterBar;
