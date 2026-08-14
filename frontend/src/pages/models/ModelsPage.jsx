import { useState, useEffect } from "react";
import { fetchRegistry, promoteModel } from "../../services/registryService";
import "./ModelsPage.css";

function ModelsPage() {
  const [registry, setRegistry] = useState({});
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState(null);

  const loadData = async () => {
    try {
      const data = await fetchRegistry();
      setRegistry(data || {});
    } catch (err) {
      console.error("Failed to load registry:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handlePromote = async (datasetName, modelName, version, newStage) => {
    try {
      setActionMsg(null);
      await promoteModel({
        dataset_name: datasetName,
        model_name: modelName,
        version: version,
        stage: newStage,
      });
      setActionMsg(`Successfully set ${modelName} (${version}) to ${newStage}!`);
      await loadData();
    } catch (err) {
      alert(`Promotion failed: ${err.message}`);
    }
  };

  // Flatten registry structure for table rendering
  const registryItems = [];
  Object.entries(registry).forEach(([dsName, models]) => {
    Object.entries(models).forEach(([mName, mData]) => {
      const prodVersion = mData.production;
      const stagingVersion = mData.staging;

      Object.entries(mData.versions || {}).forEach(([vNum, vData]) => {
        let currentStage = vData.stage || "Development";
        if (vNum === prodVersion) currentStage = "Production";
        else if (vNum === stagingVersion) currentStage = "Staging";

        registryItems.push({
          dataset: dsName,
          model: mName,
          version: vNum,
          stage: currentStage,
          created_at: vData.created_at,
          metrics: vData.metrics || {},
          isProd: vNum === prodVersion,
          isStaging: vNum === stagingVersion,
        });
      });
    });
  });

  return (
    <div className="models-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1>Model Registry Manager</h1>
          <p>Govern trained model versions, manage production lifecycle stages, and promote models to deployment.</p>
        </div>
      </div>

      {actionMsg && (
        <div className="action-toast animate-fade-in">
          <span>✓ {actionMsg}</span>
          <button onClick={() => setActionMsg(null)}>✕</button>
        </div>
      )}

      {loading ? (
        <div className="loading-state glass-card">
          <span className="spinner"></span> Loading Model Registry...
        </div>
      ) : registryItems.length === 0 ? (
        <div className="empty-state glass-card">
          <p>No model versions registered yet. Train a model from the Training Studio to register versions.</p>
        </div>
      ) : (
        <div className="registry-table-card glass-card">
          <div className="table-wrapper">
            <table className="registry-table">
              <thead>
                <tr>
                  <th>Dataset</th>
                  <th>Model Name</th>
                  <th>Version</th>
                  <th>Current Stage</th>
                  <th>Key Performance Metric</th>
                  <th>Created At</th>
                  <th>Stage Promotion Actions</th>
                </tr>
              </thead>
              <tbody>
                {registryItems.map((item, idx) => {
                  const acc = item.metrics.accuracy ?? item.metrics.f1_weighted ?? item.metrics.r2;
                  return (
                    <tr key={idx} className={item.isProd ? "row-prod" : ""}>
                      <td><strong>{item.dataset}</strong></td>
                      <td>{item.model}</td>
                      <td><span className="font-mono text-cyan">{item.version}</span></td>
                      <td>
                        <span className={`badge ${
                          item.stage === "Production"
                            ? "badge-success"
                            : item.stage === "Staging"
                            ? "badge-cyan"
                            : item.stage === "Archived"
                            ? "badge-warning"
                            : "badge-primary"
                        }`}>
                          {item.stage}
                        </span>
                      </td>
                      <td>
                        <strong>
                          {typeof acc === "number"
                            ? acc <= 1 ? `${(acc * 100).toFixed(1)}%` : acc.toFixed(3)
                            : "N/A"}
                        </strong>
                      </td>
                      <td className="text-dim">{new Date(item.created_at || Date.now()).toLocaleDateString()}</td>
                      <td>
                        <div className="action-btns">
                          {!item.isProd && (
                            <button
                              className="btn btn-success btn-sm"
                              onClick={() => handlePromote(item.dataset, item.model, item.version, "Production")}
                            >
                              Promote to Production
                            </button>
                          )}
                          {!item.isStaging && !item.isProd && (
                            <button
                              className="btn btn-secondary btn-sm"
                              onClick={() => handlePromote(item.dataset, item.model, item.version, "Staging")}
                            >
                              Staging
                            </button>
                          )}
                          {item.stage !== "Archived" && (
                            <button
                              className="btn btn-danger btn-sm"
                              onClick={() => handlePromote(item.dataset, item.model, item.version, "Archived")}
                            >
                              Archive
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default ModelsPage;
