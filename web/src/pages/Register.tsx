import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { homePathForRoles, useAuth } from "../store/AuthContext";
import Logo from "../components/Logo";
import { extractErrorMessage } from "../utils/errors";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const user = await register(fullName, email, phone, password);
      navigate(homePathForRoles(user.roles));
    } catch (err: any) {
      setError(extractErrorMessage(err, "Could not create account."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Link to="/" className="back-home-link">← Back to home</Link>
        <div className="auth-brand">
          <Logo size={44} />
          <h2>Create your account</h2>
        </div>
        <form onSubmit={handleSubmit}>
          <label>Full name</label>
          <input required value={fullName} onChange={(e) => setFullName(e.target.value)} />
          <label>Email</label>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          <label>Phone (optional)</label>
          <input value={phone} onChange={(e) => setPhone(e.target.value)} />
          <label>Password</label>
          <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} />
          {error && <div className="error-text">{error}</div>}
          <button className="btn" style={{ width: "100%", marginTop: 18 }} disabled={busy}>
            {busy ? "Creating..." : "Create account"}
          </button>
        </form>
        <p className="muted" style={{ marginTop: 16 }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
