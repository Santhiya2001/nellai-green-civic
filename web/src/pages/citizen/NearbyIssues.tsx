import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import IssuesMap from "../../map/IssuesMap";
import { ComplaintListItem } from "../../types";

export default function NearbyIssues() {
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);
  const [center, setCenter] = useState<[number, number] | undefined>(undefined);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!navigator.geolocation) {
      loadNearby(8.7139, 77.7567);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCenter([pos.coords.latitude, pos.coords.longitude]);
        loadNearby(pos.coords.latitude, pos.coords.longitude);
      },
      () => {
        setError("Location access denied; showing Tirunelveli town center instead.");
        loadNearby(8.7139, 77.7567);
      }
    );
  }, []);

  function loadNearby(lat: number, lng: number) {
    apiClient.get<ComplaintListItem[]>("/complaints/nearby", { params: { latitude: lat, longitude: lng, radius_meters: 3000 } }).then((res) => setComplaints(res.data));
  }

  return (
    <div>
      <h2>Nearby Issues</h2>
      {error && <p className="muted">{error}</p>}
      <IssuesMap complaints={complaints} center={center} />
      <div className="card" style={{ marginTop: 16 }}>
        <table>
          <thead><tr><th>Number</th><th>Category</th><th>Status</th></tr></thead>
          <tbody>
            {complaints.map((c) => (
              <tr key={c.id}><td>{c.complaint_number}</td><td>{c.category_code}</td><td><span className="badge status">{c.status}</span></td></tr>
            ))}
            {complaints.length === 0 && <tr><td colSpan={3} className="muted">No nearby issues reported within 3km.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
