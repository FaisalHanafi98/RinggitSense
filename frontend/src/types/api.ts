// TypeScript types matching backend Pydantic schemas

export interface PaginationMeta {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
}

export interface APIResponse<T> {
  success: boolean;
  data: T;
  meta?: Record<string, unknown>;
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface TransactionResponse {
  id: string;
  user_id: string;
  source_id: string | null;
  transaction_date: string;
  amount: string; // Decimal comes as string from API
  description: string;
  original_description: string | null;
  category: string | null;
  category_confidence: string | null;
  subcategory: string | null;
  merchant_name: string | null;
  is_debt_related: boolean;
  debt_tier: string | null;
  debt_id: string | null;
  is_recurring: boolean;
  user_comment: string | null;
  created_at: string;
}

export interface TransactionListResponse {
  transactions: TransactionResponse[];
  pagination: PaginationMeta;
}

export interface UploadValidationDetail {
  row: number;
  field: string;
  error: string;
  value: string | null;
}

export interface DuplicateDetail {
  row: number;
  description: string;
  amount: string;
  date: string;
  status: "DUPLICATE" | "SUSPICIOUS";
}

export interface UploadResponse {
  source_id: string;
  bank_name: string;
  total_parsed: number;
  total_valid: number;
  total_invalid: number;
  total_stored: number;
  duplicates_skipped: number;
  suspicious_duplicates: number;
  validation_errors: UploadValidationDetail[];
  duplicate_details: DuplicateDetail[];
  batch_warnings: string[];
  parser_warnings: string[];
}

export interface UserResponse {
  id: string;
  clerk_id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

// Query params for GET /transactions
export interface TransactionFilters {
  page?: number;
  limit?: number;
  category?: string;
  date_from?: string;
  date_to?: string;
  source_id?: string;
  search?: string;
}

// Category constants matching backend enums
export const CATEGORIES = [
  "FOOD",
  "TRANSPORT",
  "BILLS",
  "ENTERTAINMENT",
  "SHOPPING",
  "TRANSFER",
  "DEBT_PAYMENT",
  "INCOME",
  "HEALTHCARE",
  "OTHER",
] as const;

export type TransactionCategory = (typeof CATEGORIES)[number];

export const SUPPORTED_BANKS = ["maybank", "cimb"] as const;
export type SupportedBank = (typeof SUPPORTED_BANKS)[number];

// Category display config
export const CATEGORY_CONFIG: Record<
  TransactionCategory,
  { label: string; color: string; bg: string }
> = {
  FOOD: { label: "Food & Dining", color: "#ea580c", bg: "#fff7ed" },
  TRANSPORT: { label: "Transport", color: "#2563eb", bg: "#eff6ff" },
  BILLS: { label: "Bills & Utilities", color: "#7c3aed", bg: "#f5f3ff" },
  ENTERTAINMENT: {
    label: "Entertainment",
    color: "#db2777",
    bg: "#fdf2f8",
  },
  SHOPPING: { label: "Shopping", color: "#0891b2", bg: "#ecfeff" },
  TRANSFER: { label: "Transfer", color: "#64748b", bg: "#f8fafc" },
  DEBT_PAYMENT: { label: "Debt Payment", color: "#dc2626", bg: "#fef2f2" },
  INCOME: { label: "Income", color: "#16a34a", bg: "#f0fdf4" },
  HEALTHCARE: { label: "Healthcare", color: "#0d9488", bg: "#f0fdfa" },
  OTHER: { label: "Other", color: "#71717a", bg: "#f4f4f5" },
};
