import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import IssuesMap from "../../map/IssuesMap";
import { ComplaintListItem } from "../../types";

export default function EnvironmentalMap() {
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);
  const [waterBodies, setWaterBodies] = useState<any[]>([]);
  const [trees, setTrees] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get<ComplaintListItem[]>("/complaints", { params: { limit: 200 } }).then((res) => setComplaints(res.data));
    apiClient.get("/modules/water/water-bodies").then((res) => setWaterBodies(res.data)).catch(() => {});
    apiClient.get("/modules/afforestation/trees").then((res) => setTrees(res.data)).catch(() => {});
  }, []);

  return (
    <div>
      <h2>Environmental Map</h2>
      <p className="muted">Complaints, water bodies and registered trees across Tirunelveli.</p>
      <IssuesMap complaints={complaints} />
      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h4>Water Bodies ({waterBodies.length})</h4>
          <ul>{waterBodies.slice(0, 8).map((w) => <li key={w.id}>{w.name} - {w.type}</li>)}</ul>
        </div>
        <div className="card">
          <h4>Registered Trees ({trees.length})</h4>
          <ul>{trees.slice(0, 8).map((t) => <li key={t.id}>{t.species} - {t.status}</li>)}</ul>
        </div>
      </div>
    </div>
  );
}
