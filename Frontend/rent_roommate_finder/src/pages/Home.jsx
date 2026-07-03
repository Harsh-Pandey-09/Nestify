import { Link } from "react-router-dom";

const features = [
  {
    title: "AI compatibility scoring",
    body: "Every listing is scored against your budget and preferred location, so the best fits rise to the top.",
  },
  {
    title: "Direct messaging",
    body: "Once an owner accepts your interest, chat opens instantly to sort out visits and details.",
  },
  {
    title: "Verified listings",
    body: "Owners manage rent, availability and photos directly, kept current at all times.",
  },
  {
    title: "One place for everything",
    body: "Track interests, notifications and conversations from a single dashboard.",
  },
];

export default function Home() {
  return (
    <div className="page">
      <div className="container">
        <section className="hero">
          <div>
            <span className="eyebrow">Nestify</span>
            <h1>A calmer way to find your next room and flatmate</h1>
            <p>
              Search real listings, see a compatibility score for each one
              based on your budget and location, and message owners once
              they accept your interest.
            </p>
            <div className="hero-actions">
              <Link to="/listings" className="btn btn-primary">
                Browse listings
              </Link>
              <Link to="/register" className="btn btn-outline">
                Create an account
              </Link>
            </div>
            <div className="hero-proof">
              Trusted by tenants and owners matching rooms every day.
            </div>
          </div>

          <div
            className="hero-photo"
            style={{
              background:
                "linear-gradient(160deg, var(--color-purple) 0%, var(--color-purple-dark) 100%)",
              height: "420px",
            }}
          />
        </section>

        <section className="section-band">
          <span className="eyebrow">Why it works</span>
          <h2>Matching made personal</h2>
          <p>
            Every listing you see is ranked for you, not just sorted by
            price, so the room that fits your life is easy to find.
          </p>
          <div className="feature-list">
            {features.map((feature) => (
              <div className="feature-item" key={feature.title}>
                <div className="feature-icon">•</div>
                <h3 style={{ fontSize: "16px" }}>{feature.title}</h3>
                <p style={{ marginBottom: 0 }}>{feature.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="page-header">
          <div>
            <span className="eyebrow">Get started</span>
            <h2>Ready when you are</h2>
          </div>
          <Link to="/listings" className="btn btn-primary">
            View all listings
          </Link>
        </section>
      </div>
    </div>
  );
}
