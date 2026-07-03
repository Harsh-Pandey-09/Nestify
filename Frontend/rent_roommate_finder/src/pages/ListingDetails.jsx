import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Loader from "../components/Loader";
import { getListing } from "../services/listingService";
import {
  getCompatibility,
  recomputeCompatibility,
} from "../services/profileService";
import { expressInterest } from "../services/interestService";
import { useAuth } from "../context/AuthContext";
import { API_URL, UserRole, roomTypeLabel, furnishingLabel } from "../utils/constants";

export default function ListingDetails() {
  const { listingId } = useParams();
  const { user } = useAuth();
  const [listing, setListing] = useState(null);
  const [compatibility, setCompatibility] = useState(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getListing(listingId)
      .then((data) => !cancelled && setListing(data))
      .finally(() => !cancelled && setLoading(false));

    if (user?.role === UserRole.TENANT) {
      getCompatibility(listingId)
        .then((data) => !cancelled && setCompatibility(data))
        .catch(() => {});
    }
    return () => {
      cancelled = true;
    };
  }, [listingId, user]);

  async function handleRecompute() {
    setStatus("");
    try {
      const data = await recomputeCompatibility(listingId);
      setCompatibility(data);
    } catch {
      setStatus("Could not recompute the score.");
    }
  }

  async function handleInterest() {
    setStatus("");
    try {
      await expressInterest(listingId);
      setStatus("Interest sent. You'll hear back once the owner responds.");
    } catch (err) {
      setStatus(err.response?.data?.detail || "Could not send interest.");
    }
  }

  if (loading) return <Loader />;
  if (!listing) return <div className="container page">Listing not found.</div>;

  const photos = listing.photos
    ? (Array.isArray(listing.photos) ? listing.photos : listing.photos.split(","))
    : [];

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <div>
            <span className="eyebrow">{listing.location}</span>
            <h1>{listing.title}</h1>
          </div>
          <div className="listing-rent">₹{listing.rent}/mo</div>
        </div>

        <div className="grid grid-2" style={{ gridTemplateColumns: "1.4fr 1fr" }}>
          <div>
            {photos.length > 0 ? (
              <img
                src={
                  photos[0].startsWith("http")
                    ? photos[0]
                    : `${API_URL}/${photos[0].replace(/^\//, "")}`
                }
                alt={listing.title}
                style={{
                  width: "100%",
                  height: "360px",
                  objectFit: "cover",
                  borderRadius: "var(--radius-lg)",
                  border: "1px solid var(--color-line)",
                }}
              />
            ) : (
              <div
                style={{
                  height: "360px",
                  borderRadius: "var(--radius-lg)",
                  background: "var(--color-line)",
                }}
              />
            )}

            <div className="card" style={{ marginTop: "24px" }}>
              <h3>About this room</h3>
              <div className="tag-row" style={{ marginBottom: "12px" }}>
                <span className="tag">{roomTypeLabel(listing.room_type)}</span>
                <span className="tag">{furnishingLabel(listing.furnishing_status)}</span>
                <span className="tag">Available {listing.available_from}</span>
              </div>
              <p>{listing.description}</p>
            </div>
          </div>

          <div>
            {user?.role === UserRole.TENANT && (
              <div className="card" style={{ marginBottom: "20px" }}>
                <h3>Compatibility</h3>
                {compatibility ? (
                  <>
                    <div className="listing-rent" style={{ marginBottom: "8px" }}>
                      {compatibility.score}%
                    </div>
                    <p>{compatibility.explanation}</p>
                    <span className="tag">source: {compatibility.source}</span>
                    <button
                      className="link-btn"
                      style={{ display: "block", marginTop: "12px" }}
                      onClick={handleRecompute}
                    >
                      Recompute score
                    </button>
                  </>
                ) : (
                  <p>Complete your tenant profile to see a match score.</p>
                )}
              </div>
            )}

            {user?.role === UserRole.TENANT && (
              <div className="card">
                <h3>Interested?</h3>
                <p>Send an interest and the owner will be notified.</p>
                <button className="btn btn-primary btn-block" onClick={handleInterest}>
                  Express interest
                </button>
                {status && (
                  <p style={{ marginTop: "12px", fontSize: "13px" }}>{status}</p>
                )}
              </div>
            )}

            {!user && (
              <div className="card">
                <h3>Log in to apply</h3>
                <p>Create a tenant account to see your match score and reach out.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
