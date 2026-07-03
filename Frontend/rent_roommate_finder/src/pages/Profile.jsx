import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import Loader from "../components/Loader";
import NotificationItem from "../components/Notification";
import {
  getTenantProfile,
  createTenantProfile,
  updateTenantProfile,
  updateMyUser,
} from "../services/profileService";
import { getNotifications, markNotificationRead } from "../services/notificationService";
import { UserRole } from "../utils/constants";

const blankProfile = {
  preferred_location: "",
  budget_min: "",
  budget_max: "",
  move_in_date: "",
  notes: "",
};

export default function Profile() {
  const { user, setUser } = useAuth();
  const [accountForm, setAccountForm] = useState({ name: user?.name || "", password: "" });
  const [profile, setProfile] = useState(blankProfile);
  const [hasProfile, setHasProfile] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");

  useEffect(() => {
    async function load() {
      const notifData = await getNotifications().catch(() => []);
      setNotifications(notifData);

      if (user?.role === UserRole.TENANT) {
        try {
          const data = await getTenantProfile();
          setProfile(data);
          setHasProfile(true);
        } catch {
          setHasProfile(false);
        }
      }
      setLoading(false);
    }
    load();
  }, [user]);

  function updateAccount(field, value) {
    setAccountForm((prev) => ({ ...prev, [field]: value }));
  }

  function updateProfile(field, value) {
    setProfile((prev) => ({ ...prev, [field]: value }));
  }

  async function handleAccountSubmit(e) {
    e.preventDefault();
    const payload = { name: accountForm.name };
    if (accountForm.password) payload.password = accountForm.password;
    const updated = await updateMyUser(payload);
    setUser(updated);
    setStatus("Account details updated.");
  }

  async function handleProfileSubmit(e) {
    e.preventDefault();
    const payload = {
      ...profile,
      budget_min: Number(profile.budget_min),
      budget_max: Number(profile.budget_max),
    };
    const saved = hasProfile
      ? await updateTenantProfile(payload)
      : await createTenantProfile(payload);
    setProfile(saved);
    setHasProfile(true);
    setStatus("Tenant profile saved.");
  }

  async function handleMarkRead(id) {
    await markNotificationRead(id, true);
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
  }

  if (loading) return <Loader />;

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <div>
            <span className="eyebrow">Account</span>
            <h1>Your profile</h1>
          </div>
        </div>

        {status && <div className="form-success">{status}</div>}

        <div className="grid grid-2">
          <div className="card">
            <h3>Account details</h3>
            <form onSubmit={handleAccountSubmit}>
              <div className="form-group">
                <label htmlFor="name">Full name</label>
                <input
                  id="name"
                  value={accountForm.name}
                  onChange={(e) => updateAccount("name", e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="new-password">New password (optional)</label>
                <input
                  id="new-password"
                  type="password"
                  value={accountForm.password}
                  onChange={(e) => updateAccount("password", e.target.value)}
                />
              </div>
              <button type="submit" className="btn btn-primary">
                Save changes
              </button>
            </form>
          </div>

          {user?.role === UserRole.TENANT && (
            <div className="card">
              <h3>Rental preferences</h3>
              <form onSubmit={handleProfileSubmit}>
                <div className="form-group">
                  <label htmlFor="preferred_location">Preferred location</label>
                  <input
                    id="preferred_location"
                    required
                    value={profile.preferred_location}
                    onChange={(e) => updateProfile("preferred_location", e.target.value)}
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="budget_min">Min budget</label>
                    <input
                      id="budget_min"
                      type="number"
                      required
                      value={profile.budget_min}
                      onChange={(e) => updateProfile("budget_min", e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="budget_max">Max budget</label>
                    <input
                      id="budget_max"
                      type="number"
                      required
                      value={profile.budget_max}
                      onChange={(e) => updateProfile("budget_max", e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="move_in_date">Move-in date</label>
                  <input
                    id="move_in_date"
                    type="date"
                    required
                    value={profile.move_in_date}
                    onChange={(e) => updateProfile("move_in_date", e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="notes">Notes</label>
                  <textarea
                    id="notes"
                    value={profile.notes || ""}
                    onChange={(e) => updateProfile("notes", e.target.value)}
                  />
                </div>
                <button type="submit" className="btn btn-primary">
                  {hasProfile ? "Update preferences" : "Save preferences"}
                </button>
              </form>
            </div>
          )}
        </div>

        <div className="page-header" style={{ marginTop: "48px" }}>
          <h2>Notifications</h2>
        </div>
        <div className="card" style={{ padding: 0 }}>
          {notifications.length === 0 ? (
            <div className="empty-state">You're all caught up.</div>
          ) : (
            notifications.map((n) => (
              <NotificationItem key={n.id} notification={n} onMarkRead={handleMarkRead} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
