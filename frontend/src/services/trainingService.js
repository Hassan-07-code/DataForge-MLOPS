import { apiRequest } from "./api";

  export async function trainModel(payload) {
  if (!payload || typeof payload !== "object") {
  throw new Error("Training payload is required.");
  }

return apiRequest("/api/train", {
method: "POST",
body: payload,
});
}

  export async function fetchExperiments() {
  return apiRequest("/api/experiments");
  }
