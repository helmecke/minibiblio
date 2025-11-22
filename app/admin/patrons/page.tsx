import { PatronsTable } from "./patrons-table";

async function getPatrons() {
  const res = await fetch("http://127.0.0.1:8000/api/python/patrons", {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch patrons");
  }
  return res.json();
}

export default async function PatronsPage() {
  let patrons = [];
  let error = null;

  try {
    patrons = await getPatrons();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load patrons";
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Patrons</h1>
          <p className="text-muted-foreground">
            Manage library members and their information
          </p>
        </div>
      </div>

      {error ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
          {error}. Make sure the FastAPI server is running.
        </div>
      ) : (
        <PatronsTable patrons={patrons} />
      )}
    </div>
  );
}
