import { getTranslations } from "next-intl/server";
import { PatronsContent } from "./patrons-content";
import { AddPatronDialog } from "./add-patron-dialog";

export default async function PatronsPage() {
  const t = await getTranslations("patrons");

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

      <PatronsContent />
    </div>
  );
}
