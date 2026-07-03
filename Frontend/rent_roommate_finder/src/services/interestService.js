import api from "./api";

export async function expressInterest(listingId) {
  const { data } = await api.post("/api/interest", { listing_id: listingId });
  return data;
}

export async function getSentInterests() {
  const { data } = await api.get("/api/interest/sent");
  return data;
}

export async function getReceivedInterests() {
  const { data } = await api.get("/api/interest/received");
  return data;
}

export async function acceptInterest(interestId) {
  const { data } = await api.patch(`/api/interest/${interestId}/accept`);
  return data;
}

export async function declineInterest(interestId) {
  const { data } = await api.patch(`/api/interest/${interestId}/decline`);
  return data;
}
