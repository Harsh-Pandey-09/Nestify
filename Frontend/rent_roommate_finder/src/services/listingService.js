import api from "./api";

export async function browseListings(params = {}) {
  const { data } = await api.get("/api/listings", { params });
  return data;
}

export async function getListing(listingId) {
  const { data } = await api.get(`/api/listings/${listingId}`);
  return data;
}

export async function getMyListings() {
  const { data } = await api.get("/api/listings/owner/mine");
  return data;
}

export async function createListing(payload) {
  const { data } = await api.post("/api/listings", payload);
  return data;
}

export async function updateListing(listingId, payload) {
  const { data } = await api.put(`/api/listings/${listingId}`, payload);
  return data;
}

export async function deleteListing(listingId) {
  const { data } = await api.delete(`/api/listings/${listingId}`);
  return data;
}

export async function markListingFilled(listingId) {
  const { data } = await api.patch(`/api/listings/${listingId}/fill`);
  return data;
}

export async function uploadListingPhotos(listingId, files) {
  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("files", file));
  const { data } = await api.post(
    `/api/listings/${listingId}/photos`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}
