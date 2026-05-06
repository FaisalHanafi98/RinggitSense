import { Outlet } from "react-router";
import Header from "./Header";

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-bg">
      <Header />
      <main className="mx-auto max-w-[1280px] px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
