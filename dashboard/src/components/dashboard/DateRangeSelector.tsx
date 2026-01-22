import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export type DateRange = "7days" | "30days" | "all";

interface DateRangeSelectorProps {
  value: DateRange;
  onChange: (value: DateRange) => void;
}

const DateRangeSelector = ({ value, onChange }: DateRangeSelectorProps) => {
  return (
    <Select value={value} onValueChange={(val) => onChange(val as DateRange)}>
      <SelectTrigger className="w-[160px] bg-card">
        <SelectValue placeholder="Select range" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="7days">Last 7 Days</SelectItem>
        <SelectItem value="30days">Last 30 Days</SelectItem>
        <SelectItem value="all">All Time</SelectItem>
      </SelectContent>
    </Select>
  );
};

export default DateRangeSelector;
