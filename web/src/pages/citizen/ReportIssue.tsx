import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../../api/client";
import { Category } from "../../types";
import { extractErrorMessage } from "../../utils/errors";

export default function ReportIssue() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoryCode, setCategoryCode] = useState("");
  const [description, setDescription] = useState("");
  const [addressText, setAddressText] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    apiClient.get<Category[]>("/categories").then((res) => setCategories(res.data));
  }, []);

  function captureLocation() {
    setLocating(true);
    setError("");
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by this browser.");
      setLocating(false);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setLocating(false);
      },
      () => {
        setError("Could not get your location. Please allow location access.");
        setLocating(false);
      }
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (!coords) {
      setError("Please capture your location before submitting.");
      return;
    }
    setBusy(true);
    try {
      const form = new FormData();
      form.append("category_code", categoryCode);
      form.append("description", description);
      form.append("latitude", String(coords.lat));
      form.append("longitude", String(coords.lng));
      if (addressText) form.append("address_text", addressText);
      if (image) form.append("image", image);

      const { data } = await apiClient.post("/complaints", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      navigate(`/citizen/complaints?highlight=${data.id}`);
    } catch (err: any) {
      setError(extractErrorMessage(err, "Could not submit complaint."));
    } finally {
      setBusy(false);
    }
  }

  const groupedByModule = categories.reduce<Record<string, Category[]>>((acc, c) => {
    (acc[c.module_id] ||= []).push(c);
    return acc;
  }, {});

  return (
    <div>
      <h2>Report an Issue</h2>
      <form onSubmit={handleSubmit} className="card form-narrow">
        <label>Category</label>
        <select required value={categoryCode} onChange={(e) => setCategoryCode(e.target.value)}>
          <option value="">Select a category</option>
          {Object.entries(groupedByModule).map(([moduleId, cats]) => (
            <optgroup key={moduleId} label={moduleId}>
              {cats.map((c) => (
                <option key={c.code} value={c.code}>{c.name}</option>
              ))}
            </optgroup>
          ))}
        </select>

        <label>Description</label>
        <textarea required rows={4} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe the issue..." />

        <label>Location</label>
        <button type="button" className="btn secondary" onClick={captureLocation} disabled={locating}>
          {locating ? "Locating..." : coords ? `Captured: ${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}` : "Capture current GPS location"}
        </button>

        <label>Address (optional)</label>
        <input value={addressText} onChange={(e) => setAddressText(e.target.value)} placeholder="Landmark or street name" />

        <label>Photo (optional)</label>
        <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => setImage(e.target.files?.[0] || null)} />

        {error && <div className="error-text">{error}</div>}

        <button className="btn" style={{ marginTop: 18 }} disabled={busy}>
          {busy ? "Submitting..." : "Submit Complaint"}
        </button>
      </form>
    </div>
  );
}
