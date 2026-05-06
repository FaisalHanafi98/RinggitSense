import { useState, useMemo, useCallback } from "react";
import { useTransactions } from "@/hooks/useTransactions";
import TransactionTable from "@/components/transactions/TransactionTable";
import TransactionFiltersComponent from "@/components/transactions/TransactionFilters";
import type { TransactionFilters } from "@/types/api";
import { ChevronLeft, ChevronRight, AlertCircle } from "lucide-react";

export default function TransactionsPage() {
  const [filters, setFilters] = useState<TransactionFilters>({ page: 1, limit: 25 });
  const { data, isLoading, isError, error } = useTransactions(filters);

  const pagination = data?.pagination;

  const handleFilters = useCallback((next: TransactionFilters) => {
    setFilters(next);
  }, []);

  const prevPage = useMemo(
    () => () => setFilters((f) => ({ ...f, page: (f.page || 1) - 1 })),
    []
  );
  const nextPage = useMemo(
    () => () => setFilters((f) => ({ ...f, page: (f.page || 1) + 1 })),
    []
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-text-primary">Transactions</h1>
        <p className="mt-1 text-sm text-text-secondary">
          View and filter your financial transactions.
        </p>
      </div>

      <TransactionFiltersComponent filters={filters} onChange={handleFilters} />

      {isError ? (
        <div className="flex items-start gap-3 rounded-[--radius-lg] border border-danger/20 bg-danger-light px-6 py-4">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-danger" />
          <div>
            <h3 className="text-sm font-semibold text-danger">Failed to load transactions</h3>
            <p className="mt-1 text-sm text-danger/80">
              {error instanceof Error ? error.message : "An unexpected error occurred."}
            </p>
          </div>
        </div>
      ) : isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
        </div>
      ) : (
        <>
          <TransactionTable transactions={data?.transactions ?? []} />

          {/* Pagination */}
          {pagination && pagination.total_pages > 1 && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-text-muted">
                Page {pagination.page} of {pagination.total_pages} ({pagination.total_items} total)
              </span>
              <div className="flex gap-2">
                <button
                  onClick={prevPage}
                  disabled={pagination.page <= 1}
                  aria-label="Previous page"
                  className="flex items-center gap-1 rounded-[--radius-md] border border-border px-3 py-1.5 text-sm text-text-secondary transition-colors hover:bg-border-light disabled:opacity-40"
                >
                  <ChevronLeft className="h-4 w-4" /> Previous
                </button>
                <button
                  onClick={nextPage}
                  disabled={pagination.page >= pagination.total_pages}
                  aria-label="Next page"
                  className="flex items-center gap-1 rounded-[--radius-md] border border-border px-3 py-1.5 text-sm text-text-secondary transition-colors hover:bg-border-light disabled:opacity-40"
                >
                  Next <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
