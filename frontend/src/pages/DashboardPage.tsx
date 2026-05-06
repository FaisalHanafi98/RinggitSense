import { useTransactions, computeMetrics, groupByCategory, groupByMonth } from "@/hooks/useTransactions";
import SummaryMetrics from "@/components/dashboard/SummaryMetrics";
import SpendingChart from "@/components/dashboard/SpendingChart";
import CategoryBreakdown from "@/components/dashboard/CategoryBreakdown";
import RecentTransactions from "@/components/dashboard/RecentTransactions";
import FinancialDisclaimer from "@/components/dashboard/FinancialDisclaimer";
import { AlertCircle } from "lucide-react";

export default function DashboardPage() {
  const { data, isLoading, isError, error } = useTransactions({ limit: 200 });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex items-start gap-3 rounded-[--radius-lg] border border-danger/20 bg-danger-light px-6 py-4">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-danger" />
          <div>
            <h3 className="text-sm font-semibold text-danger">Failed to load dashboard</h3>
            <p className="mt-1 text-sm text-danger/80">
              {error instanceof Error ? error.message : "An unexpected error occurred."}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const transactions = data?.transactions ?? [];
  const metrics = computeMetrics(transactions);
  const categoryData = groupByCategory(transactions);
  const monthlyData = groupByMonth(transactions);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-text-primary">Dashboard</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Your financial overview at a glance.
        </p>
      </div>

      <SummaryMetrics
        netBalance={metrics.netBalance}
        totalSpending={metrics.totalSpending}
        totalIncome={metrics.totalIncome}
        transactionCount={metrics.transactionCount}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <SpendingChart data={monthlyData} />
        </div>
        <div className="lg:col-span-2">
          <CategoryBreakdown data={categoryData} />
        </div>
      </div>

      <RecentTransactions transactions={transactions} />

      <FinancialDisclaimer />
    </div>
  );
}
