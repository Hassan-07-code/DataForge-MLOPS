import { useState, useEffect } from "react";
import { fetchDatasets, cleanDataset } from "../../services/dataService";
import "./DataCleaningPage.css";

function DataCleaningPage() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [missingStrategy, setMissingStrategy] = useState("mean");
  const [encodeCategoricals, setEncodeCategoricals] = useState(true);
  const [scaleFeatures, setScaleFeatures] = useState(false);

  const [cleaningResult, setCleaningResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDatasets() {
      try{
        const data = await fetchDatasets();

        setDatasets(data);
        const lastDataset = localStorage.getItem("lastUploadedDataset");

        if(lastDataset) {
          const exists = data.find(
            (d) => d.name === lastDataset
          );

          if (exists) {
            setSelectedDataset(lastDataset);
            return;
          }
        }

        if (data.length > 0) {
          setSelectedDataset(data[0].name);
        }

      }catch (err) {
        console.error("Error loading datasets:", err);
      }
    }
    loadDatasets();
  },[]
  )

  const handleClean = async (e) => {
    e.preventDefault();
    if (!selectedDataset) return;
    setLoading(true);
    setError(null);
    setCleaningResult(null);

    try {
      const res = await cleanDataset({
        dataset_name: selectedDataset,
        remove_duplicates: removeDuplicates,
        missing_strategy: missingStrategy,
        encode_categoricals: encodeCategoricals,
        scale_features: scaleFeatures,
      });
      setCleaningResult(res);
    } catch (err) {
      console.error("Error cleaning dataset:", err);
      setError(err.message || "Failed to clean dataset.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cleaning-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Automated Data Cleaning Suite</h1>
          <p>Remove duplicate rows, handle missing values, encode categorical variables, and scale numerical features.</p>
        </div>
      </div>

      <div className="cleaning-grid">
        {/* Configuration Panel */}
        <div className="cleaning-config-card glass-card">
          <h3>Cleaning Pipeline Configuration</h3>

          <form onSubmit={handleClean} className="cleaning-form">
            <div className="form-group">
              <label>Select Target Dataset</label>
              <select
                value={selectedDataset}
                onChange={(e) => setSelectedDataset(e.target.value)}
              >
                {datasets.map((d) => (
                  <option key={d.name} value={d.name}>
                    {d.name} ({d.rows} rows, {d.column_count} cols)
                  </option>
                ))}
              </select>
            </div>

            <div className="form-checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={removeDuplicates}
                  onChange={(e) => setRemoveDuplicates(e.target.checked)}
                />
                <span>Remove Duplicate Rows</span>
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={encodeCategoricals}
                  onChange={(e) => setEncodeCategoricals(e.target.checked)}
                />
                <span>Label Encode Categorical Features</span>
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={scaleFeatures}
                  onChange={(e) => setScaleFeatures(e.target.checked)}
                />
                <span>Standard Scale Numerical Columns</span>
              </label>
            </div>

            <div className="form-group">
              <label>Missing Values Imputation Strategy</label>
              <select
                value={missingStrategy}
                onChange={(e) => setMissingStrategy(e.target.value)}
              >
                <option value="mean">Mean Imputation (Numerical)</option>
                <option value="median">Median Imputation (Numerical)</option>
                <option value="mode">Mode Imputation (Categorical/Discrete)</option>
              </select>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={loading}
            >
              {loading ? <span className="spinner"></span> : "Execute Cleaning Pipeline →"}
            </button>
          </form>
        </div>

        {/* Output Log & Summary */}
        <div className="cleaning-output-card glass-card">
          <h3>Execution Audit Log</h3>

          {error && <div className="error-alert">⚠️ {error}</div>}

          {cleaningResult ? (
            <div className="cleaning-result-view animate-fade-in">
              <div className="summary-banner">
                <div className="summary-item">
                  <span>Original Rows</span>
                  <strong>{cleaningResult.original_rows}</strong>
                </div>
                <div className="summary-item">
                  <span>Cleaned Rows</span>
                  <strong className="text-green">{cleaningResult.cleaned_rows}</strong>
                </div>
                <div className="summary-item">
                  <span>Output Artifact</span>
                  <strong className="text-cyan">{cleaningResult.output_dataset}</strong>
                </div>
              </div>

              <div className="log-section">
                <h4>Pipeline Step Logs</h4>
                <ul className="log-list font-mono">
                  {cleaningResult.log.map((logLine, idx) => (
                    <li key={idx}>{logLine}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="empty-log-placeholder">
              <p>Configure pipeline options on the left and click execute to process your dataset.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DataCleaningPage;
