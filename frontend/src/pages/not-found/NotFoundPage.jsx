import { Link } from "react-router-dom";
import "./NotFoundPage.css";

function NotFoundPage() {
  return (
    <div className="not-found-page animate-fade-in">
      <div className="not-found-card glass-card">
        <span className="error-code">404</span>
        <h2>Page Not Found</h2>
        <p>The MLOps pipeline route you requested does not exist or has been relocated.</p>
        <Link to="/dashboard" className="btn btn-primary mt-20">
          ← Return to Command Center
        </Link>
      </div>
    </div>
  );
}

export default NotFoundPage;
