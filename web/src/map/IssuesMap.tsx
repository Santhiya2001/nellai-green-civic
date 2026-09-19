import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { ComplaintListItem } from "../types";

// Vite serves leaflet's default marker images from node_modules poorly by
// default; point at the CDN copies instead of shipping broken icons.
const defaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

interface Props {
  complaints: ComplaintListItem[];
  center?: [number, number];
  zoom?: number;
}

const TIRUNELVELI_CENTER: [number, number] = [8.7139, 77.7567];

export default function IssuesMap({ complaints, center = TIRUNELVELI_CENTER, zoom = 13 }: Props) {
  return (
    <div className="complaint-map">
      <MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url={import.meta.env.VITE_MAP_TILE_URL || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}
        />
        {complaints.map((c) => (
          <Marker key={c.id} position={[c.latitude, c.longitude]} icon={defaultIcon}>
            <Popup>
              <strong>{c.complaint_number}</strong>
              <br />
              {c.category_code} &mdash; {c.severity}
              <br />
              <span className="muted">{c.status}</span>
              <p>{c.description.slice(0, 120)}</p>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
