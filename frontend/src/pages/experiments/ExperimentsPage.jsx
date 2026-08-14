import { useState, useEffect } from "react";
import { fetchExperiments } from "../../services/trainingService";
import "./ExperimentsPage.css";

function ExperimentsPage() {
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterModel, setFilterModel] = useState("all");

  useEffect(() => {
    fetchExperiments()
      .then((data) => setExperiments(data || []))
      .finally(() => setLoading(false));
  }, []);

  const filtered = filterModel === "all"
    ? experiments
    : experiments.filter((e) => e.model === filterModel);

  const uniqueModels = Array.from(new Set(experiments.map((e) => e.model)));

  return (
    <div className="experiments-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>MLflow Experiment Tracker</h1>
          <p>Track metrics, parameters, and artifacts across training runs logged in MLflow.</p>
        </div>

        <div className="filter-wrap">
          <label>Filter by Model: </label>
          <select
            value={filterModel}
            onChange={(e) => setFilterModel(e.target.value)}
          >
            <option value="all">All Models ({experiments.length})</option>
            {uniqueModels.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state glass-card">
          <span className="spinner"></span> Fetching MLflow Runs...
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty-state glass-card">
          <p>No experiment runs logged yet. Launch a model training run from the Training Studio to populate experiments.</p>
        </div>
      ) : (
        <div className="experiments-grid">
          {filtered.map((exp) => (
            <div key={exp.id} className="exp-card glass-card">
              <div className="exp-header">
                <div>
                  <span className="badge badge-cyan">{exp.dataset}</span>
                  <h3>{exp.model}</h3>
                </div>
                <span className={`badge ${exp.stage === "Production" ? "badge-success" : "badge-primary"}`}>
                  {exp.version} ({exp.stage || "Development"})
                </span>
              </div>

              <div className="exp-time">
                <small>Run Date: {new Date(exp.created_at || Date.now()).toLocaleString()}</small>
              </div>

              <div className="exp-metrics-list">
                {Object.entries(exp.metrics || {}).map(([mk, mv]) => (
                  <div key={mk} className="exp-metric-pill">
                    <span>{mk.replace("_", " ")}</span>
                    <strong>
                      {typeof mv === "number"
                        ? mv < 1
                          ? `${(mv * 100).toFixed(1)}%`
                          : mv.toFixed(3)
                        : mv}
                    </strong>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ExperimentsPage;
