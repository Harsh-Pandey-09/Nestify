import { useEffect, useState } from "react";
import ListingCard from "../components/ListingCard";
import Loader from "../components/Loader";
import { browseListings } from "../services/listingService";
import { RoomType, roomTypeLabel } from "../utils/constants";

const emptyFilters = {
  location: "",
  min_budget: "",
  max_budget: "",
  room_type: "",
  sort_by: "compatibility",
};

export default function Listings() {
  const [filters, setFilters] = useState(emptyFilters);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchListings(activeFilters) {
    setLoading(true);
    setError("");
    try {
      const cleaned = Object.fromEntries(
        Object.entries(activeFilters).filter(([, v]) => v !== "")
      );
      const data = await browseListings(cleaned);
      setListings(data.items || data.results || data || []);
    } catch (err) {
      setError("Could not load listings right now.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchListings(emptyFilters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleFilterSubmit(e) {
    e.preventDefault();
    fetchListings(filters);
  }

  function update(field, value) {
    setFilters((prev) => ({ ...prev, [field]: value }));
  }

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <div>
            <span className="eyebrow">Browse</span>
            <h1>Rooms and rentals</h1>
          </div>
        </div>

        <form className="card" onSubmit={handleFilterSubmit} style={{ marginBottom: "32px" }}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="location">Location</label>
              <input
                id="location"
                placeholder="e.g. Koramangala"
                value={filters.location}
                onChange={(e) => update("location", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="room_type">Room type</label>
              <select
                id="room_type"
                value={filters.room_type}
                onChange={(e) => update("room_type", e.target.value)}
              >
                <option value="">Any</option>
                {Object.values(RoomType).map((rt) => (
                  <option key={rt} value={rt}>
                    {roomTypeLabel(rt)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="min_budget">Min budget</label>
              <input
                id="min_budget"
                type="number"
                value={filters.min_budget}
                onChange={(e) => update("min_budget", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="max_budget">Max budget</label>
              <input
                id="max_budget"
                type="number"
                value={filters.max_budget}
                onChange={(e) => update("max_budget", e.target.value)}
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="sort_by">Sort by</label>
              <select
                id="sort_by"
                value={filters.sort_by}
                onChange={(e) => update("sort_by", e.target.value)}
              >
                <option value="compatibility">Best match</option>
                <option value="rent_asc">Rent: low to high</option>
                <option value="rent_desc">Rent: high to low</option>
                <option value="newest">Newest</option>
              </select>
            </div>
            <div style={{ display: "flex", alignItems: "flex-end" }}>
              <button type="submit" className="btn btn-primary btn-block">
                Apply filters
              </button>
            </div>
          </div>
        </form>

        {error && <div className="form-error">{error}</div>}

        {loading ? (
          <Loader />
        ) : listings.length === 0 ? (
          <div className="empty-state">No listings match these filters yet.</div>
        ) : (
          <div className="grid grid-3">
            {listings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
