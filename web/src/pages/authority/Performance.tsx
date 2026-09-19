import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import StatTile from "../../components/StatTile";
import { DashboardSummary } from "../../types";

export default function Performance() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    apiClient.get<DashboardSummary>("/analytics/dashboard").then((res) => setSummary(res.data));
  }, []);

  if (!summary) return <div>Loading...</div>;

  return (
    <div>
      <h2>Performance Dashboard</h2>
      <div className="grid grid-3">
        <StatTile label="Open Assigned" value={summary.open_complaints} />
        <StatTile label="Resolved" value={summary.resolved_complaints} />
        <StatTile label="Overdue" value={summary.overdue_complaints} />
      </div>
    </div>
  );
}
