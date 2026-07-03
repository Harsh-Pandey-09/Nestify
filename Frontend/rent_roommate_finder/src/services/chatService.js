import api from "./api";
import { WS_URL } from "../utils/constants";
import { getToken } from "../utils/auth";

export async function getChatHistory(interestId) {
  const { data } = await api.get(`/api/chat/${interestId}/messages`);
  return data;
}

export function connectChatSocket(interestId) {
  const token = getToken();
  return new WebSocket(
    `${WS_URL}/ws/chat/${interestId}?token=${encodeURIComponent(token)}`
  );
}
