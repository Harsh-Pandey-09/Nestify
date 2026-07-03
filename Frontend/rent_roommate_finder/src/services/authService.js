import api from "./api";

export async function register({ name, email, password, role }) {
  const { data } = await api.post("/api/auth/register", {
    name,
    email,
    password,
    role,
  });
  return data;
}

export async function login({ email, password }) {
  const { data } = await api.post("/api/auth/login", { email, password });
  return data;
}

export async function getCurrentUser() {
  const { data } = await api.get("/api/auth/me");
  return data;
}
