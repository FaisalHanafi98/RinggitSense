import { useState, useCallback, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadStatement } from "@/api/transactions";
import { SUPPORTED_BANKS, type SupportedBank, type UploadResponse } from "@/types/api";
import { Upload, FileText, CheckCircle, AlertCircle, X } from "lucide-react";

export default function StatementUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [bank, setBank] = useState<SupportedBank>("maybank");
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error("No file selected");
      return uploadStatement(file, bank);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.name.endsWith(".csv")) {
      setFile(dropped);
    }
  }, []);

  const result = mutation.data?.data as UploadResponse | undefined;

  return (
    <div className="space-y-6">
      {/* Bank Selector */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-text-primary">
          Select Bank
        </label>
        <select
          value={bank}
          onChange={(e) => setBank(e.target.value as SupportedBank)}
          className="rounded-[--radius-md] border border-border bg-card px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
        >
          {SUPPORTED_BANKS.map((b) => (
            <option key={b} value={b}>
              {b.charAt(0).toUpperCase() + b.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-[--radius-lg] border-2 border-dashed p-10 text-center transition-colors ${
          dragActive
            ? "border-accent bg-accent-light"
            : "border-border hover:border-accent/50 hover:bg-border-light"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) setFile(f);
          }}
        />
        <Upload className="mx-auto h-8 w-8 text-text-muted" />
        <p className="mt-3 text-sm font-medium text-text-primary">
          Drop your CSV statement here, or click to browse
        </p>
        <p className="mt-1 text-xs text-text-muted">CSV files only, max 10MB</p>
      </div>

      {/* Selected File */}
      {file && !mutation.isSuccess && (
        <div className="flex items-center gap-3 rounded-[--radius-md] border border-border bg-card px-4 py-3">
          <FileText className="h-5 w-5 text-accent" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-text-primary">{file.name}</p>
            <p className="text-xs text-text-muted">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
          <button onClick={() => setFile(null)} className="text-text-muted hover:text-text-primary">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Upload Button */}
      {file && !mutation.isSuccess && (
        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="w-full rounded-[--radius-md] bg-accent px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:opacity-60"
        >
          {mutation.isPending ? "Uploading..." : "Upload Statement"}
        </button>
      )}

      {/* Error */}
      {mutation.isError && (
        <div className="flex items-start gap-3 rounded-[--radius-md] border border-danger/20 bg-danger-light px-4 py-3">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-danger" />
          <p className="text-sm text-danger">
            Upload failed. Please check your file and try again.
          </p>
        </div>
      )}

      {/* Success */}
      {result && (
        <div className="rounded-[--radius-lg] border border-success/20 bg-success-light p-5">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-success" />
            <h3 className="text-sm font-semibold text-success">Upload Complete</h3>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Stat label="Parsed" value={result.total_parsed} />
            <Stat label="Stored" value={result.total_stored} />
            <Stat label="Duplicates" value={result.duplicates_skipped} />
            <Stat label="Invalid" value={result.total_invalid} />
          </div>
          {result.batch_warnings.length > 0 && (
            <div className="mt-3 text-xs text-warning">
              {result.batch_warnings.map((w, i) => (
                <p key={i}>{w}</p>
              ))}
            </div>
          )}
          <button
            onClick={() => {
              setFile(null);
              mutation.reset();
            }}
            className="mt-4 text-sm font-medium text-accent hover:text-accent-hover"
          >
            Upload another statement
          </button>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <p className="text-xs text-text-secondary">{label}</p>
      <p className="font-mono text-lg font-semibold text-text-primary">{value}</p>
    </div>
  );
}
