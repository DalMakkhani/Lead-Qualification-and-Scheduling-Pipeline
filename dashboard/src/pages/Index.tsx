import { useState, useMemo, useEffect } from "react";
import { Phone, Target, CalendarDays } from "lucide-react";
import { isToday, subDays, isAfter } from "date-fns";
import MetricCard from "@/components/dashboard/MetricCard";
import LeadCard from "@/components/dashboard/LeadCard";
import LeadDetailPanel from "@/components/dashboard/LeadDetailPanel";
import FilterBar from "@/components/dashboard/FilterBar";
import DateRangeSelector, { DateRange } from "@/components/dashboard/DateRangeSelector";
import EmptyState from "@/components/dashboard/EmptyState";
import { Lead, CallOutcome } from "@/types/lead";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Index = () => {
  const [dateRange, setDateRange] = useState<DateRange>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<CallOutcome | "all">("all");
  const [sortOrder, setSortOrder] = useState<"newest" | "oldest" | "name">("newest");
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch leads from API
  useEffect(() => {
    const loadLeads = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          date_range: dateRange,
          sort: sortOrder,
        });
        if (statusFilter !== "all") params.append('status', statusFilter);
        if (searchQuery) params.append('search', searchQuery);
        
        const response = await fetch(`${API_URL}/leads?${params}`);
        const data = await response.json();
        setLeads(data);
      } catch (error) {
        console.error("Failed to fetch leads:", error);
        setLeads([]);
      } finally {
        setLoading(false);
      }
    };

    loadLeads();
  }, [dateRange, statusFilter, searchQuery, sortOrder]);

  // Filter by date range (already done server-side, but kept for consistency)
  const dateFilteredLeads = useMemo(() => {
    return leads;
  }, [leads]);

  // Calculate metrics
  const metrics = useMemo(() => {
    const totalCalls = dateFilteredLeads.length;
    const qualifiedCalls = dateFilteredLeads.filter(
      (lead) => lead.call_metadata.call_outcome === "qualified"
    ).length;
    const successRate = totalCalls > 0 ? Math.round((qualifiedCalls / totalCalls) * 100) : 0;
    const todaysCalls = dateFilteredLeads.filter((lead) =>
      isToday(new Date(lead.call_metadata.timestamp))
    ).length;

    return { totalCalls, successRate, todaysCalls };
  }, [dateFilteredLeads]);

  // Filter and sort leads
  const filteredLeads = useMemo(() => {
    let leads = [...dateFilteredLeads];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      leads = leads.filter(
        (lead) =>
          lead.lead_name.toLowerCase().includes(query) ||
          lead.company_name.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (statusFilter !== "all") {
      leads = leads.filter(
        (lead) => lead.call_metadata.call_outcome === statusFilter
      );
    }

    // Sort
    leads.sort((a, b) => {
      if (sortOrder === "name") {
        return a.lead_name.localeCompare(b.lead_name);
      }
      const dateA = new Date(a.call_metadata.timestamp).getTime();
      const dateB = new Date(b.call_metadata.timestamp).getTime();
      return sortOrder === "newest" ? dateB - dateA : dateA - dateB;
    });

    return leads;
  }, [dateFilteredLeads, searchQuery, statusFilter, sortOrder]);

  const hasActiveFilters = searchQuery !== "" || statusFilter !== "all" || sortOrder !== "newest";

  const handleClearFilters = () => {
    setSearchQuery("");
    setStatusFilter("all");
    setSortOrder("newest");
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
              Lead Qualification Dashboard
            </h1>
            <p className="mt-1 text-muted-foreground">
              AI-Powered Lead Qualification System
            </p>
          </div>
          <DateRangeSelector value={dateRange} onChange={setDateRange} />
        </header>

        {/* Metrics */}
        <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <MetricCard
            title="Total Calls"
            value={metrics.totalCalls}
            icon={Phone}
            trend={{ value: 12, isPositive: true }}
          />
          <MetricCard
            title="Success Rate"
            value={`${metrics.successRate}%`}
            subtitle="Qualified leads"
            icon={Target}
            trend={{ value: 5, isPositive: true }}
          />
          <MetricCard
            title="Today's Calls"
            value={metrics.todaysCalls}
            icon={CalendarDays}
          />
        </section>

        {/* Filters */}
        <section className="mb-6">
          <FilterBar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
            sortOrder={sortOrder}
            onSortOrderChange={setSortOrder}
            onClearFilters={handleClearFilters}
            hasActiveFilters={hasActiveFilters}
          />
        </section>

        {/* Lead List */}
        <section>
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading leads...</div>
          ) : filteredLeads.length === 0 ? (
            <EmptyState
              title={hasActiveFilters ? "No leads match your filters" : "No calls recorded yet"}
              description={
                hasActiveFilters
                  ? "Try adjusting your search or filter criteria."
                  : "When calls are made, they will appear here."
              }
            />
          ) : (
            <div className="grid gap-3">
              {filteredLeads.map((lead) => (
                <LeadCard
                  key={lead.id}
                  lead={lead}
                  onClick={() => setSelectedLead(lead)}
                />
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Detail Panel */}
      {selectedLead && (
        <LeadDetailPanel
          lead={selectedLead}
          onClose={() => setSelectedLead(null)}
        />
      )}
    </div>
  );
};

export default Index;
