import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Loader from "../components/Loader";
import {
  getMyListings,
  createListing,
  markListingFilled,
  deleteListing,
} from "../services/listingService";
import { getReceivedInterests, acceptInterest, declineInterest } from "../services/interestService";
import { RoomType, FurnishingStatus, roomTypeLabel } from "../utils/constants";

const blankListing = {
  title: "",
  location: "",
  rent: "",
  available_from: "",
  room_type: RoomType.PRIVATE_ROOM,
  furnishing_status: FurnishingStatus.FURNISHED,
  description: "",
};

export default function OwnerDashboard() {
  const [listings, setListings] = useState([]);
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(blankListing);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");

  async function loadAll() {
    setLoading(true);
    const [listingData, interestData] = await Promise.all([
      getMyListings(),
      getReceivedInterests(),
    ]);
    setListings(listingData);
    setInterests(interestData);
    setLoading(false);
  }

  useEffect(() => {
    loadAll();
  }, []);

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    try {
      await createListing({ ...form, rent: Number(form.rent) });
      setForm(blankListing);
      setShowForm(false);
      loadAll();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create listing.");
    }
  }

  async function handleFill(listingId) {
    await markListingFilled(listingId);
    loadAll();
  }

  async function handleDelete(listingId) {
    await deleteListing(listingId);
    loadAll();
  }

  async function handleAccept(interestId) {
    await acceptInterest(interestId);
    loadAll();
  }

  async function handleDecline(interestId) {
    await declineInterest(interestId);
    loadAll();
  }

  const links = [
    { to: "/owner", label: "Overview", end: true },
    { to: "/profile", label: "Profile" },
  ];

  return (
    <div className="page">
      <div className="container layout-with-sidebar">
        <Sidebar title="Owner" links={links} />

        <div>
          <div className="page-header">
            <div>
              <span className="eyebrow">Owner dashboard</span>
              <h1>Your listings</h1>
            </div>
            <button
              className="btn btn-primary"
              onClick={() => setShowForm((prev) => !prev)}
            >
              {showForm ? "Cancel" : "Add listing"}
            </button>
          </div>

          {showForm && (
            <form className="card" onSubmit={handleCreate} style={{ marginBottom: "32px" }}>
              {error && <div className="form-error">{error}</div>}
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="title">Title</label>
                  <input
                    id="title"
                    required
                    value={form.title}
                    onChange={(e) => update("title", e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="location">Location</label>
                  <input
                    id="location"
                    required
                    value={form.location}
                    onChange={(e) => update("location", e.target.value)}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="rent">Rent (monthly)</label>
                  <input
                    id="rent"
                    type="number"
                    required
                    value={form.rent}
                    onChange={(e) => update("rent", e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="available_from">Available from</label>
                  <input
                    id="available_from"
                    type="date"
                    required
                    value={form.available_from}
                    onChange={(e) => update("available_from", e.target.value)}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="room_type">Room type</label>
                  <select
                    id="room_type"
                    value={form.room_type}
                    onChange={(e) => update("room_type", e.target.value)}
                  >
                    {Object.values(RoomType).map((rt) => (
                      <option key={rt} value={rt}>
                        {roomTypeLabel(rt)}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="furnishing_status">Furnishing</label>
                  <select
                    id="furnishing_status"
                    value={form.furnishing_status}
                    onChange={(e) => update("furnishing_status", e.target.value)}
                  >
                    {Object.values(FurnishingStatus).map((fs) => (
                      <option key={fs} value={fs}>
                        {fs}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={form.description}
                  onChange={(e) => update("description", e.target.value)}
                />
              </div>
              <button type="submit" className="btn btn-primary">
                Publish listing
              </button>
            </form>
          )}

          {loading ? (
            <Loader />
          ) : (
            <>
              {listings.length === 0 ? (
                <div className="empty-state">You have not listed a room yet.</div>
              ) : (
                <div className="grid grid-3" style={{ marginBottom: "48px" }}>
                  {listings.map((listing) => (
                    <div key={listing.id} className="card">
                      <Link to={`/listings/${listing.id}`}>
                        <h3>{listing.title}</h3>
                      </Link>
                      <p style={{ marginBottom: "4px" }}>{listing.location}</p>
                      <div className="listing-rent">₹{listing.rent}/mo</div>
                      <span className="status-pill" style={{ marginTop: "8px", display: "inline-block" }}>
                        {listing.status}
                      </span>
                      <div style={{ display: "flex", gap: "8px", marginTop: "16px" }}>
                        {listing.status !== "filled" && (
                          <button
                            className="btn btn-outline btn-sm"
                            onClick={() => handleFill(listing.id)}
                          >
                            Mark filled
                          </button>
                        )}
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(listing.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="page-header">
                <h2>Interests received</h2>
              </div>

              {interests.length === 0 ? (
                <div className="empty-state">No interests yet.</div>
              ) : (
                <div className="card" style={{ padding: 0 }}>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Tenant</th>
                        <th>Listing</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {interests.map((interest) => (
                        <tr key={interest.id}>
                          <td>{interest.tenant_name || interest.tenant?.name}</td>
                          <td>{interest.listing_title || interest.listing?.title}</td>
                          <td>
                            <span className={`status-pill status-${interest.status}`}>
                              {interest.status}
                            </span>
                          </td>
                          <td style={{ display: "flex", gap: "8px" }}>
                            {interest.status === "pending" && (
                              <>
                                <button
                                  className="btn btn-primary btn-sm"
                                  onClick={() => handleAccept(interest.id)}
                                >
                                  Accept
                                </button>
                                <button
                                  className="btn btn-outline btn-sm"
                                  onClick={() => handleDecline(interest.id)}
                                >
                                  Decline
                                </button>
                              </>
                            )}
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
