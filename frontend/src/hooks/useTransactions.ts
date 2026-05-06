import { useQuery } from "@tanstack/react-query";
import { fetchTransactions } from "@/api/transactions";
import type { TransactionFilters, TransactionResponse } from "@/types/api";

export function useTransactions(filters: TransactionFilters = {}) {
  return useQuery({
    queryKey: ["transactions", filters],
    queryFn: () => fetchTransactions(filters),
    select: (res) => res.data,
  });
}

// Derived helpers
export function computeMetrics(transactions: TransactionResponse[]) {
  let totalIncome = 0;
  let totalSpending = 0;

  for (const tx of transactions) {
    const amt = parseFloat(tx.amount);
    if (amt > 0) totalIncome += amt;
    else totalSpending += Math.abs(amt);
  }

  return {
    totalIncome,
    totalSpending,
    netBalance: totalIncome - totalSpending,
    transactionCount: transactions.length,
  };
}

export function groupByCategory(transactions: TransactionResponse[]) {
  const map = new Map<string, number>();
  for (const tx of transactions) {
    const cat = tx.category || "OTHER";
    const amt = Math.abs(parseFloat(tx.amount));
    map.set(cat, (map.get(cat) || 0) + amt);
  }
  return Array.from(map.entries())
    .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
    .sort((a, b) => b.value - a.value);
}

export function groupByMonth(transactions: TransactionResponse[]) {
  const map = new Map<string, { income: number; spending: number }>();
  for (const tx of transactions) {
    const month = tx.transaction_date.slice(0, 7); // YYYY-MM
    const entry = map.get(month) || { income: 0, spending: 0 };
    const amt = parseFloat(tx.amount);
    if (amt > 0) entry.income += amt;
    else entry.spending += Math.abs(amt);
    map.set(month, entry);
  }
  return Array.from(map.entries())
    .map(([month, data]) => ({
      month,
      income: Math.round(data.income * 100) / 100,
      spending: Math.round(data.spending * 100) / 100,
    }))
    .sort((a, b) => a.month.localeCompare(b.month));
}
