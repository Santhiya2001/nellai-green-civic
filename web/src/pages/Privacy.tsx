import PublicNavbar from "../components/PublicNavbar";
import Footer from "../components/Footer";

export default function Privacy() {
  return (
    <div>
      <PublicNavbar />
      <div className="legal-page">
        <h1>Privacy Policy</h1>
        <p className="muted">Last updated: 18 September 2026</p>

        <h3>What we collect</h3>
        <p>
          Name, email, and phone (optional) for your account. GPS location, an optional photo, and a
          description for each complaint you file. Passwords are stored as bcrypt hashes, never in
          plain text.
        </p>

        <h3>Who sees it</h3>
        <p>
          The authority assigned to your complaint and platform administrators can see what's needed
          to resolve it. The public map shows complaint location, category and status —
          <strong> never your name, email or phone number</strong>. We never sell or share your data
          with third parties. The AI classification service only receives the complaint text and
          image, never your identity.
        </p>

        <h3>How long we keep it</h3>
        <p>
          Active account data is kept while your account is active. Complaint records are retained as
          a civic record for the locality, but de-identified if you delete your account.
        </p>

        <h3>Your controls</h3>
        <p>
          You can delete your account at any time from your Profile page. This deactivates your
          account and replaces your personal details with de-identified placeholders — complaints you
          filed remain as public civic record but are no longer linked to you.
        </p>

        <h3>Location data</h3>
        <p>
          Location is only captured when you actively report an issue or use "Nearby Issues" — the app
          does not track your location in the background.
        </p>

        <p className="muted">
          Full policy source: <code>docs/privacy-policy.md</code> in the project repository.
        </p>
      </div>
      <Footer />
    </div>
  );
}
