import PublicNavbar from "../components/PublicNavbar";
import Footer from "../components/Footer";

export default function Terms() {
  return (
    <div>
      <PublicNavbar />
      <div className="legal-page">
        <h1>Terms of Service</h1>
        <p className="muted">Last updated: 18 September 2026</p>

        <h3>What this platform is</h3>
        <p>
          Nellai Green &amp; Civic lets citizens report civic and environmental issues, lets
          authorities track and resolve them, and lets volunteers organize environmental activities.
          It is a reporting and coordination tool — <strong>not an emergency service</strong>. For a
          life-threatening emergency, contact local emergency services directly.
        </p>

        <h3>Acceptable use</h3>
        <p>
          Don't submit knowingly false reports, abusive or harassing content, or attempt to access
          another user's account. Accounts filing deliberately false or abusive reports may be
          deactivated.
        </p>

        <h3>Land ownership claims</h3>
        <p>
          The afforestation module never asserts that land is government-owned based on satellite
          imagery or map data alone. Any ownership status shown is either <code>UNVERIFIED</code> or
          has been explicitly confirmed by an administrator against official records.
        </p>

        <h3>No warranty</h3>
        <p>
          This is open-source software provided "as is" under the Apache License 2.0. The
          organization deploying this code for a given district is responsible for its own service
          commitments to users.
        </p>

        <p className="muted">
          Full terms source: <code>docs/terms-of-service.md</code> in the project repository.
        </p>
      </div>
      <Footer />
    </div>
  );
}
