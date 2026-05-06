import { Link } from "react-router";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="text-center">
        <p className="font-mono text-6xl font-bold text-border">404</p>
        <h1 className="mt-4 text-xl font-semibold text-text-primary">Page not found</h1>
        <p className="mt-2 text-sm text-text-secondary">
          The page you're looking for doesn't exist.
        </p>
        <Link
          to="/"
          className="mt-6 inline-block rounded-[--radius-md] bg-accent px-5 py-2 text-sm font-medium text-white no-underline hover:bg-accent-hover"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
