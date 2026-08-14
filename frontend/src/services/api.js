const API_BASE_URL =
import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function apiRequest(endpoint, options = {}) {
const {
method = "GET",
body,
headers = {},
signal,
timeout = 30000,
} = options;

const controller = new AbortController();

const timeoutId = setTimeout(() => {
controller.abort();
}, timeout);

if (signal) {
signal.addEventListener(
"abort",
() => controller.abort(),
{ once: true }
);
}

const config = {
method,
headers: {
Accept: "application/json",
...headers,
},
signal: controller.signal,
};

if (body !== undefined) {
if (body instanceof FormData) {
config.body = body;
} else {
config.headers["Content-Type"] = "application/json";
config.body = JSON.stringify(body);
}
}

try {
const response = await fetch(
`${API_BASE_URL}${endpoint}`,
config
);


const contentType =
  response.headers.get("content-type") || "";

let data;

if (contentType.includes("application/json")) {
  data = await response.json();
} else {
  data = await response.text();
}

if (!response.ok) {
  let message = `API request failed with status ${response.status}`;

  if (typeof data === "string" && data.trim()) {
    message = data;
  } else if (data?.detail) {
    message =
      typeof data.detail === "string"
        ? data.detail
        : data.detail.message ||
          JSON.stringify(data.detail);
  } else if (data?.message) {
    message = data.message;
  }

  const error = new Error(message);
  error.status = response.status;
  error.data = data;

  throw error;
}

return data;
```

} catch (error) {
if (error.name === "AbortError") {
throw new Error("API request timed out.");
}

```
if (error instanceof TypeError) {
  throw new Error(
    "Unable to connect to the DataForge backend."
  );
}

throw error;


} finally {
clearTimeout(timeoutId);
}
}

export { API_BASE_URL, apiRequest };

export default API_BASE_URL;
