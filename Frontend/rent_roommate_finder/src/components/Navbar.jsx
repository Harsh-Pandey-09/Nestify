import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { UserRole } from "../utils/constants";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  function dashboardPath() {
    if (!user) return "/login";
    if (user.role === UserRole.OWNER) return "/owner";
    if (user.role === UserRole.ADMIN) return "/admin";
    return "/tenant";
  }

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">
          <span className="brand-mark" />
          Nestify
        </Link>

        <nav className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/listings">Listings</Link>
          {user && <Link to={dashboardPath()}>Dashboard</Link>}
          {user && <Link to="/profile">Profile</Link>}
        </nav>

        <div className="nav-actions">
          {user ? (
            <>
              <span className="nav-role-tag">{user.role}</span>
              <button className="btn btn-outline btn-sm" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline btn-sm">
                Log in
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Get started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
