import { useState, useEffect } from "react";
import { fetchDatasets } from "../../services/dataService";
import { trainModel } from "../../services/trainingService";
import "./TrainingPage.css";

const ALGORITHMS = [
  "Random Forest",
  "Decision Tree",
  "Logistic Regression",
  "Gradient Boosting",
  "XGBoost",
  "SVM",
  "Naive Bayes"
];

function TrainingPage() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [targetCol, setTargetCol] = useState("");
  const [selectedAlgorithm, setSelectedAlgorithm] = useState("Random Forest");
  const [testSplit, setTestSplit] = useState(0.2);

  const [trainingResult, setTrainingResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDatasets().then((data) => {
      setDatasets(data);
      if (data.length > 0) {
        setSelectedDataset(data[0].name);
        if (data[0].columns && data[0].columns.length > 0) {
          setTargetCol(data[0].columns[data[0].columns.length - 1]);
        }
      }
    });
  }, []);

  const handleDatasetChange = (dsName) => {
    setSelectedDataset(dsName);
    const ds = datasets.find((d) => d.name === dsName);
    if (ds && ds.columns && ds.columns.length > 0) {
      setTargetCol(ds.columns[ds.columns.length - 1]);
    }
  };

  const currentDatasetObj = datasets.find((d) => d.name === selectedDataset);

  const handleTrain = async (e) => {
    e.preventDefault();
    if (!selectedDataset || !targetCol) return;
    setLoading(true);
    setError(null);
    setTrainingResult(null);

    try {
      const res = await trainModel({
        dataset_name: selectedDataset,
        target_col: targetCol,
        model_name: selectedAlgorithm,
        test_size: parseFloat(testSplit),
        save: true
      });
      setTrainingResult(res);
    } catch (err) {
      setError(err.message || "Model training failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="training-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Model Training Studio</h1>
          <p>Configure machine learning algorithms, split ratios, fit models, and log metrics directly to MLflow & Registry.</p>
        </div>
      </div>

      <div className="training-grid">
        {/* Configuration Card */}
        <div className="training-config-card glass-card">
          <h3>Training Configuration</h3>

          <form onSubmit={handleTrain} className="training-form">
            <div className="form-group">
              <label>Select Dataset</label>
              <select
                value={selectedDataset}
                onChange={(e) => handleDatasetChange(e.target.value)}
              >
                {datasets.map((d) => (
                  <option key={d.name} value={d.name}>
                    {d.name} ({d.rows} rows)
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Target Column (Y Variable)</label>
              <select
                value={targetCol}
                onChange={(e) => setTargetCol(e.target.value)}
              >
                {currentDatasetObj?.columns?.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Algorithm Choice</label>
              <select
                value={selectedAlgorithm}
                onChange={(e) => setSelectedAlgorithm(e.target.value)}
              >
                {ALGORITHMS.map((algo) => (
                  <option key={algo} value={algo}>
                    {algo}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Validation Test Split: {(testSplit * 100).toFixed(0)}%</label>
              <input
                type="range"
                min="0.1"
                max="0.4"
                step="0.05"
                value={testSplit}
                onChange={(e) => setTestSplit(e.target.value)}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span> Fitting & Profiling Model...
                </>
              ) : (
                "⚡ Train & Register Model"
              )}
            </button>
          </form>
        </div>

        {/* Results Card */}
        <div className="training-result-card glass-card">
          <h3>Evaluation Results & Metrics</h3>

          {error && <div className="error-alert">⚠️ {error}</div>}

          {loading && (
            <div className="training-progress-box">
              <div className="spinner-large"></div>
              <h4>Executing ML Pipeline...</h4>
              <p>Fitting pipeline on dataset features and computing cross-validated metrics.</p>
            </div>
          )}

          {trainingResult && !loading && (
            <div className="results-view animate-fade-in">
              <div className="success-banner">
                <span className="badge badge-success">✓ Training Complete</span>
                <h2>{trainingResult.model_name}</h2>
                <small className="font-mono text-cyan">Saved to: {trainingResult.model_path}</small>
              </div>

              <h4 className="mt-20">Evaluated Model Metrics</h4>
              <div className="metrics-grid">
                {Object.entries(trainingResult.metrics || {}).map(([metricKey, metricValue]) => (
                  <div key={metricKey} className="metric-box">
                    <span className="metric-name">{metricKey.replace("_", " ").toUpperCase()}</span>
                    <strong className="metric-val">
                      {typeof metricValue === "number"
                        ? metricValue < 1
                          ? `${(metricValue * 100).toFixed(2)}%`
                          : metricValue.toFixed(4)
                        : metricValue ?? "N/A"}
                    </strong>
                  </div>
                ))}
              </div>

              <div className="mlflow-badge-bar mt-20">
                <span className="badge badge-primary">✓ Logged to MLflow Run</span>
                <span className="badge badge-cyan">✓ Model Registry Registered</span>
              </div>
            </div>
          )}

          {!trainingResult && !loading && !error && (
            <div className="empty-training-placeholder">
              <p>Configure model hyper-parameters on the left and click train to start execution.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TrainingPage;
