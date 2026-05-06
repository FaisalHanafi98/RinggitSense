import { Link, useLocation } from "react-router";
import { UserButton, SignInButton, useAuth } from "@clerk/react";

const NAV_ITEMS = [
  { label: "Dashboard", path: "/" },
  { label: "Transactions", path: "/transactions" },
  { label: "Upload", path: "/upload" },
];

export default function Header() {
  const location = useLocation();
  const { isSignedIn } = useAuth();

  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex h-14 max-w-[1280px] items-center justify-between px-6">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 no-underline">
          <span className="text-lg font-semibold tracking-tight text-text-primary">
            RinggitSense
          </span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`rounded-md px-3 py-1.5 text-sm font-medium no-underline transition-colors ${
                  isActive
                    ? "bg-accent-light text-accent"
                    : "text-text-secondary hover:text-text-primary hover:bg-border-light"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Auth */}
        <div className="flex items-center gap-3">
          {isSignedIn ? (
            <UserButton />
          ) : (
            <SignInButton mode="modal">
              <button className="rounded-md bg-accent px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-accent-hover">
                Sign in
              </button>
            </SignInButton>
          )}
        </div>
      </div>
    </header>
  );
}
