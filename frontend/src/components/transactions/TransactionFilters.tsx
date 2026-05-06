import { useState, useEffect, useCallback, useRef } from "react";
import { CATEGORIES, CATEGORY_CONFIG, type TransactionCategory } from "@/types/api";
import type { TransactionFilters as Filters } from "@/types/api";

interface TransactionFiltersProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
}

export default function TransactionFilters({ filters, onChange }: TransactionFiltersProps) {
  const [searchInput, setSearchInput] = useState(filters.search || "");
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const handleSearch = useCallback(
    (value: string) => {
      setSearchInput(value);
      clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        onChange({ ...filters, search: value || undefined, page: 1 });
      }, 300);
    },
    [filters, onChange]
  );

  useEffect(() => {
    return () => clearTimeout(debounceRef.current);
  }, []);

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Category */}
      <label className="sr-only" htmlFor="filter-category">Category</label>
      <select
        id="filter-category"
        value={filters.category || ""}
        onChange={(e) => onChange({ ...filters, category: e.target.value || undefined, page: 1 })}
        className="rounded-[--radius-md] border border-border bg-card px-3 py-1.5 text-sm text-text-primary outline-none focus:border-accent"
      >
        <option value="">All Categories</option>
        {CATEGORIES.map((cat) => (
          <option key={cat} value={cat}>
            {CATEGORY_CONFIG[cat as TransactionCategory].label}
          </option>
        ))}
      </select>

      {/* Date From */}
      <label className="sr-only" htmlFor="filter-date-from">Date from</label>
      <input
        id="filter-date-from"
        type="date"
        value={filters.date_from || ""}
        onChange={(e) => onChange({ ...filters, date_from: e.target.value || undefined, page: 1 })}
        className="rounded-[--radius-md] border border-border bg-card px-3 py-1.5 text-sm text-text-primary outline-none focus:border-accent"
      />

      {/* Date To */}
      <label className="sr-only" htmlFor="filter-date-to">Date to</label>
      <input
        id="filter-date-to"
        type="date"
        value={filters.date_to || ""}
        onChange={(e) => onChange({ ...filters, date_to: e.target.value || undefined, page: 1 })}
        className="rounded-[--radius-md] border border-border bg-card px-3 py-1.5 text-sm text-text-primary outline-none focus:border-accent"
      />

      {/* Search (debounced) */}
      <label className="sr-only" htmlFor="filter-search">Search transactions</label>
      <input
        id="filter-search"
        type="text"
        value={searchInput}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search transactions..."
        className="rounded-[--radius-md] border border-border bg-card px-3 py-1.5 text-sm text-text-primary outline-none focus:border-accent"
      />

      {/* Reset */}
      {(filters.category || filters.date_from || filters.date_to || filters.search) && (
        <button
          onClick={() => {
            setSearchInput("");
            onChange({ page: 1, limit: filters.limit });
          }}
          aria-label="Clear all filters"
          className="text-xs font-medium text-accent hover:text-accent-hover"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
