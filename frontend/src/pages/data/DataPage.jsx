import { useState, useEffect, useRef, useMemo} from "react";
import { useNavigate } from "react-router-dom";
import { fetchDatasets, fetchVisualization } from "../../services/dataService";
import "./DataPage.css";

function DataPage() {
  const navigate = useNavigate();
  const [vizData, setVizData] = useState(null);
  const [vizLoading, setVizLoading] = useState(false);
    {/*==================================================
                DATASET UPLOAD STATE
    ==================================================*/}
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [datasetSummary, setDatasetSummary] = useState(null);
    const [datasetPreview, setDatasetPreview] = useState([]);
    const [previewColumns, setPreviewColumns] = useState([]);
    const [searchPreview, setSearchPreview] = useState("");
    const [uploadedFileName, setUploadedFileName] = useState("No Dataset Uploaded");
    const fileInputRef = useRef(null);

    useEffect(() => {
        async function loadDatasets() {
        try {
            const data = await fetchDatasets();
            setDatasets(data);
        } catch (err) {
            console.error("Failed to load datasets:", err);
        } finally {
            setLoading(false);
        }
        }
        loadDatasets();
    }, []);
    
    /*==================================================
                DATASET HEALTH SCORE
    ==================================================*/

    const datasetHealth = useMemo(() => {

        if (!datasetSummary) return 0;

        const rows = datasetSummary.rows || 0;

        if (rows === 0) return 0;
        const missing = datasetSummary.missing_values || 0;
        const totalCells = rows * (datasetSummary.columns || 1);
        const ratio = totalCells === 0 ? 0 : missing / totalCells;
        const score = Math.max(0, Math.round((1 - ratio) * 100));

        return score;
    }, [datasetSummary]);

    /*==================================================
                FILTERED PREVIEW
    ==================================================*/

    const filteredPreview = useMemo(() => {

        if (!searchPreview) return datasetPreview;

        return datasetPreview.filter((row) =>

            Object.values(row)
                .join(" ")
                .toLowerCase()
                .includes(searchPreview.toLowerCase())
        );
    }, [datasetPreview, searchPreview]);

    /*==================================================
                DATASET UPLOAD
    ==================================================*/

    const handleDatasetUpload = async (event) => {

        const file = event.target.files[0];

        if (!file) return;

        try {

            setUploading(true);

            setUploadProgress(15);

            const formData = new FormData();

            formData.append("file", file);

            const response = await fetch(

                "http://127.0.0.1:8000/api/dataset/upload",

                {

                    method: "POST",

                    body: formData,

                }

            );

            setUploadProgress(55);

            const result = await response.json();

            if (!response.ok) {

                throw new Error(result.detail || "Upload failed.");

            }
            setUploadedFileName(result.summary.filename);

            setDatasetSummary(result.summary);
            localStorage.setItem("lastUploadedDataset", result.summary.filename);

            setDatasetPreview(result.preview.records.slice(0, 10));

            setPreviewColumns(result.preview.columns);

            setUploadProgress(100);

            const latest = await fetchDatasets();

        }

        catch (err) {

            console.error(err);

            alert(err.message);

        }

        finally {

            setUploading(false);

        }

    };

    return (
        <div className="data-page animate-fade-in">
        {/* Header */}
        <div className="page-header">
            <div>
            <h1>Dataset Management</h1>
            <p>Inspect raw datasets, view column schemas, missing metrics, and prepare datasets for model training.</p>
            </div>
            <div className="header-actions">
            <button className="btn btn-primary" onClick={() => navigate("/cleaning")}>
                <span>🧹</span> Proceed to Data Cleaning
            </button>
            </div>
        </div>

      {/*===============================================
            DATASET WORKSPACE
      ==================================================*/}

    <section className="dataset-workspace">

        {/* Upload Card */}

        <div className="glass-card upload-workspace">

            <div className="card-header">

                <div>

                    <h3>Upload Dataset</h3>

                    <small>CSV (.csv) & Excel (.xlsx)</small>

                </div>

            </div>

            <div
                className="upload-dropzone"

                onClick={() => fileInputRef.current.click()}>

                            {
                datasetSummary ? (

                    <>
                        <div className="upload-success-icon">
                            ✅
                        </div>

                        <h4>{uploadedFileName}</h4>

                        <p>
                            Dataset uploaded successfully.
                        </p>

                        <small>
                            {datasetSummary.rows.toLocaleString()} Rows • {" "}
                            {datasetSummary.columns} Columns
                        </small>
                    </>

                ) : (

                    <>
                        <div className="upload-icon">
                            📂
                        </div>

                        <h4>
                            Drag & Drop or Browse
                        </h4>

                        <p>
                            Upload CSV or Excel dataset.
                        </p>
                    </>

                )
            }

                <button

                    type="button"

                    className="btn btn-primary">

                        {
                            datasetSummary
                                ? "Replace Dataset"
                                : "Browse Dataset"
                        }

                </button>

            </div>

            <input

                ref={fileInputRef}

                type="file"

                accept=".csv,.xlsx,.xls"

                hidden

                onChange={handleDatasetUpload}

            />

            {

                uploading && (

                    <div className="upload-progress">

                        <div

                            className="upload-progress-fill"

                            style={{

                                width: `${uploadProgress}%`

                            }}

                        />

                    </div>

                )

            }

        </div>

        {/* Dataset Summary */}

        <div className="glass-card dataset-summary-card">

            <div className="card-header">

                <div>

                    <h3>Dataset Summary</h3>

                    <small>

                        Current uploaded dataset

                    </small>

                </div>

            </div>

            {

                datasetSummary ?

                (

                    <div className="summary-grid">

                        <div className="summary-item">

                            <span>Filename</span>

                            <strong>

                                {datasetSummary.filename}

                            </strong>

                        </div>

                        <div className="summary-item">

                            <span>Rows</span>

                            <strong>

                                {datasetSummary.rows}

                            </strong>

                        </div>

                        <div className="summary-item">

                            <span>Columns</span>

                            <strong>

                                {datasetSummary.columns}

                            </strong>

                        </div>

                        <div className="summary-item">

                            <span>Missing</span>

                            <strong>

                                {datasetSummary.missing_values}

                            </strong>

                        </div>

                        <div className="summary-item">

                            <span>Numerical</span>

                            <strong>

                                {datasetSummary.numerical_columns}

                            </strong>

                        </div>

                        <div className="summary-item">

                            <span>Categorical</span>

                            <strong>

                                {datasetSummary.categorical_columns}

                            </strong>

                        </div>

                        <div className="summary-item">

                            <span>Dataset Size</span>

                            <strong>

                                {datasetSummary.size_mb} MB

                            </strong>

                        </div>

                        <div className="summary-item">

                            <span>Status</span>

                            <strong className="text-green">

                                Ready

                            </strong>

                        </div>

                    </div>

                )

                :

                (

                    <div className="empty-summary">

                        <h4>

                            No Dataset Uploaded

                        </h4>

                        <p>

                            Upload a CSV or Excel dataset to begin your ML workflow.

                        </p>

                    </div>

                )

            }

        </div>

    </section>


        {/* Right: Selected Dataset Details & Columns */}
        <div className="dataset-detail-col">
          {/*==================================================
                    DATASET PREVIEW
          ==================================================*/}

          <div className="glass-card preview-card">

              <div className="card-header">

                  <div>

                      <h3>Dataset Preview</h3>

                      <small>

                          Showing first 10 records

                      </small>

                  </div>

                  <input

                      type="text"

                      placeholder="Search preview..."

                      className="preview-search"

                      value={searchPreview}

                      onChange={(e) =>

                          setSearchPreview(e.target.value)

                      }

                  />

              </div>

              {

                  filteredPreview.length > 0 ?

                  (

                      <div className="preview-table-wrapper">

                          <table className="preview-table">

                              <thead>

                                  <tr>

                                      {

                                          previewColumns.map((column) => (

                                              <th key={column}>

                                                  {column}

                                              </th>

                                          ))

                                      }

                                  </tr>

                              </thead>

                              <tbody>

                                  {

                                      filteredPreview.map((row, rowIndex) => (

                                          <tr key={rowIndex}>

                                              {

                                                  previewColumns.map((column) => (

                                                      <td key={column}>

                                                          {

                                                              row[column] !== null &&

                                                              row[column] !== undefined

                                                                  ? String(row[column])

                                                                  : "-"

                                                          }

                                                      </td>

                                                  ))

                                              }

                                          </tr>

                                      ))

                                  }

                              </tbody>

                          </table>

                      </div>

                  )

                  :

                  (

                      <div className="preview-empty">

                          <div className="preview-empty-icon">

                              📊

                          </div>

                          <h4>

                              No Preview Available

                          </h4>

                          <p>

                              Upload or select a dataset to preview

                              the first 10 records.

                          </p>

                      </div>

                  )

              }

          </div>

          {/*==================================================
                          DATASET HEALTH
          ==================================================*/}

          <div className="glass-card dataset-health-card">

              <div className="card-header">

                  <div>

                      <h3>Dataset Health</h3>

                      <small>

                          AI quality assessment

                      </small>

                  </div>

              </div>

              <div className="health-content">

                  {/* Circular Health Indicator */}

                  <div className="health-circle-wrapper">

                      <div

                          className="health-circle"

                          style={{

                              background: `conic-gradient(
                                  var(--accent-green) ${datasetHealth * 3.6}deg,
                                  rgba(255,255,255,.08) 0deg
                              )`

                          }}

                      >

                          <div className="health-circle-inner">

                              <strong>

                                  {datasetHealth}%

                              </strong>

                              <span>

                                  Health

                              </span>

                          </div>

                      </div>

                  </div>

                  {/* Quality Metrics */}

                  <div className="health-info">

                      <div className="health-item">

                          <span>Rows</span>

                          <strong>

                              {datasetSummary?.rows ?? "--"}

                          </strong>

                      </div>

                      <div className="health-item">

                          <span>Columns</span>

                          <strong>

                              {datasetSummary?.columns ?? "--"}

                          </strong>

                      </div>

                      <div className="health-item">

                          <span>Missing Values</span>

                          <strong>

                              {datasetSummary?.missing_values ?? "--"}

                          </strong>

                      </div>

                      <div className="health-item">

                          <span>Numerical</span>

                          <strong>

                              {datasetSummary?.numerical_columns ?? "--"}

                          </strong>

                      </div>

                      <div className="health-item">

                          <span>Categorical</span>

                          <strong>

                              {datasetSummary?.categorical_columns ?? "--"}

                          </strong>

                      </div>

                      <div className="health-item">

                          <span>Status</span>

                          <strong

                              className={

                                  datasetHealth >= 90

                                      ? "status-good"

                                      : datasetHealth >= 70

                                      ? "status-warning"

                                      : "status-danger"

                              }

                          >

                              {

                                  datasetHealth >= 90

                                      ? "Excellent"

                                      : datasetHealth >= 70

                                      ? "Needs Cleaning"

                                      : "Poor"

                              }

                          </strong>

                      </div>

                  </div>

              </div>

              <div className="health-footer">

                  <button

                      className="btn btn-primary"

                      onClick={() => navigate("/cleaning")}

                  >

                      Proceed to Data Cleaning →

                  </button>

              </div>

          </div>
        </div>
      </div>
  )
}

export default DataPage;
