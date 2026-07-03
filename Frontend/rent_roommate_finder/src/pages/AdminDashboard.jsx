import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Loader from "../components/Loader";
import api from "../services/api";

export default function AdminDashboard() {
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("users");

  async function loadAll() {
    setLoading(true);
    const [summaryRes, usersRes, listingsRes] = await Promise.all([
      api.get("/api/admin/activity"),
      api.get("/api/admin/users"),
      api.get("/api/admin/listings"),
    ]);
    setSummary(summaryRes.data);
    setUsers(usersRes.data);
    setListings(listingsRes.data);
    setLoading(false);
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function deactivateUser(userId) {
    await api.delete(`/api/admin/users/${userId}`);
    loadAll();
  }

  async function deleteListing(listingId) {
    await api.delete(`/api/admin/listings/${listingId}`);
    loadAll();
  }

  const links = [{ to: "/admin", label: "Overview", end: true }];

  if (loading) return <Loader />;

  return (
    <div className="page">
      <div className="container layout-with-sidebar">
        <Sidebar title="Admin" links={links} />

        <div>
          <div className="page-header">
            <div>
              <span className="eyebrow">Admin dashboard</span>
              <h1>Platform activity</h1>
            </div>
          </div>

          {summary && (
            <div className="stat-row">
              {Object.entries(summary).map(([key, value]) => (
                <div className="stat-card" key={key}>
                  <div className="stat-value">{value}</div>
                  <div className="stat-label">{key.replace(/_/g, " ")}</div>
                </div>
              ))}
            </div>
          )}

          <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
            <button
              className={`btn btn-sm ${tab === "users" ? "btn-primary" : "btn-outline"}`}
              onClick={() => setTab("users")}
            >
              Users
            </button>
            <button
              className={`btn btn-sm ${tab === "listings" ? "btn-primary" : "btn-outline"}`}
              onClick={() => setTab("listings")}
            >
              Listings
            </button>
          </div>

          {tab === "users" ? (
            <div className="card" style={{ padding: 0 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td>{u.name}</td>
                      <td>{u.email}</td>
                      <td>{u.role}</td>
                      <td>{u.is_active ? "Active" : "Deactivated"}</td>
                      <td>
                        {u.is_active && (
                          <button
                            className="link-btn"
                            onClick={() => deactivateUser(u.id)}
                          >
                            Deactivate
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="card" style={{ padding: 0 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Location</th>
                    <th>Rent</th>
                    <th>Status</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {listings.map((l) => (
                    <tr key={l.id}>
                      <td>{l.title}</td>
                      <td>{l.location}</td>
                      <td>₹{l.rent}</td>
                      <td>{l.status}</td>
                      <td>
                        <button className="link-btn" onClick={() => deleteListing(l.id)}>
                          Delete
                        </button>
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
