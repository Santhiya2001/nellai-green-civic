import { FormEvent, useEffect, useState } from "react";
import { apiClient } from "../../api/client";

interface Authority { id: string; name: string; department: string; level: string; contact_email: string | null; }
interface Rule { id: string; category_code: string; boundary_level: string | null; authority_id: string; priority: number; }

export default function Authorities() {
  const [authorities, setAuthorities] = useState<Authority[]>([]);
  const [rules, setRules] = useState<Rule[]>([]);
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [level, setLevel] = useState("LOCAL_BODY");

  const [ruleCategory, setRuleCategory] = useState("");
  const [ruleAuthorityId, setRuleAuthorityId] = useState("");

  function refresh() {
    apiClient.get<Authority[]>("/authorities").then((res) => setAuthorities(res.data));
    apiClient.get<Rule[]>("/authorities/responsibility-map").then((res) => setRules(res.data));
  }
  useEffect(refresh, []);

  async function createAuthority(e: FormEvent) {
    e.preventDefault();
    await apiClient.post("/authorities", { name, department, level });
    setName(""); setDepartment("");
    refresh();
  }

  async function createRule(e: FormEvent) {
    e.preventDefault();
    await apiClient.post("/authorities/responsibility-map", { category_code: ruleCategory, authority_id: ruleAuthorityId, priority: 0 });
    setRuleCategory(""); setRuleAuthorityId("");
    refresh();
  }

  return (
    <div>
      <h2>Authorities &amp; Responsibility Mapping</h2>
      <div className="grid grid-2">
        <div className="card">
          <h3>Create Authority</h3>
          <form onSubmit={createAuthority}>
            <label>Name</label>
            <input required value={name} onChange={(e) => setName(e.target.value)} />
            <label>Department</label>
            <input required value={department} onChange={(e) => setDepartment(e.target.value)} />
            <label>Level</label>
            <select value={level} onChange={(e) => setLevel(e.target.value)}>
              <option value="LOCAL_BODY">Local Body</option>
              <option value="BLOCK_LEVEL">Block Level</option>
              <option value="DISTRICT_LEVEL">District Level</option>
              <option value="DEPARTMENT">Department</option>
            </select>
            <button className="btn" style={{ marginTop: 14 }}>Create</button>
          </form>
        </div>

        <div className="card">
          <h3>Map Category &rarr; Authority</h3>
          <form onSubmit={createRule}>
            <label>Category code (e.g. DRAIN_BLOCKAGE)</label>
            <input required value={ruleCategory} onChange={(e) => setRuleCategory(e.target.value)} />
            <label>Authority</label>
            <select required value={ruleAuthorityId} onChange={(e) => setRuleAuthorityId(e.target.value)}>
              <option value="">Select...</option>
              {authorities.map((a) => <option key={a.id} value={a.id}>{a.name} ({a.level})</option>)}
            </select>
            <button className="btn" style={{ marginTop: 14 }}>Map</button>
          </form>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Authorities</h3>
        <table>
          <thead><tr><th>Name</th><th>Department</th><th>Level</th></tr></thead>
          <tbody>{authorities.map((a) => <tr key={a.id}><td>{a.name}</td><td>{a.department}</td><td>{a.level}</td></tr>)}</tbody>
        </table>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Responsibility Map</h3>
        <table>
          <thead><tr><th>Category</th><th>Boundary Level</th><th>Authority</th><th>Priority</th></tr></thead>
          <tbody>
            {rules.map((r) => (
              <tr key={r.id}>
                <td>{r.category_code}</td>
                <td>{r.boundary_level || "Any"}</td>
                <td>{authorities.find((a) => a.id === r.authority_id)?.name || r.authority_id}</td>
                <td>{r.priority}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
