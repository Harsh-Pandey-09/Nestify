import api from "./api";

export async function getMyUser() {
  const { data } = await api.get("/api/users/me");
  return data;
}

export async function updateMyUser(payload) {
  const { data } = await api.put("/api/users/me", payload);
  return data;
}

export async function getTenantProfile() {
  const { data } = await api.get("/api/tenant/profile");
  return data;
}

export async function createTenantProfile(payload) {
  const { data } = await api.post("/api/tenant/profile", payload);
  return data;
}

export async function updateTenantProfile(payload) {
  const { data } = await api.put("/api/tenant/profile", payload);
  return data;
}

export async function getCompatibility(listingId) {
  const { data } = await api.get(`/api/compatibility/${listingId}`);
  return data;
}

export async function recomputeCompatibility(listingId) {
  const { data } = await api.post(`/api/compatibility/${listingId}/recompute`);
  return data;
}
