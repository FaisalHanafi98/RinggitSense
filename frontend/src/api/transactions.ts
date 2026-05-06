import apiClient from "./client";
import type {
  APIResponse,
  TransactionListResponse,
  TransactionFilters,
  UploadResponse,
  SupportedBank,
} from "@/types/api";

export async function fetchTransactions(
  filters: TransactionFilters = {}
): Promise<APIResponse<TransactionListResponse>> {
  const params = new URLSearchParams();

  if (filters.page) params.set("page", String(filters.page));
  if (filters.limit) params.set("limit", String(filters.limit));
  if (filters.category) params.set("category", filters.category);
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  if (filters.source_id) params.set("source_id", filters.source_id);
  if (filters.search) params.set("search", filters.search);

  const { data } = await apiClient.get<
    APIResponse<TransactionListResponse>
  >(`/api/v1/transactions?${params.toString()}`);
  return data;
}

export async function uploadStatement(
  file: File,
  bank: SupportedBank
): Promise<APIResponse<UploadResponse>> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post<APIResponse<UploadResponse>>(
    `/api/v1/transactions/upload?bank=${bank}`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return data;
}
