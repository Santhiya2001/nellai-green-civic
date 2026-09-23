import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../store/AuthContext";
import Logo from "./Logo";

export default function PublicNavbar() {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const homePath = hasRole("ADMIN", "SUPER_ADMIN") ? "/admin" : hasRole("AUTHORITY") ? "/authority" : "/citizen";

  return (
    <header className="public-navbar">
      <div className="public-navbar-inner">
        <Link to="/" className="brand" onClick={() => setMenuOpen(false)}>
          <Logo size={34} />
          <span>Nellai Green &amp; Civic</span>
        </Link>

        <button className="nav-toggle" aria-label="Toggle menu" onClick={() => setMenuOpen((v) => !v)}>
          ☰
        </button>

        <nav className={`public-nav-links ${menuOpen ? "open" : ""}`}>
          <a href="/#modules" onClick={() => setMenuOpen(false)}>Modules</a>
          <a href="/#about" onClick={() => setMenuOpen(false)}>About</a>
          <Link to="/citizen/map" onClick={() => setMenuOpen(false)}>Map</Link>
          <a href="https://github.com/Santhiya2001/nellai-green-civic" target="_blank" rel="noreferrer">GitHub</a>

          {user ? (
            <>
              <button className="btn" onClick={() => { setMenuOpen(false); navigate(homePath); }}>
                Dashboard
              </button>
              <button className="btn secondary" onClick={() => { logout(); setMenuOpen(false); navigate("/"); }}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link className="btn secondary" to="/login" onClick={() => setMenuOpen(false)}>Sign in</Link>
              <Link className="btn" to="/register" onClick={() => setMenuOpen(false)}>Report an Issue</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
