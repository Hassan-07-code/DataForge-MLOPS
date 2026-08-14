import { useState, useEffect } from "react";
import { fetchDatasets, fetchVisualization } from "../../services/dataService";
import "./VisualizationPage.css";

function VisualizationPage() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [vizData, setVizData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDatasets().then((data) => {
      setDatasets(data);
      if (data.length > 0) setSelectedDataset(data[0].name);
    });
  }, []);

  useEffect(() => {
    if (!selectedDataset) return;
    setLoading(true);
    fetchVisualization(selectedDataset)
      .then(setVizData)
      .finally(() => setLoading(false));
  }, [selectedDataset]);

  return (
    <div className="visualization-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Visual Analytics Studio</h1>
          <p>Explore feature distributions, value counts, missingness, and column statistics for your datasets.</p>
        </div>

        <div className="header-selector">
          <select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
          >
            {datasets.map((d) => (
              <option key={d.name} value={d.name}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state glass-card">
          <span className="spinner"></span> Computing Data Analytics...
        </div>
      ) : vizData?.summary ? (
        <div className="viz-content">
          {/* Summary Banner */}
          <div className="viz-stats-grid">
            <div className="stat-card glass-card">
              <span className="stat-label">Total Rows</span>
              <h2>{vizData.total_rows}</h2>
            </div>
            <div className="stat-card glass-card">
              <span className="stat-label">Total Features</span>
              <h2>{vizData.total_columns}</h2>
            </div>
            <div className="stat-card glass-card">
              <span className="stat-label">Numeric Features</span>
              <h2>{Object.values(vizData.summary).filter((c) => c.type === "numeric").length}</h2>
            </div>
            <div className="stat-card glass-card">
              <span className="stat-label">Categorical Features</span>
              <h2>{Object.values(vizData.summary).filter((c) => c.type === "categorical").length}</h2>
            </div>
          </div>

          {/* Histogram Charts Grid for Numeric Features */}
          <h2 className="section-subtitle mt-24">Feature Value Distributions</h2>
          <div className="charts-grid">
            {Object.entries(vizData.summary)
              .filter(([_, info]) => info.type === "numeric" && info.distribution)
              .map(([colName, info]) => {
                const maxCount = Math.max(...info.distribution.map((b) => b.count), 1);
                return (
                  <div key={colName} className="chart-card glass-card">
                    <div className="chart-card-header">
                      <h4>{colName}</h4>
                      <span className="badge badge-cyan">Numeric</span>
                    </div>

                    <div className="bar-chart">
                      {info.distribution.map((b, i) => {
                        const pct = (b.count / maxCount) * 100;
                        return (
                          <div key={i} className="bar-col" title={`${b.bin}: ${b.count}`}>
                            <div className="bar-fill" style={{ height: `${pct}%` }}></div>
                            <small className="bar-label">{b.count}</small>
                          </div>
                        );
                      })}
                    </div>

                    <div className="chart-meta">
                      <small>Min: {info.min.toFixed(2)}</small>
                      <small>Mean: {info.mean.toFixed(2)}</small>
                      <small>Max: {info.max.toFixed(2)}</small>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      ) : (
        <div className="glass-card loading-state">No visualization data available for this dataset.</div>
      )}
    </div>
  );
}

export default VisualizationPage;
