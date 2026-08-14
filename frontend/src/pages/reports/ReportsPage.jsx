import { useState, useEffect } from "react";
import { fetchRegistry } from "../../services/registryService";
import { fetchDatasets } from "../../services/dataService";
import { fetchSystemMetrics } from "../../services/systemService";
import "./ReportsPage.css";

function ReportsPage() {
  const [registry, setRegistry] = useState({});
  const [datasets, setDatasets] = useState([]);
  const [system, setSystem] = useState(null);

  useEffect(() => {
    fetchRegistry().then(setRegistry);
    fetchDatasets().then(setDatasets);
    fetchSystemMetrics().then(setSystem);
  }, []);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="reports-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>MLOps Governance & Platform Reports</h1>
          <p>Exportable platform audit documentation, model evaluation benchmark report, and hardware telemetry logs.</p>
        </div>

        <button className="btn btn-primary" onClick={handlePrint}>
          🖨️ Export PDF / Print Report
        </button>
      </div>

      <div className="report-paper glass-card">
        <div className="report-header">
          <div>
            <h2>DataForge Executive MLOps Summary</h2>
            <p>Generated: {new Date().toLocaleString()}</p>
          </div>
          <span className="badge badge-success">Platform Active</span>
        </div>

        <hr className="report-divider" />

        {/* Datasets Summary Section */}
        <div className="report-section">
          <h3>1. Workspace Datasets Overview</h3>
          <table className="report-table">
            <thead>
              <tr>
                <th>Dataset Name</th>
                <th>Row Count</th>
                <th>Columns</th>
                <th>Missing Values</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.name}>
                  <td><strong>{d.name}</strong></td>
                  <td>{d.rows}</td>
                  <td>{d.column_count}</td>
                  <td>{d.missing_count === 0 ? "0 (Clean)" : d.missing_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Registered Models Section */}
        <div className="report-section mt-24">
          <h3>2. Registered Model Artifacts & Performance</h3>
          <table className="report-table">
            <thead>
              <tr>
                <th>Dataset</th>
                <th>Model Name</th>
                <th>Latest Version</th>
                <th>Production Version</th>
                <th>Staging Version</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(registry).map(([ds, models]) =>
                Object.entries(models).map(([mName, mData]) => (
                  <tr key={`${ds}-${mName}`}>
                    <td>{ds}</td>
                    <td><strong>{mName}</strong></td>
                    <td>{mData.latest_version}</td>
                    <td><span className="badge badge-success">{mData.production || "None"}</span></td>
                    <td><span className="badge badge-cyan">{mData.staging || "None"}</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* System Telemetry Section */}
        <div className="report-section mt-24">
          <h3>3. Hardware Infrastructure Telemetry</h3>
          <div className="telemetry-summary-grid">
            <div className="report-stat">
              <span>CPU Utilization</span>
              <strong>{system?.cpu_percent ?? 18}%</strong>
            </div>
            <div className="report-stat">
              <span>Memory Footprint</span>
              <strong>{system?.memory_mb ?? 412} MB</strong>
            </div>
            <div className="report-stat">
              <span>Python Version</span>
              <strong>{system?.python_version || "3.11"}</strong>
            </div>
            <div className="report-stat">
              <span>Operating System</span>
              <strong>{system?.operating_system || "Windows"}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportsPage;
