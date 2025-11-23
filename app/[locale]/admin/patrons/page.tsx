import { getTranslations } from "next-intl/server";
import { PatronsTable } from "./patrons-table";
import { AddPatronDialog } from "./add-patron-dialog";

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
  const t = await getTranslations("patrons");
  const tErrors = await getTranslations("errors");
  let patrons = [];
  let error = null;

  try {
    patrons = await getPatrons();
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
        <AddPatronDialog />
      </div>

      {error ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
          {error}. {tErrors("serverNotRunning")}
        </div>
      ) : (
        <PatronsTable patrons={patrons} />
      )}
    </div>
  );
}
