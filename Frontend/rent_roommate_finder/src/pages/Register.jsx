import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register as registerRequest } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import { UserRole } from "../utils/constants";

export default function Register() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: UserRole.TENANT,
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const data = await registerRequest(form);
      login(data.access_token, data.user);
      navigate(form.role === UserRole.OWNER ? "/owner" : "/tenant");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Could not create your account."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <div className="container auth-shell">
        <span className="eyebrow">Join the platform</span>
        <h1 style={{ fontSize: "32px" }}>Create your account</h1>

        <div className="auth-card" style={{ marginTop: "24px" }}>
          {error && <div className="form-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Full name</label>
              <input
                id="name"
                required
                value={form.name}
                onChange={(e) => update("name", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                required
                minLength={6}
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="role">I am a</label>
              <select
                id="role"
                value={form.role}
                onChange={(e) => update("role", e.target.value)}
              >
                <option value={UserRole.TENANT}>Tenant, looking for a room</option>
                <option value={UserRole.OWNER}>Owner, listing a room</option>
              </select>
            </div>
            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={submitting}
            >
              {submitting ? "Creating account..." : "Create account"}
            </button>
          </form>
          <p style={{ marginTop: "16px", fontSize: "13px" }}>
            Already registered? <Link to="/login">Log in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
