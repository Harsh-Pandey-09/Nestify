import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login as loginRequest } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import { UserRole } from "../utils/constants";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const data = await loginRequest({ email, password });
      login(data.access_token, data.user);
      const role = data.user?.role;
      if (role === UserRole.OWNER) navigate("/owner");
      else if (role === UserRole.ADMIN) navigate("/admin");
      else navigate("/tenant");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Could not log in. Check your details."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <div className="container auth-shell">
        <span className="eyebrow">Welcome back</span>
        <h1 style={{ fontSize: "32px" }}>Log in to your account</h1>

        <div className="auth-card" style={{ marginTop: "24px" }}>
          {error && <div className="form-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={submitting}
            >
              {submitting ? "Logging in..." : "Log in"}
            </button>
          </form>
          <p style={{ marginTop: "16px", fontSize: "13px" }}>
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
