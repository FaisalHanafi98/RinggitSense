import { type ReactNode } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string;
  trend?: {
    direction: "up" | "down" | "flat";
    label: string;
  };
  icon?: ReactNode;
}

export default function MetricCard({ label, value, trend, icon }: MetricCardProps) {
  return (
    <div className="rounded-[--radius-lg] border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-text-secondary">{label}</span>
        {icon && <span className="text-text-muted">{icon}</span>}
      </div>
      <p className="mt-2 font-mono text-2xl font-semibold tracking-tight text-text-primary">
        {value}
      </p>
      {trend && (
        <div className="mt-2 flex items-center gap-1">
          {trend.direction === "up" && (
            <TrendingUp className="h-3.5 w-3.5 text-success" />
          )}
          {trend.direction === "down" && (
            <TrendingDown className="h-3.5 w-3.5 text-danger" />
          )}
          {trend.direction === "flat" && (
            <Minus className="h-3.5 w-3.5 text-text-muted" />
          )}
          <span
            className={`text-xs font-medium ${
              trend.direction === "up"
                ? "text-success"
                : trend.direction === "down"
                  ? "text-danger"
                  : "text-text-muted"
            }`}
          >
            {trend.label}
          </span>
        </div>
      )}
    </div>
  );
}
