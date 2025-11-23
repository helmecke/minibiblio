import { getTranslations } from "next-intl/server";
import { LoansTable } from "./loans-table";
import { CheckoutDialog } from "./checkout-dialog";

async function getLoans() {
  const res = await fetch("http://127.0.0.1:8000/api/python/loans", {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch loans");
  }
  return res.json();
}

export default async function CirculationPage() {
  const t = await getTranslations("circulation");
  const tErrors = await getTranslations("errors");
  let loans = [];
  let error = null;

  try {
    loans = await getLoans();
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
        <CheckoutDialog />
      </div>

      {error ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
          {error}. {tErrors("serverNotRunning")}
        </div>
      ) : (
        <LoansTable loans={loans} />
      )}
    </div>
  );
}
