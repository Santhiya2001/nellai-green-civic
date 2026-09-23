import { Link, NavLink, Outlet } from "react-router-dom";
import { API_DOCS_URL } from "../api/client";
import { useAuth } from "../store/AuthContext";
import Logo from "./Logo";

interface NavItem {
  to: string;
  label: string;
}

function navForRole(role: string): NavItem[] {
  switch (role) {
    case "ADMIN":
    case "SUPER_ADMIN":
      return [
        { to: "/admin", label: "Dashboard" },
        { to: "/admin/complaints", label: "Complaints" },
        { to: "/admin/authorities", label: "Authorities" },
        { to: "/admin/escalation", label: "Escalation Rules" },
        { to: "/admin/modules", label: "Modules" },
        { to: "/admin/map", label: "GIS Map" },
      ];
    case "AUTHORITY":
      return [
        { to: "/authority", label: "Assigned Complaints" },
        { to: "/authority/performance", label: "Performance" },
      ];
    default:
      return [
        { to: "/citizen", label: "Dashboard" },
        { to: "/citizen/report", label: "Report Issue" },
        { to: "/citizen/complaints", label: "My Complaints" },
        { to: "/citizen/nearby", label: "Nearby Issues" },
        { to: "/citizen/map", label: "Environmental Map" },
        { to: "/citizen/volunteer", label: "Volunteer Activities" },
        { to: "/citizen/notifications", label: "Notifications" },
      ];
  }
}

export default function Layout() {
  const { user, logout } = useAuth();
  const primaryRole = user?.roles.includes("SUPER_ADMIN")
    ? "SUPER_ADMIN"
    : user?.roles.includes("ADMIN")
    ? "ADMIN"
    : user?.roles.includes("AUTHORITY")
    ? "AUTHORITY"
    : "CITIZEN";

  const items = navForRole(primaryRole);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link to="/" className="sidebar-brand">
          <Logo size={30} />
          <span>Nellai Green &amp; Civic</span>
        </Link>
        <nav>
          {items.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to.split("/").length <= 2}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <Link to="/" className="sidebar-back-link">← Back to public site</Link>
      </aside>
      <div className="app-content-col">
        <main className="main-content">
          <div className="topbar">
            <div className="muted">Signed in as {user?.full_name} ({primaryRole})</div>
            <button className="btn secondary" onClick={logout}>Logout</button>
          </div>
          <Outlet />
        </main>
        <footer className="app-footer">
          <span>Nellai Green &amp; Civic — open source under Apache License 2.0</span>
          <Link to="/privacy">Privacy</Link>
          <Link to="/terms">Terms</Link>
          <a href={API_DOCS_URL} target="_blank" rel="noreferrer">API Docs</a>
        </footer>
      </div>
    </div>
  );
}
