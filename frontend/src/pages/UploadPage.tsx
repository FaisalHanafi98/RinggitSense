import StatementUpload from "@/components/upload/StatementUpload";

export default function UploadPage() {
  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-text-primary">Upload Statement</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Upload your bank statement to import transactions.
        </p>
      </div>
      <StatementUpload />
    </div>
  );
}
