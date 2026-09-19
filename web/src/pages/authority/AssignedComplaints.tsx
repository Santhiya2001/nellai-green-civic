import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { ComplaintListItem } from "../../types";

const NEXT_STATUS: Record<string, string[]> = {
  ASSIGNED: ["ACKNOWLEDGED", "REJECTED"],
  ACKNOWLEDGED: ["IN_PROGRESS", "REJECTED"],
  IN_PROGRESS: [],
  REOPENED: ["IN_PROGRESS"],
};

export default function AssignedComplaints() {
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [resolutionText, setResolutionText] = useState("");
  const [resolutionPhoto, setResolutionPhoto] = useState<File | null>(null);

  function refresh() {
    apiClient.get<ComplaintListItem[]>("/complaints").then((res) => setComplaints(res.data));
  }
  useEffect(refresh, []);

  async function moveStatus(id: string, toStatus: string) {
    if (toStatus === "REJECTED") {
      const reason = prompt("Reason for rejection:");
      if (!reason) return;
      await apiClient.post(`/complaints/${id}/reject`, { reason });
    } else {
      await apiClient.post(`/complaints/${id}/status`, { to_status: toStatus });
    }
    refresh();
  }

  async function submitResolution(id: string) {
    const form = new FormData();
    form.append("description", resolutionText);
    if (resolutionPhoto) form.append("photo", resolutionPhoto);
    await apiClient.post(`/complaints/${id}/resolve`, form, { headers: { "Content-Type": "multipart/form-data" } });
    setResolvingId(null);
    setResolutionText("");
    setResolutionPhoto(null);
    refresh();
  }

  const priority = [...complaints].sort((a, b) => {
    const order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];
    return order.indexOf(a.severity) - order.indexOf(b.severity);
  });

  return (
    <div>
      <h2>Assigned Complaints</h2>
      <div className="card">
        <table>
          <thead><tr><th>Number</th><th>Category</th><th>Severity</th><th>Status</th><th>Deadline</th><th>Actions</th></tr></thead>
          <tbody>
            {priority.map((c) => (
              <tr key={c.id}>
                <td>{c.complaint_number}</td>
                <td>{c.category_code}</td>
                <td><span className={`badge ${c.severity}`}>{c.severity}</span></td>
                <td><span className="badge status">{c.status}</span></td>
                <td>{c.deadline_at ? new Date(c.deadline_at).toLocaleDateString() : "-"}</td>
                <td>
                  {(NEXT_STATUS[c.status] || []).map((s) => (
                    <button key={s} className="btn secondary" style={{ marginRight: 6 }} onClick={() => moveStatus(c.id, s)}>{s}</button>
                  ))}
                  {c.status === "IN_PROGRESS" && (
                    <button className="btn" onClick={() => setResolvingId(c.id)}>Mark Resolved</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {resolvingId && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3>Resolution Evidence</h3>
          <label>Description of work done</label>
          <textarea rows={3} value={resolutionText} onChange={(e) => setResolutionText(e.target.value)} />
          <label>Photo evidence</label>
          <input type="file" accept="image/*" onChange={(e) => setResolutionPhoto(e.target.files?.[0] || null)} />
          <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
            <button className="btn" onClick={() => submitResolution(resolvingId)}>Submit</button>
            <button className="btn secondary" onClick={() => setResolvingId(null)}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}
