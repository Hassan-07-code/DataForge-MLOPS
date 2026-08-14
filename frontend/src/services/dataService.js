import { apiRequest } from "./api";


export async function fetchDatasets() {
  return apiRequest("/api/datasets");
}


export async function uploadDataset(file) {
  if (!file) {
    throw new Error("No dataset file selected.");
  }

  const formData = new FormData();
  formData.append("file", file);

  return apiRequest("/api/datasets/upload", {
    method: "POST",
    body: formData,
  });
}

export async function fetchDataset(datasetName) {
  if (!datasetName) {
    throw new Error("Dataset name is required.");
  }

  return apiRequest(
    `/api/datasets/${encodeURIComponent(datasetName)}`
  );
}


export async function fetchVisualization(datasetName) {
  if (!datasetName) {
    throw new Error("Dataset name is required.");
  }

  return apiRequest(
    `/api/visualizations/${encodeURIComponent(datasetName)}`
  );
}

export async function cleanDataset({
  dataset_name,
  operations = {},
}) {
  if (!dataset_name) {
    throw new Error("Dataset name is required.");
  }

  return apiRequest("/api/datasets/clean", {
    method: "POST",
    body: {
      dataset_name,
      operations,
    },
  });
}