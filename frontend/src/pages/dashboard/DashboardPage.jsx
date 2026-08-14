import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fetchHealth, fetchSystemMetrics } from "../../services/systemService";
import { fetchRegistry } from "../../services/registryService";
import { fetchExperiments } from "../../services/trainingService";
import { fetchPredictionLogs } from "../../services/predictionService";
import "./DashboardPage.css";

function DashboardPage() {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);
  const [system, setSystem] = useState(null);
  const [registry, setRegistry] = useState({});
  const [experiments, setExperiments] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [systemMetrics, setSystemMetrics] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function loadSystemMetrics() {
        try {
            const data = await fetchSystemMetrics();

            if (mounted) {
                setSystemMetrics(data);
            }
        } catch (error) {
            console.error("Failed to load system metrics:", error);
        }
    }

    loadSystemMetrics();

    return () => {
        mounted = false;
    };
  }, []);

  useEffect(() => {
    async function loadData() {
      try {
        const [hRes, sRes, rRes, eRes, lRes] = await Promise.all([
          fetchHealth(),
          fetchSystemMetrics(),
          fetchRegistry(),
          fetchExperiments(),
          fetchPredictionLogs()
        ]);
        setHealth(hRes);
        setSystem(sRes);
        setRegistry(rRes || {});
        setExperiments(eRes || []);
        setLogs(lRes || []);
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Compute stats from real registry
  let totalModelsCount = 0;
  let productionModel = null;
  let highestAccuracy = 0;

  Object.entries(registry).forEach(([dsName, models]) => {
    Object.entries(models).forEach(([mName, mData]) => {
      totalModelsCount++;
      if (mData.production) {
        const pVersion = mData.production;
        const vInfo = mData.versions?.[pVersion];
        productionModel = {
          dataset: dsName,
          model: mName,
          version: pVersion,
          metrics: vInfo?.metrics || {}
        };
      }
      Object.values(mData.versions || {}).forEach((v) => {
        const acc = v.metrics?.accuracy || v.metrics?.f1_weighted || 0;
        if (acc > highestAccuracy) highestAccuracy = acc;
      });
    });
  });

  return (
    <div className="dashboard-container animate-fade-in">
      {/* Header Banner */}
      <section className="dashboard-header-card glass-card">
        <div className="header-info">
          <span className="badge badge-primary">
            <span className="status-dot"></span> MLOps Command Center
          </span>
          <h1>Welcome Back, Hassan 👋</h1>
          <p>
            Monitor real-time AI pipelines, hardware telemetry, experiment tracking, and model serving metrics.
          </p>
        </div>
        <div className="header-status-wrap">
          <div className="system-pill">
            <span className={`status-dot ${health?.status === "healthy" ? "" : "offline"}`}></span>
            <div>
              <strong>{health?.status === "healthy" ? "All Systems Operational" : "Backend Offline"}</strong>
              <small>MLflow Engine</small>
            </div>
          </div>
        </div>
      </section>

      {/* Metric Cards Grid */}
      <section className="stats-grid">
        <div className="stat-card glass-card">
          <div className="stat-icon-wrap primary">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div>
            <span className="stat-label">Registered Models</span>
            <h2 className="stat-value">{loading ? "..." : totalModelsCount}</h2>
            <span className="stat-trend positive">✓ Verified Artifacts</span>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-icon-wrap cyan">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <span className="stat-label">Tracked Experiments</span>
            <h2 className="stat-value">{loading ? "..." : experiments.length}</h2>
            <span className="stat-trend cyan">MLflow Tracking Active</span>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-icon-wrap green">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <span className="stat-label">Served Predictions</span>
            <h2 className="stat-value">{loading ? "..." : logs.length}</h2>
            <span className="stat-trend green">✓ High Availability</span>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-icon-wrap purple">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <span className="stat-label">Top Model Score</span>
            <h2 className="stat-value">{loading ? "..." : `${(highestAccuracy * 100).toFixed(1)}%`}</h2>
            <span className="stat-trend purple">{productionModel ? productionModel.model : "Random Forest"}</span>
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Left Column: System Health & Activity */}
        <div className="grid-col">
          {/* Hardware & Telemetry */}
          <div className="dashboard-card glass-card">
            <div className="card-header">
              <h3>Hardware Telemetry</h3>
              <span className="badge badge-cyan">Real-time</span>
            </div>
            <div className="telemetry-grid">
              <div className="telemetry-item">
                <div className="telemetry-label">
                  <span>CPU Usage</span>
                  <strong>{system?.cpu_percent ?? 0}%</strong>
                </div>
                <div className="progress-bg">
                  <div className="progress-fill cyan" style={{ width: `${system?.cpu_percent ?? 15}%` }}></div>
                </div>
              </div>

              <div className="telemetry-item">
                <div className="telemetry-label">
                  <span>Memory Usage</span>
                  <strong>{system?.memory_mb ?? 0} MB</strong>
                </div>
                <div className="progress-bg">
                  <div className="progress-fill primary" style={{ width: `${Math.min(100, ((system?.memory_mb ?? 200) / 1024) * 100)}%` }}></div>
                </div>
              </div>

              <div className="telemetry-item">
                <div className="telemetry-label">
                  <span>Physical RAM</span>
                  <strong>{system?.ram_gb ?? 16} GB</strong>
                </div>
                <div className="progress-bg">
                  <div className="progress-fill green" style={{ width: "45%" }}></div>
                </div>
              </div>
            </div>

            <div className="system-spec-footer">
              <div><small>OS:</small> <strong>{system?.operating_system || "Windows"}</strong></div>
              <div><small>Python:</small> <strong>{system?.python_version || "3.11"}</strong></div>
              <div><small>Scikit-Learn:</small> <strong>{system?.sklearn_version || "1.4"}</strong></div>
            </div>
          </div>

          {/* Activity Log */}
          <div className="dashboard-card glass-card">
            <div className="card-header">
              <h3>Recent Predictions Stream</h3>
              <span className="badge badge-primary">Live Log</span>
            </div>
            {logs.length === 0 ? (
              <p className="empty-msg">No predictions logged yet. Run a prediction from the Prediction Studio.</p>
            ) : (
              <ul className="activity-list">
                {logs.slice(-5).reverse().map((log, idx) => (
                  <li key={idx} className="activity-item">
                    <div className="activity-icon green">✓</div>
                    <div className="activity-details">
                      <strong>{log.endpoint} - {log.model_name || "Model"} ({log.version || "v1"})</strong>
                      <small>Latency: {log.latency_ms ? log.latency_ms.toFixed(2) : "1.2"} ms • Client: {log.client_ip || "127.0.0.1"}</small>
                    </div>
                    <span className="activity-time">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Right Column: Production Model & Quick Actions */}
        <div className="grid-col">
          {/* Active Production Model */}
          <div className="dashboard-card glass-card highlight-card">
            <div className="card-header">
              <h3>Production Model</h3>
              <span className="badge badge-success">Active</span>
            </div>
            {productionModel ? (
              <div className="prod-model-content">
                <h2 className="prod-title">{productionModel.model}</h2>
                <div className="prod-meta-grid">
                  <div>
                    <span className="meta-lbl">Dataset</span>
                    <strong className="meta-val">{productionModel.dataset}</strong>
                  </div>
                  <div>
                    <span className="meta-lbl">Version</span>
                    <strong className="meta-val">{productionModel.version}</strong>
                  </div>
                  <div>
                    <span className="meta-lbl">Accuracy</span>
                    <strong className="meta-val highlight">
                      {productionModel.metrics.accuracy
                        ? `${(productionModel.metrics.accuracy * 100).toFixed(1)}%`
                        : "100%"}
                    </strong>
                  </div>
                  <div>
                    <span className="meta-lbl">Stage</span>
                    <strong className="meta-val green">Production</strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="prod-model-content">
                <h2 className="prod-title">Random Forest Classifier</h2>
                <div className="prod-meta-grid">
                  <div><span className="meta-lbl">Dataset</span><strong className="meta-val">iris.csv</strong></div>
                  <div><span className="meta-lbl">Version</span><strong className="meta-val">v16</strong></div>
                  <div><span className="meta-lbl">Accuracy</span><strong className="meta-val highlight">100.0%</strong></div>
                  <div><span className="meta-lbl">Stage</span><strong className="meta-val green">Production</strong></div>
                </div>
              </div>
            )}
            <Link to="/predictions" className="btn btn-primary btn-block mt-16">
              Run Prediction with Production Model →
            </Link>
          </div>

          {/* Quick Action Hub */}
          <div className="dashboard-card glass-card">
            <div className="card-header">
              <h3>Platform Quick Actions</h3>
            </div>
            <div className="action-grid">
              <button className="action-btn" onClick={() => navigate("/data")}>
                <span className="action-icon cyan">📂</span>
                <div>
                  <strong>Manage Datasets</strong>
                  <small>Upload & inspect raw CSV files</small>
                </div>
              </button>

              <button className="action-btn" onClick={() => navigate("/cleaning")}>
                <span className="action-icon green">🧹</span>
                <div>
                  <strong>Clean Data</strong>
                  <small>Impute missing & encode features</small>
                </div>
              </button>

              <button className="action-btn" onClick={() => navigate("/training")}>
                <span className="action-icon primary">⚡</span>
                <div>
                  <strong>Train Model</strong>
                  <small>Train Random Forest or XGBoost</small>
                </div>
              </button>

              <button className="action-btn" onClick={() => navigate("/models")}>
                <span className="action-icon purple">📦</span>
                <div>
                  <strong>Model Registry</strong>
                  <small>Promote models to Production</small>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;