import { FormEvent, useEffect, useState } from "react";
import { apiClient } from "../../api/client";

interface Rule {
  id: string;
  category_code: string | null;
  deadline_days: number;
  initial_authority_level: string;
  escalation_level_1: string;
  escalation_level_2: string;
  reminder_before_days: number;
  is_active: boolean;
}

export default function EscalationManagement() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [categoryCode, setCategoryCode] = useState("");
  const [deadlineDays, setDeadlineDays] = useState(3);
  const [sweepResult, setSweepResult] = useState<string>("");

  function refresh() {
    apiClient.get<Rule[]>("/escalation/rules").then((res) => setRules(res.data));
  }
  useEffect(refresh, []);

  async function createRule(e: FormEvent) {
    e.preventDefault();
    await apiClient.post("/escalation/rules", {
      category_code: categoryCode || null,
      deadline_days: deadlineDays,
      initial_authority_level: "LOCAL_BODY",
      escalation_level_1: "BLOCK_LEVEL",
      escalation_level_2: "DISTRICT_LEVEL",
      reminder_before_days: 1,
    });
    setCategoryCode("");
    refresh();
  }

  async function runSweep() {
    const { data } = await apiClient.post("/escalation/sweep");
    setSweepResult(`Checked ${data.checked}, reminded ${data.reminded}, escalated ${data.escalated}.`);
  }

  return (
    <div>
      <h2>Escalation Rules</h2>
      <div className="card">
        <form onSubmit={createRule}>
          <label>Category code (blank = default rule)</label>
          <input value={categoryCode} onChange={(e) => setCategoryCode(e.target.value)} placeholder="e.g. DRAIN_BLOCKAGE" />
          <label>Deadline (working days)</label>
          <input type="number" min={1} value={deadlineDays} onChange={(e) => setDeadlineDays(Number(e.target.value))} />
          <button className="btn" style={{ marginTop: 14 }}>Save Rule</button>
        </form>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <div className="topbar">
          <h3 style={{ margin: 0 }}>Configured Rules</h3>
          <button className="btn secondary" onClick={runSweep}>Run Escalation Sweep Now</button>
        </div>
        {sweepResult && <p className="muted">{sweepResult}</p>}
        <table>
          <thead><tr><th>Category</th><th>Deadline (days)</th><th>Level 1</th><th>Level 2</th></tr></thead>
          <tbody>
            {rules.map((r) => (
              <tr key={r.id}>
                <td>{r.category_code || "Default"}</td>
                <td>{r.deadline_days}</td>
                <td>{r.escalation_level_1}</td>
                <td>{r.escalation_level_2}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
