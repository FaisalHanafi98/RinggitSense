import { lazy, Suspense, useEffect } from "react";
import { ClerkProvider, RedirectToSignIn, useAuth } from "@clerk/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router";
import DashboardLayout from "@/components/layout/DashboardLayout";
import ErrorBoundary from "@/components/ErrorBoundary";
import { setTokenGetter } from "@/api/client";

const DashboardPage = lazy(() => import("@/pages/DashboardPage"));
const TransactionsPage = lazy(() => import("@/pages/TransactionsPage"));
const UploadPage = lazy(() => import("@/pages/UploadPage"));
const NotFoundPage = lazy(() => import("@/pages/NotFoundPage"));

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

function PageLoader() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
    </div>
  );
}

function AuthProvider({ children }: { children: React.ReactNode }) {
  const { getToken } = useAuth();
  useEffect(() => {
    setTokenGetter(getToken);
  }, [getToken]);
  return <>{children}</>;
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) return <PageLoader />;
  if (!isSignedIn) return <RedirectToSignIn />;
  return <>{children}</>;
}

export default function App() {
  return (
    <ErrorBoundary>
      <ClerkProvider publishableKey={clerkPubKey}>
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            <BrowserRouter>
              <Suspense fallback={<PageLoader />}>
                <Routes>
                  <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
                    <Route index element={<DashboardPage />} />
                    <Route path="transactions" element={<TransactionsPage />} />
                    <Route path="upload" element={<UploadPage />} />
                    <Route path="*" element={<NotFoundPage />} />
                  </Route>
                </Routes>
              </Suspense>
            </BrowserRouter>
          </QueryClientProvider>
        </AuthProvider>
      </ClerkProvider>
    </ErrorBoundary>
  );
}
