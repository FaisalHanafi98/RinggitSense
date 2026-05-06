import axios, { type AxiosError } from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  headers: {
    "Content-Type": "application/json",
  },
});

// Token getter — set by AuthProvider component after Clerk mounts
let getToken: (() => Promise<string | null>) | null = null;

export function setTokenGetter(fn: () => Promise<string | null>) {
  getToken = fn;
}

// Auth interceptor — adds Bearer token to all requests
apiClient.interceptors.request.use(async (config) => {
  if (getToken) {
    const token = await getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Error interceptor — normalizes error responses
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string; message?: string }>) => {
    const status = error.response?.status;
    const detail =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message;

    if (status === 401) {
      console.warn("[API] Unauthorized — redirecting to sign-in");
    } else if (status === 413) {
      return Promise.reject(new Error("File too large. Maximum size is 10MB."));
    } else if (status === 422) {
      return Promise.reject(new Error(`Validation error: ${detail}`));
    } else if (status && status >= 500) {
      return Promise.reject(new Error("Server error. Please try again later."));
    } else if (!error.response) {
      return Promise.reject(new Error("Network error. Check your connection."));
    }

    return Promise.reject(new Error(detail || "An unexpected error occurred."));
  }
);

export default apiClient;
