import { getTranslations } from "next-intl/server";
import { CatalogContent } from "./catalog-content";
import { AddCatalogDialog } from "./add-catalog-dialog";

export default async function CatalogPage() {
  const t = await getTranslations("catalog");

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

      <CatalogContent />
    </div>
  );
}
