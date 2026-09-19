import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { apiClient } from "../../api/client";
import StatTile from "../../components/StatTile";
import { DashboardSummary } from "../../types";

export default function AdminDashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [byCategory, setByCategory] = useState<{ category: string; count: number }[]>([]);

  useEffect(() => {
    apiClient.get<DashboardSummary>("/analytics/dashboard").then((res) => setSummary(res.data));
    apiClient.get("/analytics/by-category").then((res) => setByCategory(res.data));
  }, []);

  if (!summary) return <div>Loading...</div>;

  return (
    <div>
      <h2>Admin Dashboard</h2>
      <div className="grid grid-4" style={{ marginBottom: 24 }}>
        <StatTile label="Total Complaints" value={summary.total_complaints} />
        <StatTile label="Open" value={summary.open_complaints} />
        <StatTile label="Resolved" value={summary.resolved_complaints} />
        <StatTile label="Overdue" value={summary.overdue_complaints} />
        <StatTile label="Escalated" value={summary.escalated_complaints} />
        <StatTile label="High Severity Open" value={summary.high_severity_open} />
      </div>

      <div className="card">
        <h3>Complaints by Category</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={byCategory}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" height={80} />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#1a7a4c" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
