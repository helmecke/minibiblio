import { getTranslations } from "next-intl/server";
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
  const t = await getTranslations("catalog");
  const tErrors = await getTranslations("errors");
  let items = [];
  let error = null;

  try {
    items = await getCatalogItems();
  } catch (e) {
    error = e instanceof Error ? e.message : tErrors("failedToLoad", { resource: t("title") });
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t("title")}</h1>
          <p className="text-muted-foreground">
            {t("description")}
          </p>
        </div>
        <AddCatalogDialog />
      </div>

      {error ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
          {error}. {tErrors("serverNotRunning")}
        </div>
      ) : (
        <CatalogTable items={items} />
      )}
    </div>
  );
}
