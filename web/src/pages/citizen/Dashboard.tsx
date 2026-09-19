import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiClient } from "../../api/client";
import StatTile from "../../components/StatTile";
import { useAuth } from "../../store/AuthContext";
import { ComplaintListItem } from "../../types";
import { wikimediaFile } from "../../utils/wikimedia";

// Public domain, Wikimedia Commons.
const BANNER_IMG = wikimediaFile("Courtallam (Kutralam) Falls - Tenkasi 02.jpg", 1200);

export default function CitizenDashboard() {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);

  useEffect(() => {
    apiClient.get<ComplaintListItem[]>("/complaints", { params: { mine: true, limit: 5 } }).then((res) => setComplaints(res.data));
  }, []);

  const open = complaints.filter((c) => !["CLOSED", "REJECTED"].includes(c.status)).length;
  const firstName = user?.full_name?.split(" ")[0] || "there";

  return (
    <div>
      <div className="welcome-banner" style={{ backgroundImage: `linear-gradient(120deg, rgba(19,92,57,0.88), rgba(19,92,57,0.55)), url(${BANNER_IMG})` }}>
        <h2>Welcome back, {firstName}</h2>
        <p>Every report you file helps keep Tirunelveli's civic infrastructure and environment accountable.</p>
      </div>

      <div className="grid grid-3" style={{ margin: "20px 0 24px" }}>
        <StatTile label="My complaints" value={complaints.length} />
        <StatTile label="Currently open" value={open} />
        <Link to="/citizen/report" style={{ textDecoration: "none" }}>
          <StatTile label="Report a new issue" value="+" />
        </Link>
      </div>

      <div className="card">
        <div className="topbar">
          <h3 style={{ margin: 0 }}>Recent complaints</h3>
          <Link className="btn secondary" to="/citizen/complaints">View all</Link>
        </div>
        <table>
          <thead>
            <tr><th>Number</th><th>Category</th><th>Status</th><th>Reported</th></tr>
          </thead>
          <tbody>
            {complaints.map((c) => (
              <tr key={c.id}>
                <td>{c.complaint_number}</td>
                <td>{c.category_code}</td>
                <td><span className="badge status">{c.status}</span></td>
                <td>{new Date(c.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {complaints.length === 0 && (
              <tr><td colSpan={4} className="muted">No complaints yet. <Link to="/citizen/report">Report your first issue</Link>.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
