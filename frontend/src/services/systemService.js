import { apiRequest } from "./api";

export async function fetchHealth() {
return apiRequest("/api/health");
}

export async function fetchSystemMetrics() {
return apiRequest("/api/system");
}
