import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import IssuesMap from "../../map/IssuesMap";
import { ComplaintListItem } from "../../types";

export default function GISMap() {
  const [complaints, setComplaints] = useState<ComplaintListItem[]>([]);

  useEffect(() => {
    apiClient.get<ComplaintListItem[]>("/complaints", { params: { limit: 500 } }).then((res) => setComplaints(res.data));
  }, []);

  return (
    <div>
      <h2>GIS Map</h2>
      <IssuesMap complaints={complaints} zoom={12} />
    </div>
  );
}
