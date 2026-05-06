import type { TransactionResponse } from "@/types/api";
import { CATEGORY_CONFIG, type TransactionCategory } from "@/types/api";

interface TransactionTableProps {
  transactions: TransactionResponse[];
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-MY", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function TransactionTable({ transactions }: TransactionTableProps) {
  if (transactions.length === 0) {
    return (
      <div className="rounded-[--radius-lg] border border-border bg-card px-6 py-12 text-center">
        <p className="text-sm text-text-muted">No transactions found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-[--radius-lg] border border-border bg-card">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left">
            <th className="px-6 py-3 text-xs font-medium uppercase tracking-wider text-text-muted">
              Date
            </th>
            <th className="px-6 py-3 text-xs font-medium uppercase tracking-wider text-text-muted">
              Description
            </th>
            <th className="px-6 py-3 text-xs font-medium uppercase tracking-wider text-text-muted">
              Category
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-text-muted">
              Amount
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border-light">
          {transactions.map((tx) => {
            const amt = parseFloat(tx.amount);
            const isPositive = amt > 0;
            const cat = tx.category as TransactionCategory | null;
            const config = cat ? CATEGORY_CONFIG[cat] : null;

            return (
              <tr key={tx.id} className="transition-colors hover:bg-border-light/50">
                <td className="whitespace-nowrap px-6 py-3 font-mono text-xs text-text-secondary">
                  {formatDate(tx.transaction_date)}
                </td>
                <td className="max-w-[300px] truncate px-6 py-3 text-text-primary">
                  {tx.description}
                </td>
                <td className="px-6 py-3">
                  {config ? (
                    <span
                      className="inline-block rounded-full px-2.5 py-0.5 text-[11px] font-medium"
                      style={{ color: config.color, backgroundColor: config.bg }}
                    >
                      {config.label}
                    </span>
                  ) : (
                    <span className="text-xs text-text-muted">—</span>
                  )}
                </td>
                <td
                  className={`whitespace-nowrap px-6 py-3 text-right font-mono font-medium ${
                    isPositive ? "text-success" : "text-text-primary"
                  }`}
                >
                  {isPositive ? "+" : "-"}RM{" "}
                  {Math.abs(amt).toLocaleString("en-MY", { minimumFractionDigits: 2 })}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
