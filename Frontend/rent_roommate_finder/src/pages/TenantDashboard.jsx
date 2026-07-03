import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Loader from "../components/Loader";
import { getSentInterests } from "../services/interestService";

export default function TenantDashboard() {
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSentInterests()
      .then(setInterests)
      .finally(() => setLoading(false));
  }, []);

  const links = [
    { to: "/tenant", label: "Overview", end: true },
    { to: "/profile", label: "Profile" },
  ];

  return (
    <div className="page">
      <div className="container layout-with-sidebar">
        <Sidebar title="Tenant" links={links} />

        <div>
          <div className="page-header">
            <div>
              <span className="eyebrow">Tenant dashboard</span>
              <h1>Your interests</h1>
            </div>
            <Link to="/listings" className="btn btn-primary">
              Browse more listings
            </Link>
          </div>

          {loading ? (
            <Loader />
          ) : interests.length === 0 ? (
            <div className="empty-state">
              You haven't expressed interest in any listings yet.
            </div>
          ) : (
            <div className="card" style={{ padding: 0 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Listing</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {interests.map((interest) => (
                    <tr key={interest.id}>
                      <td>
                        <Link to={`/listings/${interest.listing_id}`}>
                          {interest.listing_title || interest.listing?.title || `#${interest.listing_id}`}
                        </Link>
                      </td>
                      <td>
                        <span className={`status-pill status-${interest.status}`}>
                          {interest.status}
                        </span>
                      </td>
                      <td>
                        {interest.status === "accepted" && (
                          <Link to={`/chat/${interest.id}`} className="link-btn">
                            Open chat
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
