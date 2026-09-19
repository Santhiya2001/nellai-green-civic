import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { Complaint, ComplaintListItem } from "../../types";

export default function MyComplaints() {
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);
  const [selected, setSelected] = useState<Complaint | null>(null);
  const [feedback, setFeedback] = useState("");

  function refresh() {
    apiClient.get<ComplaintListItem[]>("/complaints", { params: { mine: true } }).then((res) => setComplaints(res.data));
  }

  useEffect(refresh, []);

  async function openDetail(id: string) {
    const { data } = await apiClient.get<Complaint>(`/complaints/${id}`);
    setSelected(data);
  }

  async function verify(complaintId: string, verified: boolean) {
    await apiClient.post(`/complaints/${complaintId}/verify`, { verified, feedback: feedback || null });
    setSelected(null);
    setFeedback("");
    refresh();
  }

  return (
    <div>
      <h2>My Complaints</h2>
      <div className="card">
        <table>
          <thead><tr><th>Number</th><th>Category</th><th>Severity</th><th>Status</th><th>Deadline</th><th></th></tr></thead>
          <tbody>
            {complaints.map((c) => (
              <tr key={c.id}>
                <td>{c.complaint_number}</td>
                <td>{c.category_code}</td>
                <td><span className={`badge ${c.severity}`}>{c.severity}</span></td>
                <td><span className="badge status">{c.status}</span></td>
                <td>{c.deadline_at ? new Date(c.deadline_at).toLocaleDateString() : "-"}</td>
                <td><button className="btn secondary" onClick={() => openDetail(c.id)}>View</button></td>
              </tr>
            ))}
            {complaints.length === 0 && <tr><td colSpan={6} className="muted">No complaints yet.</td></tr>}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3>{selected.complaint_number}</h3>
          <p>{selected.description}</p>
          <p className="muted">Status: {selected.status} · Severity: {selected.severity}</p>
          {selected.status === "VERIFICATION" && (
            <div>
              <label>Feedback (optional)</label>
              <textarea rows={2} value={feedback} onChange={(e) => setFeedback(e.target.value)} />
              <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
                <button className="btn" onClick={() => verify(selected.id, true)}>Confirm Resolved</button>
                <button className="btn danger" onClick={() => verify(selected.id, false)}>Not Resolved, Reopen</button>
              </div>
            </div>
          )}
          <button className="btn secondary" style={{ marginTop: 12 }} onClick={() => setSelected(null)}>Close</button>
        </div>
      )}
    </div>
  );
}
