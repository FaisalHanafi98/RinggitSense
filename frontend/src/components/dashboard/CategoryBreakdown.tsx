import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { CATEGORY_CONFIG, type TransactionCategory } from "@/types/api";

interface CategoryData {
  name: string;
  value: number;
}

interface CategoryBreakdownProps {
  data: CategoryData[];
}

const CHART_COLORS = [
  "#4f46e5", "#ea580c", "#2563eb", "#7c3aed", "#db2777",
  "#0891b2", "#16a34a", "#d97706", "#0d9488", "#71717a",
];

export default function CategoryBreakdown({ data }: CategoryBreakdownProps) {
  if (data.length === 0) {
    return (
      <div className="rounded-[--radius-lg] border border-border bg-card p-6">
        <h3 className="text-sm font-medium text-text-secondary">Category Breakdown</h3>
        <p className="mt-8 text-center text-sm text-text-muted">No category data yet.</p>
      </div>
    );
  }

  const total = data.reduce((sum, d) => sum + d.value, 0);

  return (
    <div className="rounded-[--radius-lg] border border-border bg-card p-6">
      <h3 className="mb-4 text-sm font-medium text-text-secondary">Category Breakdown</h3>
      <div className="flex items-center gap-6">
        <div className="h-[200px] w-[200px] shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={2}
                dataKey="value"
                stroke="none"
              >
                {data.map((_entry, index) => (
                  <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "#fff",
                  border: "1px solid #e4e4e7",
                  borderRadius: "8px",
                  fontSize: "13px",
                }}
                formatter={(value) => [`RM ${Number(value).toLocaleString("en-MY", { minimumFractionDigits: 2 })}`]}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-col gap-2 overflow-hidden">
          {data.slice(0, 6).map((item, i) => {
            const config = CATEGORY_CONFIG[item.name as TransactionCategory];
            const pct = total > 0 ? ((item.value / total) * 100).toFixed(1) : "0";
            return (
              <div key={item.name} className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 shrink-0 rounded-full"
                  style={{ background: CHART_COLORS[i % CHART_COLORS.length] }}
                />
                <span className="truncate text-sm text-text-primary">
                  {config?.label || item.name}
                </span>
                <span className="ml-auto whitespace-nowrap font-mono text-xs text-text-muted">
                  {pct}%
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
