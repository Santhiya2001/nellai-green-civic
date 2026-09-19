import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { ComplaintListItem } from "../../types";

export default function ComplaintManagement() {
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);
  const [statusFilter, setStatusFilter] = useState("");

  function refresh() {
    apiClient.get<ComplaintListItem[]>("/complaints", { params: statusFilter ? { status: statusFilter } : {} }).then((res) => setComplaints(res.data));
  }

  useEffect(refresh, [statusFilter]);

  async function reject(id: string) {
    const reason = prompt("Reason for rejection:");
    if (!reason) return;
    await apiClient.post(`/complaints/${id}/reject`, { reason });
    refresh();
  }

  return (
    <div>
      <h2>Complaint Management</h2>
      <div className="card">
        <label>Filter by status</label>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ maxWidth: 240 }}>
          <option value="">All</option>
          {["REPORTED", "AI_ANALYZED", "ASSIGNED", "ACKNOWLEDGED", "IN_PROGRESS", "RESOLVED", "VERIFICATION", "CLOSED", "REJECTED", "REOPENED"].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <table style={{ marginTop: 16 }}>
          <thead><tr><th>Number</th><th>Category</th><th>Severity</th><th>Status</th><th>Deadline</th><th></th></tr></thead>
          <tbody>
            {complaints.map((c) => (
              <tr key={c.id}>
                <td>{c.complaint_number}</td>
                <td>{c.category_code}</td>
                <td><span className={`badge ${c.severity}`}>{c.severity}</span></td>
                <td><span className="badge status">{c.status}</span></td>
                <td>{c.deadline_at ? new Date(c.deadline_at).toLocaleDateString() : "-"}</td>
                <td>
                  {!["CLOSED", "REJECTED"].includes(c.status) && (
                    <button className="btn danger" onClick={() => reject(c.id)}>Reject</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
