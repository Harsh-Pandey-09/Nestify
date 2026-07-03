import { Link } from "react-router-dom";
import { API_URL } from "../utils/constants";
import { roomTypeLabel } from "../utils/constants";

function firstPhoto(photos) {
  if (!photos) return null;
  const list = Array.isArray(photos) ? photos : photos.split(",");
  const first = list.find(Boolean);
  if (!first) return null;
  return first.startsWith("http") ? first : `${API_URL}/${first.replace(/^\//, "")}`;
}

export default function ListingCard({ listing }) {
  const photo = firstPhoto(listing.photos);
  const score = listing.compatibility_score;

  return (
    <Link to={`/listings/${listing.id}`} className="listing-card">
      {photo ? (
        <img src={photo} alt={listing.title} className="listing-card-photo" />
      ) : (
        <div className="listing-card-photo" />
      )}
      <div className="listing-card-body">
        <div className="listing-card-top">
          <div>
            <h3 style={{ fontSize: "18px", marginBottom: 2 }}>{listing.title}</h3>
            <div className="listing-location">{listing.location}</div>
          </div>
          {typeof score === "number" && (
            <span className={`score-badge ${score < 50 ? "low" : ""}`}>
              {score}% match
            </span>
          )}
        </div>

        <div className="listing-rent">₹{listing.rent}/mo</div>

        <div className="tag-row">
          <span className="tag">{roomTypeLabel(listing.room_type)}</span>
          <span className="tag">{listing.furnishing_status}</span>
        </div>
      </div>
    </Link>
  );
}
