import { auth } from "@/lib/auth";
import { Package, Users2, BookOpen, TrendingUp } from "lucide-react";

interface CountResponse {
  count: number;
}

async function getPatronCount(status?: string): Promise<number> {
  try {
    const url = status
      ? `http://127.0.0.1:8000/api/python/patrons/count?status=${status}`
      : "http://127.0.0.1:8000/api/python/patrons/count";
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return 0;
    const data: CountResponse = await res.json();
    return data.count;
  } catch {
    return 0;
  }
}

async function getCatalogCount(type?: string, status?: string): Promise<number> {
  try {
    const params = new URLSearchParams();
    if (type) params.set("type", type);
    if (status) params.set("status", status);
    const query = params.toString();
    const url = query
      ? `http://127.0.0.1:8000/api/python/catalog/count?${query}`
      : "http://127.0.0.1:8000/api/python/catalog/count";
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return 0;
    const data: CountResponse = await res.json();
    return data.count;
  } catch {
    return 0;
  }
}

export default async function AdminDashboard() {
  const session = await auth();
  const [activePatrons, totalPatrons, totalCatalog, borrowedItems] = await Promise.all([
    getPatronCount("active"),
    getPatronCount(),
    getCatalogCount(),
    getCatalogCount(undefined, "borrowed"),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {session?.user?.name || "Admin"}!
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Catalog Items</h3>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="text-2xl font-bold">{totalCatalog}</div>
          <p className="text-xs text-muted-foreground">
            {totalCatalog === 0 ? "No items added yet" : "Books and media"}
          </p>
        </div>

        <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Active Patrons</h3>
            <Users2 className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="text-2xl font-bold">{activePatrons}</div>
          <p className="text-xs text-muted-foreground">
            {totalPatrons} total patrons
          </p>
        </div>

        <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">Borrowed</h3>
            <Package className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="text-2xl font-bold">{borrowedItems}</div>
          <p className="text-xs text-muted-foreground">
            {borrowedItems === 0 ? "No active loans" : "Items currently borrowed"}
          </p>
        </div>

        <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
          <div className="flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="text-sm font-medium">This Month</h3>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="text-2xl font-bold">0</div>
          <p className="text-xs text-muted-foreground">
            Transactions this month
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <p className="text-muted-foreground">
          Start by adding books to your library or inviting users.
        </p>
      </div>
    </div>
  );
}
