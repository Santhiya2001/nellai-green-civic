import { Link } from "react-router-dom";
import { API_DOCS_URL } from "../api/client";
import Logo from "./Logo";

const REPO_URL = "https://github.com/Santhiya2001/nellai-green-civic";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div className="footer-col footer-brand">
          <div className="brand" style={{ color: "white" }}>
            <Logo size={34} />
            <span>Nellai Green &amp; Civic</span>
          </div>
          <p>
            An open-source, modular civic and environmental management platform for
            Tirunelveli — built so it can grow into a reusable framework for other
            districts and cities.
          </p>
        </div>

        <div className="footer-col">
          <h4>Platform</h4>
          <a href="/#modules">Modules</a>
          <Link to="/citizen/map">Environmental Map</Link>
          <Link to="/register">Report an Issue</Link>
          <Link to="/login">Sign in</Link>
        </div>

        <div className="footer-col">
          <h4>Resources</h4>
          <a href={API_DOCS_URL} target="_blank" rel="noreferrer">API Documentation</a>
          <a href={REPO_URL} target="_blank" rel="noreferrer">Source Code</a>
          <a href={`${REPO_URL}/blob/main/docs/module-development.md`} target="_blank" rel="noreferrer">Contribute a Module</a>
        </div>

        <div className="footer-col">
          <h4>Legal</h4>
          <Link to="/privacy">Privacy Policy</Link>
          <Link to="/terms">Terms of Service</Link>
          <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank" rel="noreferrer">Apache License 2.0</a>
        </div>
      </div>
      <div className="footer-bottom">
        <span>© {new Date().getFullYear()} Nellai Green &amp; Civic — Open source under Apache License 2.0</span>
        <span>Tirunelveli, Tamil Nadu, India</span>
      </div>
    </footer>
  );
}
