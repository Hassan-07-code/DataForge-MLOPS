import API_BASE_URL from "./api";

export async function predict(data) {
  const response = await fetch(`${API_BASE_URL}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errText = await response.text();
    throw new Error(errText || "Prediction failed");
  }
  return await response.json();
}

export async function batchPredict(data) {
  const response = await fetch(`${API_BASE_URL}/api/batch_predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errText = await response.text();
    throw new Error(errText || "Batch prediction failed");
  }
  return await response.json();
}

export async function fetchPredictionLogs() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/predictions/logs`);
    if (!response.ok) throw new Error("Failed to fetch logs");
    return await response.json();
  } catch (err) {
    console.warn("Prediction logs fetch error:", err);
    return [];
  }
}
