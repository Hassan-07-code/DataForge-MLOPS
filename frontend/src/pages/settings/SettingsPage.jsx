import { useState } from "react";
import API_BASE_URL from "../../services/api";
import "./SettingsPage.css";

function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(API_BASE_URL);
  const [mlflowUri, setMlflowUri] = useState("sqlite:///mlflow.db");
  const [cacheStatus, setCacheStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    alert("Settings updated successfully!");
  };

  const handleForceReload = async () => {
    setLoading(true);
    setCacheStatus(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/reload?dataset=iris.csv&model=Random%20Forest`, {
        method: "POST"
      });
      const data = await res.json();
      setCacheStatus(data.message || "Model cache reloaded successfully!");
    } catch (err) {
      setCacheStatus("Cache reload failed. Check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Platform Settings & Diagnostics</h1>
          <p>Configure backend API endpoints, MLflow tracking URI, model cache reloads, and platform preferences.</p>
        </div>
      </div>

      <div className="settings-grid">
        {/* API & Connection Config */}
        <div className="settings-card glass-card">
          <h3>Backend & Endpoint Settings</h3>

          <form onSubmit={handleSave} className="settings-form">
            <div className="form-group">
              <label>FastAPI Backend Server URL</label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>MLflow Experiment Tracking URI</label>
              <input
                type="text"
                value={mlflowUri}
                onChange={(e) => setMlflowUri(e.target.value)}
              />
            </div>

            <button type="submit" className="btn btn-primary">
              💾 Save Configuration
            </button>
          </form>
        </div>

        {/* Model Cache Controls */}
        <div className="settings-card glass-card">
          <h3>Model Cache & Watcher Operations</h3>
          <p>Force reload the active production model in memory or trigger background filesystem watcher re-indexing.</p>

          <div className="cache-actions mt-16">
            <button className="btn btn-secondary" onClick={handleForceReload} disabled={loading}>
              {loading ? <span className="spinner"></span> : "🔄 Force Reload Production Model Cache"}
            </button>

            {cacheStatus && <div className="toast-msg font-mono text-cyan mt-12">✓ {cacheStatus}</div>}
          </div>

          <hr className="divider mt-20" />

          <h4 className="mt-16">System Info</h4>
          <div className="info-list text-dim text-sm mt-10">
            <div>Environment: <strong>Development / Local</strong></div>
            <div>Registry Path: <strong>artifacts/registry/registry.json</strong></div>
            <div>Models Dir: <strong>artifacts/models</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
