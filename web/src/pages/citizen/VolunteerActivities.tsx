import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";

interface VolunteerEvent {
  id: string;
  title: string;
  activity_type: string;
  start_at: string;
  latitude: number;
  longitude: number;
  registered_count?: number;
  capacity?: number;
}

export default function VolunteerActivities() {
  const [events, setEvents] = useState<VolunteerEvent[]>([]);
  const [message, setMessage] = useState("");

  function refresh() {
    apiClient.get<VolunteerEvent[]>("/modules/volunteer/events").then((res) => setEvents(res.data));
  }

  useEffect(refresh, []);

  async function register(eventId: string) {
    try {
      await apiClient.post(`/modules/volunteer/events/${eventId}/register`);
      setMessage("Registered! See you there.");
      refresh();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || "Could not register.");
    }
  }

  return (
    <div>
      <h2>Volunteer Activities</h2>
      {message && <p className="muted">{message}</p>}
      <div className="grid grid-2">
        {events.map((e) => (
          <div key={e.id} className="card">
            <h4>{e.title}</h4>
            <p className="muted">{e.activity_type.replace("_", " ")} &middot; {new Date(e.start_at).toLocaleString()}</p>
            {e.capacity && <p className="muted">{e.registered_count ?? 0} / {e.capacity} registered</p>}
            <button className="btn" onClick={() => register(e.id)}>Register to volunteer</button>
          </div>
        ))}
        {events.length === 0 && <p className="muted">No upcoming events right now.</p>}
      </div>
    </div>
  );
}
