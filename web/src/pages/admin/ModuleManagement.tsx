import { useEffect, useState } from "react";
import { apiClient } from "../../api/client";

interface ModuleInfo {
  id: string;
  name: string;
  version: string;
  description: string;
  api_version: string;
  author: string;
  enabled: boolean;
}

export default function ModuleManagement() {
  const [modules, setModules] = useState<ModuleInfo[]>([]);

  useEffect(() => {
    apiClient.get<ModuleInfo[]>("/modules").then((res) => setModules(res.data));
  }, []);

  return (
    <div>
      <h2>Module Registry</h2>
      <p className="muted">
        Every module here was auto-discovered from a <code>module.json</code> under <code>/modules</code> --
        a new module can be added by dropping in a new folder, without editing the core.
      </p>
      <div className="grid grid-3">
        {modules.map((m) => (
          <div key={m.id} className="card">
            <div className="topbar">
              <h4 style={{ margin: 0 }}>{m.name}</h4>
              <span className="badge status">{m.enabled ? "Enabled" : "Disabled"}</span>
            </div>
            <p className="muted">v{m.version} &middot; API {m.api_version}</p>
            <p style={{ fontSize: 13 }}>{m.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
