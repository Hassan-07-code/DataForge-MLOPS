import { useState, useEffect } from "react";
import { predict, batchPredict, fetchPredictionLogs } from "../../services/predictionService";
import { fetchDatasets } from "../../services/dataService";
import "./PredictionsPage.css";

function PredictionsPage() {
  const [activeTab, setActiveTab] = useState("single");
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [selectedModel, setSelectedModel] = useState("Random Forest");

  // Form feature state
  const [featureInputs, setFeatureInputs] = useState({});
  const [singleResult, setSingleResult] = useState(null);
  const [singleLoading, setSingleLoading] = useState(false);
  const [singleError, setSingleError] = useState(null);

  // Batch state
  const [batchJson, setBatchJson] = useState(`[
  { "sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2 },
  { "sepal_length": 6.7, "sepal_width": 3.0, "petal_length": 5.2, "petal_width": 2.3 }
]`);
  const [batchResult, setBatchResult] = useState(null);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchError, setBatchError] = useState(null);

  // Logs state
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchDatasets().then((data) => {
      setDatasets(data);
      if (data.length > 0) {
        setSelectedDataset(data[0].name);
        initFeatureInputs(data[0]);
      }
    });
    fetchPredictionLogs().then(setLogs);
  }, []);

  const initFeatureInputs = (dsObj) => {
    if (!dsObj || !dsObj.columns) return;
    const inputs = {};
    // Exclude last column assuming it's the target
    const featureCols = dsObj.columns.slice(0, -1);
    featureCols.forEach((col) => {
      inputs[col] = "0";
    });
    setFeatureInputs(inputs);
  };

  const handleDatasetChange = (dsName) => {
    setSelectedDataset(dsName);
    const ds = datasets.find((d) => d.name === dsName);
    if (ds) initFeatureInputs(ds);
  };

  const handleSinglePredict = async (e) => {
    e.preventDefault();
    setSingleLoading(true);
    setSingleError(null);
    setSingleResult(null);

    // Convert string inputs to numeric floats where possible
    const formattedFeatures = {};
    Object.entries(featureInputs).forEach(([k, v]) => {
      const num = parseFloat(v);
      formattedFeatures[k] = isNaN(num) ? v : num;
    });

    try {
      const res = await predict({
        dataset_name: selectedDataset,
        model_name: selectedModel,
        features: formattedFeatures,
      });
      setSingleResult(res);
      // Refresh prediction logs
      fetchPredictionLogs().then(setLogs);
    } catch (err) {
      setSingleError(err.message || "Prediction failed.");
    } finally {
      setSingleLoading(false);
    }
  };

  const handleBatchPredict = async (e) => {
    e.preventDefault();
    setBatchLoading(true);
    setBatchError(null);
    setBatchResult(null);

    try {
      const parsedRows = JSON.parse(batchJson);
      const res = await batchPredict({
        dataset_name: selectedDataset,
        model_name: selectedModel,
        rows: parsedRows,
      });
      setBatchResult(res);
      fetchPredictionLogs().then(setLogs);
    } catch (err) {
      setBatchError(`Invalid JSON or batch failure: ${err.message}`);
    } finally {
      setBatchLoading(false);
    }
  };

  return (
    <div className="predictions-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Real-Time Prediction Studio</h1>
          <p>Serve real-time single and batch inference requests using deployed production models.</p>
        </div>

        <div className="tab-buttons">
          <button
            className={`tab-btn ${activeTab === "single" ? "active" : ""}`}
            onClick={() => setActiveTab("single")}
          >
            Single Predict
          </button>

          <button
            className={`tab-btn ${activeTab === "batch" ? "active" : ""}`}
            onClick={() => setActiveTab("batch")}
          >
            Batch Predict
          </button>

          <button
            className={`tab-btn ${activeTab === "logs" ? "active" : ""}`}
            onClick={() => setActiveTab("logs")}
          >
            Prediction Logs ({logs.length})
          </button>
        </div>
      </div>

      {activeTab === "single" && (
        <div className="pred-grid">
          {/* Form */}
          <div className="pred-form-card glass-card">
            <h3>Single Prediction Input Form</h3>

            <form onSubmit={handleSinglePredict} className="pred-form">
              <div className="form-group-row">
                <div className="form-group">
                  <label>Dataset Scope</label>
                  <select
                    value={selectedDataset}
                    onChange={(e) => handleDatasetChange(e.target.value)}
                  >
                    {datasets.map((d) => (
                      <option key={d.name} value={d.name}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Model Engine</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    <option value="Random Forest">Random Forest</option>
                    <option value="Decision Tree">Decision Tree</option>
                    <option value="Logistic Regression">Logistic Regression</option>
                  </select>
                </div>
              </div>

              <h4 className="mt-16">Feature Values Input</h4>
              <div className="features-inputs-grid">
                {Object.keys(featureInputs).map((colName) => (
                  <div key={colName} className="form-group">
                    <label>{colName}</label>
                    <input
                      type="text"
                      value={featureInputs[colName]}
                      onChange={(e) =>
                        setFeatureInputs({
                          ...featureInputs,
                          [colName]: e.target.value,
                        })
                      }
                    />
                  </div>
                ))}
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-block mt-20"
                disabled={singleLoading}
              >
                {singleLoading ? <span className="spinner"></span> : "⚡ Run Real-Time Predict"}
              </button>
            </form>
          </div>

          {/* Results */}
          <div className="pred-result-card glass-card">
            <h3>Prediction Response</h3>

            {singleError && <div className="error-alert">⚠️ {singleError}</div>}

            {singleResult && (
              <div className="single-res-view animate-fade-in">
                <div className="res-badge-banner">
                  <span className="badge badge-success">✓ Inferred Output</span>
                  <span className="badge badge-primary">{singleResult.model_name} ({singleResult.version})</span>
                </div>

                <div className="prediction-output-box">
                  <span className="pred-lbl">Predicted Target Class</span>
                  <h1 className="pred-val">{singleResult.prediction}</h1>
                </div>

                {singleResult.probability && (
                  <div className="probability-section">
                    <h4>Confidence Probabilities</h4>
                    <div className="proba-bars font-mono">
                      {singleResult.probability.map((prob, idx) => (
                        <div key={idx} className="proba-item">
                          <span>Class {idx}: {(prob * 100).toFixed(1)}%</span>
                          <div className="progress-bg">
                            <div
                              className="progress-fill cyan"
                              style={{ width: `${prob * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {!singleResult && !singleError && (
              <div className="empty-state">
                <p>Fill feature values on the left and click predict to retrieve inference probabilities.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "batch" && (
        <div className="batch-view glass-card">
          <h3>Batch Inference JSON Processor</h3>
          <p>Paste an array of JSON objects containing feature key-value pairs for bulk scoring.</p>

          <form onSubmit={handleBatchPredict} className="batch-form mt-16">
            <textarea
              rows="8"
              className="font-mono"
              value={batchJson}
              onChange={(e) => setBatchJson(e.target.value)}
            ></textarea>

            <button type="submit" className="btn btn-primary mt-16" disabled={batchLoading}>
              {batchLoading ? <span className="spinner"></span> : "⚡ Execute Batch Predict"}
            </button>
          </form>

          {batchError && <div className="error-alert mt-16">⚠️ {batchError}</div>}

          {batchResult && (
            <div className="batch-results-view mt-24 animate-fade-in">
              <h4>Batch Predictions Result ({batchResult.total_rows} rows)</h4>
              <div className="font-mono json-output">
                <pre>{JSON.stringify(batchResult.predictions, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "logs" && (
        <div className="logs-view glass-card">
          <h3>Prediction Audit Telemetry</h3>
          <div className="table-wrapper">
            <table className="registry-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Endpoint</th>
                  <th>Dataset</th>
                  <th>Model</th>
                  <th>Version</th>
                  <th>Latency (ms)</th>
                  <th>Client IP</th>
                </tr>
              </thead>
              <tbody>
                {logs.slice().reverse().map((log, idx) => (
                  <tr key={idx}>
                    <td className="text-dim">{new Date(log.timestamp).toLocaleString()}</td>
                    <td><span className="badge badge-cyan">{log.endpoint}</span></td>
                    <td>{log.dataset_name}</td>
                    <td>{log.model_name}</td>
                    <td><span className="font-mono">{log.version}</span></td>
                    <td className="text-green font-mono">{log.latency_ms ? log.latency_ms.toFixed(2) : "1.5"} ms</td>
                    <td>{log.client_ip || "127.0.0.1"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default PredictionsPage;
