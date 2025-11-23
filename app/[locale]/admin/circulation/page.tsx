import { getTranslations } from "next-intl/server";
import { CirculationContent } from "./circulation-content";
import { CheckoutDialog } from "./checkout-dialog";

export default async function CirculationPage() {
  const t = await getTranslations("circulation");

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

      <CirculationContent />
    </div>
  );
}
