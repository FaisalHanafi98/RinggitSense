export default function FinancialDisclaimer() {
  return (
    <div className="rounded-[--radius-md] border border-border-light bg-card px-4 py-3">
      <p className="text-[11px] leading-relaxed text-text-muted">
        <strong className="font-medium text-text-secondary">Disclaimer:</strong>{" "}
        This is not professional financial advice. Consult a licensed financial
        advisor for major decisions. Past patterns do not guarantee future
        results. Your data is processed locally and protected under PDPA
        (Malaysia).
      </p>
    </div>
  );
}
