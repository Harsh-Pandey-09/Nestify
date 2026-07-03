import { useParams, Link } from "react-router-dom";
import ChatBox from "../components/ChatBox";
import { useAuth } from "../context/AuthContext";

export default function Chat() {
  const { interestId } = useParams();
  const { user } = useAuth();

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <div>
            <span className="eyebrow">Conversation</span>
            <h1>Chat</h1>
          </div>
          <Link to="/profile" className="link-btn">
            Back to dashboard
          </Link>
        </div>

        <ChatBox interestId={interestId} currentUserId={user?.id} />
      </div>
    </div>
  );
}
