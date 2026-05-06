import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface MonthlyData {
  month: string;
  income: number;
  spending: number;
}

interface SpendingChartProps {
  data: MonthlyData[];
}

function formatMonth(month: string): string {
  const [year, m] = month.split("-");
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${months[parseInt(m, 10) - 1]} ${year.slice(2)}`;
}

export default function SpendingChart({ data }: SpendingChartProps) {
  if (data.length === 0) {
    return (
      <div className="rounded-[--radius-lg] border border-border bg-card p-6">
        <h3 className="text-sm font-medium text-text-secondary">Monthly Overview</h3>
        <p className="mt-8 text-center text-sm text-text-muted">
          Upload a bank statement to see your spending trends.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-[--radius-lg] border border-border bg-card p-6">
      <h3 className="mb-6 text-sm font-medium text-text-secondary">Monthly Overview</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="gradientSpending" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4f46e5" stopOpacity={0.15} />
              <stop offset="100%" stopColor="#4f46e5" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradientIncome" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#16a34a" stopOpacity={0.1} />
              <stop offset="100%" stopColor="#16a34a" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" vertical={false} />
          <XAxis
            dataKey="month"
            tickFormatter={formatMonth}
            tick={{ fontSize: 12, fill: "#71717a" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#71717a" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              background: "#fff",
              border: "1px solid #e4e4e7",
              borderRadius: "8px",
              fontSize: "13px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
            }}
            formatter={(value) => [`RM ${Number(value).toLocaleString("en-MY", { minimumFractionDigits: 2 })}`]}
            labelFormatter={(label) => formatMonth(String(label))}
          />
          <Area
            type="monotone"
            dataKey="income"
            stroke="#16a34a"
            strokeWidth={2}
            fill="url(#gradientIncome)"
            name="Income"
          />
          <Area
            type="monotone"
            dataKey="spending"
            stroke="#4f46e5"
            strokeWidth={2}
            fill="url(#gradientSpending)"
            name="Spending"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
