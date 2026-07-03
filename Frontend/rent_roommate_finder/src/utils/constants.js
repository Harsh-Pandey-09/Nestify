export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export const UserRole = {
  TENANT: "tenant",
  OWNER: "owner",
  ADMIN: "admin",
};

export const RoomType = {
  PRIVATE_ROOM: "private_room",
  SHARED_ROOM: "shared_room",
  ENTIRE_PLACE: "entire_place",
};

export const FurnishingStatus = {
  FURNISHED: "furnished",
  SEMI_FURNISHED: "semi_furnished",
  UNFURNISHED: "unfurnished",
};

export const ListingStatus = {
  ACTIVE: "active",
  FILLED: "filled",
};

export const InterestStatus = {
  PENDING: "pending",
  ACCEPTED: "accepted",
  DECLINED: "declined",
};

export const NotificationType = {
  HIGH_MATCH_INTEREST: "high_match_interest",
  INTEREST_RECEIVED: "interest_received",
  INTEREST_ACCEPTED: "interest_accepted",
  INTEREST_DECLINED: "interest_declined",
  NEW_MESSAGE: "new_message",
  LISTING_FILLED: "listing_filled",
};

export const roomTypeLabel = (value) =>
  ({
    private_room: "Private room",
    shared_room: "Shared room",
    entire_place: "Entire place",
  }[value] || value);

export const furnishingLabel = (value) =>
  ({
    furnished: "Furnished",
    semi_furnished: "Semi-furnished",
    unfurnished: "Unfurnished",
  }[value] || value);

export const notificationCopy = (type) =>
  ({
    high_match_interest: "New high-match interest",
    interest_received: "New interest received",
    interest_accepted: "Interest accepted",
    interest_declined: "Interest declined",
    new_message: "New message",
    listing_filled: "Listing marked filled",
  }[type] || type);
