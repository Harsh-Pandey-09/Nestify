import { notificationCopy } from "../utils/constants";

function timeAgo(isoDate) {
  const diffMs = Date.now() - new Date(isoDate).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function Notification({ notification, onMarkRead }) {
  return (
    <div
      className={`notification-item ${!notification.is_read ? "unread" : ""}`}
    >
      <div>
        <div>
          {!notification.is_read && <span className="notification-dot" />}
          <strong style={{ fontSize: "14px" }}>
            {notificationCopy(notification.type)}
          </strong>
        </div>
        <p style={{ margin: "4px 0 0 0", fontSize: "13px" }}>
          {notification.message}
        </p>
        <span style={{ fontSize: "11px", color: "var(--color-muted)" }}>
          {timeAgo(notification.created_at)}
        </span>
      </div>
      {!notification.is_read && (
        <button className="link-btn" onClick={() => onMarkRead(notification.id)}>
          Mark read
        </button>
      )}
    </div>
  );
}
