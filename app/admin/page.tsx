import { auth } from "@/lib/auth";
import { Package, Users2, BookOpen, TrendingUp } from "lucide-react";

interface Patron {
  id: string;
  status: "active" | "inactive" | "suspended";
}

async function getPatrons(): Promise<Patron[]> {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/python/patrons", {
      cache: "no-store",
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function AdminDashboard() {
  const session = await auth();
  const patrons = await getPatrons();
  const activePatrons = patrons.filter((p) => p.status === "active").length;
  const totalPatrons = patrons.length;

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
            <h3 className="text-sm font-medium">Total Books</h3>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="text-2xl font-bold">0</div>
          <p className="text-xs text-muted-foreground">
            No books added yet
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
          <div className="text-2xl font-bold">0</div>
          <p className="text-xs text-muted-foreground">
            No active loans
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
