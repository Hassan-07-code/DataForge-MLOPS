import { apiRequest } from "./api";

export async function fetchRegistry() {
return apiRequest("/api/registry");
}

export async function promoteModel(payload) {
if (!payload || typeof payload !== "object") {
throw new Error("Promotion payload is required.");
}

return apiRequest("/api/models/promote", {
method: "POST",
body: payload,
});
}
