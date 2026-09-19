import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";
import { NotificationItem } from "../../types";

export default function Notifications() {
  const [items, setItems] = useState<NotificationItem[]>([]);

  function refresh() {
    apiClient.get<NotificationItem[]>("/notifications").then((res) => setItems(res.data));
  }

  useEffect(refresh, []);

  async function markRead(id: string) {
    await apiClient.post(`/notifications/${id}/read`);
    refresh();
  }

  return (
    <div>
      <h2>Notifications</h2>
      <div className="card">
        {items.map((n) => (
          <div key={n.id} style={{ padding: "10px 0", borderBottom: "1px solid var(--color-border)", opacity: n.is_read ? 0.6 : 1 }}>
            <strong>{n.title}</strong>
            <p style={{ margin: "4px 0" }}>{n.body}</p>
            <div className="topbar">
              <span className="muted">{new Date(n.created_at).toLocaleString()}</span>
              {!n.is_read && <button className="btn secondary" onClick={() => markRead(n.id)}>Mark read</button>}
            </div>
          </div>
        ))}
        {items.length === 0 && <p className="muted">No notifications yet.</p>}
      </div>
    </div>
  );
}
