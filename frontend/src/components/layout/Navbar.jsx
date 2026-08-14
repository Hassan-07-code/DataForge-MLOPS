import { useState, useEffect } from "react";
import { fetchHealth } from "../../services/systemService";
import "./Layout.css";

function Navbar() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setHealth({ status: "offline" }));
  }, []);

  return (
    <header className="navbar">
      <div className="navbar-left">
        <h2>DataForge Platform</h2>
        <p className="navbar-sub">Machine Learning Operations & Analytics Studio</p>
      </div>

      <div className="navbar-right">
        <div className="search-bar-wrap">
          <svg className="search-icon" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input type="text" placeholder="Search models, datasets, runs..." />
        </div>

        <div className="status-badge-nav">
          <span className={`status-dot ${health?.status === "healthy" ? "" : "offline"}`}></span>
          <span className="status-text">{health?.status === "healthy" ? "Backend Connected" : "Connecting..."}</span>
        </div>

        <div className="profile-chip">
          <div className="profile-avatar">H</div>
          <div className="profile-info">
            <span className="profile-name">Hassan</span>
            <small className="profile-role">AI Engineer</small>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;