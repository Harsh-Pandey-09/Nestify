import api from "./api";

export async function getNotifications() {
  const { data } = await api.get("/api/notifications");
  return data;
}

export async function markNotificationRead(notificationId, isRead = true) {
  const { data } = await api.patch(`/api/notifications/${notificationId}/read`, {
    is_read: isRead,
  });
  return data;
}
