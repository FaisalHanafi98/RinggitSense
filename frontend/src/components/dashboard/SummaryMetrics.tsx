import MetricCard from "@/components/layout/MetricCard";
import { Wallet, TrendingDown, TrendingUp, Receipt } from "lucide-react";

interface SummaryMetricsProps {
  netBalance: number;
  totalSpending: number;
  totalIncome: number;
  transactionCount: number;
}

function formatRM(amount: number): string {
  return `RM ${Math.abs(amount).toLocaleString("en-MY", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function SummaryMetrics({
  netBalance,
  totalSpending,
  totalIncome,
  transactionCount,
}: SummaryMetricsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard
        label="Net Balance"
        value={formatRM(netBalance)}
        icon={<Wallet className="h-4 w-4" />}
      />
      <MetricCard
        label="Total Spending"
        value={formatRM(totalSpending)}
        icon={<TrendingDown className="h-4 w-4" />}
      />
      <MetricCard
        label="Total Income"
        value={formatRM(totalIncome)}
        icon={<TrendingUp className="h-4 w-4" />}
      />
      <MetricCard
        label="Transactions"
        value={transactionCount.toLocaleString()}
        icon={<Receipt className="h-4 w-4" />}
      />
    </div>
  );
}
