import { getTranslations } from "next-intl/server";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CatalogTable } from "../../catalog-table";
import { getItemsByAuthor } from "./author-data";

interface AuthorPageProps {
  params: Promise<{
    authorName: string;
  }>;
}

export default async function AuthorPage({ params }: AuthorPageProps) {
  const { authorName } = await params;
  const decodedAuthor = decodeURIComponent(authorName);
  const t = await getTranslations("catalog");

  const items = await getItemsByAuthor(decodedAuthor);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/admin/catalog">
            <ChevronLeft className="h-4 w-4" />
            <span className="sr-only">Back to catalog</span>
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">
            {t("itemsByAuthor", { author: decodedAuthor })}
          </h1>
          <p className="text-muted-foreground">
            {items.length === 0
              ? t("noItemsByAuthor")
              : t("itemCountByAuthor", { count: items.length })}
          </p>
        </div>
      </div>

      <CatalogTable items={items} />
    </div>
  );
}
