import { CatalogTable } from "./catalog-table";
import { AddCatalogDialog } from "./add-catalog-dialog";

async function getCatalogItems() {
  const res = await fetch("http://127.0.0.1:8000/api/python/catalog", {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch catalog items");
  }
  return res.json();
}

export default async function CatalogPage() {
  let items = [];
  let error = null;

  try {
    items = await getCatalogItems();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load catalog items";
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Catalog</h1>
          <p className="text-muted-foreground">
            Manage books and media in your library
          </p>
        </div>
        <AddCatalogDialog />
      </div>

      {error ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
          {error}. Make sure the FastAPI server is running.
        </div>
      ) : (
        <CatalogTable items={items} />
      )}
    </div>
  );
}
