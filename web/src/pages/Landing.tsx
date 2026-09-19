import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiClient } from "../api/client";
import PublicNavbar from "../components/PublicNavbar";
import Footer from "../components/Footer";
import { wikimediaFile } from "../utils/wikimedia";

const RIVER_IMG = wikimediaFile("River Under The Gopalasamudram Bridge 01.jpg", 1600);
const TEMPLE_IMG = wikimediaFile("Nellaiappar.jpg");

const GALLERY = [
  {
    src: wikimediaFile("Courtallam (Kutralam) Falls - Tenkasi 02.jpg", 800),
    alt: "Courtallam Falls, Tenkasi",
    caption: "Courtallam Falls",
    credit: "Public domain, Wikimedia Commons",
  },
  {
    src: wikimediaFile("KMTR rainforest canopy.jpg", 800),
    alt: "Rainforest canopy, Kalakad Mundanthurai Tiger Reserve",
    caption: "Kalakad Mundanthurai Tiger Reserve",
    credit: "T. R. Shankar Raman, CC BY 4.0",
  },
  {
    src: wikimediaFile("Paddy field in Tamil Nadu India.jpg", 800),
    alt: "Paddy field in Tamil Nadu",
    caption: "Paddy fields of the Tamirabharani basin",
    credit: "Jperiapandi, CC BY-SA 4.0",
  },
];

interface PublicStats {
  total_complaints: number;
  resolved_complaints: number;
  registered_users: number;
  trees_registered: number;
  volunteer_events: number;
}

const MODULES = [
  { icon: "🚧", name: "Civic", blurb: "Road damage, streetlights, public toilets" },
  { icon: "🌊", name: "Drainage", blurb: "Blockage and stagnation reporting" },
  { icon: "🗑️", name: "Waste", blurb: "Garbage, illegal dumping, plastic waste" },
  { icon: "💧", name: "Neervalam", blurb: "River, lake and canal health tracking" },
  { icon: "🌳", name: "Green Nellai", blurb: "Plantation sites, tree registry, survival" },
  { icon: "🤝", name: "Volunteer Nellai", blurb: "Event scheduling and registration" },
  { icon: "🌱", name: "Agriculture", blurb: "Crop disease and pest reports" },
  { icon: "🦋", name: "Biodiversity", blurb: "Species catalog and sightings" },
  { icon: "⚠️", name: "Disaster", blurb: "Alerts and urgent citizen reports" },
];

export default function Landing() {
  const [stats, setStats] = useState<PublicStats | null>(null);

  useEffect(() => {
    apiClient.get<PublicStats>("/public/stats").then((res) => setStats(res.data)).catch(() => {});
  }, []);

  return (
    <div className="landing">
      <PublicNavbar />

      <section className="hero" style={{ backgroundImage: `linear-gradient(180deg, rgba(11,46,29,0.55), rgba(11,46,29,0.85)), url(${RIVER_IMG})` }}>
        <div className="hero-inner">
          <h1>A Greener, More Accountable Tirunelveli</h1>
          <p>
            Report civic and environmental issues, track them to resolution, and join volunteers
            restoring the Tamirabharani and its surrounding land — all on one open-source platform.
          </p>
          <div className="hero-ctas">
            <Link className="btn btn-lg" to="/register">Report an Issue</Link>
            <Link className="btn btn-lg secondary" to="/citizen/map">Explore the Map</Link>
          </div>
        </div>
      </section>

      <section className="stats-strip">
        <div className="stats-strip-inner">
          <div className="stat"><strong>{stats ? stats.total_complaints : "—"}</strong><span>Issues reported</span></div>
          <div className="stat"><strong>{stats ? stats.resolved_complaints : "—"}</strong><span>Resolved</span></div>
          <div className="stat"><strong>{stats ? stats.registered_users : "—"}</strong><span>Citizens registered</span></div>
          <div className="stat"><strong>{stats ? stats.trees_registered : "—"}</strong><span>Trees registered</span></div>
          <div className="stat"><strong>{stats ? stats.volunteer_events : "—"}</strong><span>Volunteer events</span></div>
        </div>
      </section>

      <section className="section-pad" id="about">
        <div className="about-grid">
          <img src={TEMPLE_IMG} alt="Nellaiappar Temple, Tirunelveli" className="about-image" />
          <div>
            <h2>Built for Tirunelveli, designed to grow beyond it</h2>
            <p>
              Nellai Green &amp; Civic combines civic issue reporting, drainage and waste tracking,
              water-resource monitoring, afforestation, and volunteer coordination in one platform —
              with a GIS-grounded core that automatically routes every report to the right authority
              and escalates it if it's missed.
            </p>
            <p>
              The entire codebase is open source under the Apache License 2.0. Every feature area is
              an independent module, so a developer can add a new one — flood monitoring, a school
              environmental club, a temple water-tank tracker — without touching the core platform.
            </p>
            <Link className="btn" to="/register">Get started as a citizen</Link>
          </div>
        </div>
      </section>

      <section className="section-pad" id="gallery">
        <h2 className="section-title">The Land This Platform Protects</h2>
        <p className="section-subtitle">Tirunelveli's rivers, forests and farmland — the reason Green Nellai, Neervalam and Agriculture exist as modules.</p>
        <div className="gallery-grid">
          {GALLERY.map((g) => (
            <figure className="gallery-item" key={g.caption}>
              <img src={g.src} alt={g.alt} loading="lazy" />
              <figcaption>
                <strong>{g.caption}</strong>
                <span>{g.credit}</span>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section className="section-pad section-tint" id="modules">
        <h2 className="section-title">Nine Feature Modules</h2>
        <p className="section-subtitle">Every one built on the same generic, GIS-grounded complaint engine.</p>
        <div className="module-grid">
          {MODULES.map((m) => (
            <div className="module-card" key={m.name}>
              <div className="module-icon">{m.icon}</div>
              <h4>{m.name}</h4>
              <p>{m.blurb}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="cta-banner">
        <h2>Volunteers make the difference.</h2>
        <p>Join a tree-planting drive, a lake cleanup, or a biodiversity survey near you.</p>
        <Link className="btn btn-lg" to="/register">Join as a Volunteer</Link>
      </section>

      <Footer />
    </div>
  );
}
