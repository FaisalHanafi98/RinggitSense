import { Link } from "react-router";
import type { TransactionResponse } from "@/types/api";
import { CATEGORY_CONFIG, type TransactionCategory } from "@/types/api";

interface RecentTransactionsProps {
  transactions: TransactionResponse[];
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-MY", { day: "numeric", month: "short" });
}

function formatAmount(amount: string): { text: string; isPositive: boolean } {
  const num = parseFloat(amount);
  const isPositive = num > 0;
  return {
    text: `${isPositive ? "+" : "-"}RM ${Math.abs(num).toLocaleString("en-MY", { minimumFractionDigits: 2 })}`,
    isPositive,
  };
}

export default function RecentTransactions({ transactions }: RecentTransactionsProps) {
  const recent = transactions.slice(0, 8);

  return (
    <div className="rounded-[--radius-lg] border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-6 py-4">
        <h3 className="text-sm font-medium text-text-secondary">Recent Transactions</h3>
        <Link
          to="/transactions"
          className="text-xs font-medium text-accent no-underline hover:text-accent-hover"
        >
          View all
        </Link>
      </div>
      {recent.length === 0 ? (
        <p className="px-6 py-8 text-center text-sm text-text-muted">
          No transactions yet. Upload a statement to get started.
        </p>
      ) : (
        <div className="divide-y divide-border-light">
          {recent.map((tx) => {
            const { text, isPositive } = formatAmount(tx.amount);
            const cat = tx.category as TransactionCategory | null;
            const config = cat ? CATEGORY_CONFIG[cat] : null;

            return (
              <div key={tx.id} className="flex items-center gap-4 px-6 py-3">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-text-primary">
                    {tx.description}
                  </p>
                  <div className="mt-0.5 flex items-center gap-2">
                    <span className="text-xs text-text-muted">
                      {formatDate(tx.transaction_date)}
                    </span>
                    {config && (
                      <span
                        className="rounded-full px-2 py-0.5 text-[10px] font-medium"
                        style={{ color: config.color, backgroundColor: config.bg }}
                      >
                        {config.label}
                      </span>
                    )}
                  </div>
                </div>
                <span
                  className={`whitespace-nowrap font-mono text-sm font-medium ${
                    isPositive ? "text-success" : "text-text-primary"
                  }`}
                >
                  {text}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
