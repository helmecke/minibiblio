import { getTranslations } from "next-intl/server";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CatalogTable } from "../../catalog-table";

interface CatalogItem {
  id: string;
  catalog_id: string;
  type: "book" | "dvd" | "cd" | "magazine" | "other";
  title: string;
  author?: string;
  isbn?: string;
  status: "available" | "borrowed" | "reserved" | "damaged" | "lost";
  created_at: string;
  updated_at: string;
}

interface AuthorPageProps {
  params: {
    authorName: string;
    locale: string;
  };
}

async function getItemsByAuthor(authorName: string): Promise<CatalogItem[]> {
  try {
    const decodedAuthor = decodeURIComponent(authorName);
    const params = new URLSearchParams();
    params.append("search", decodedAuthor);

    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";
    const res = await fetch(
      `${baseUrl}/api/python/catalog?${params.toString()}`,
      { cache: "no-store" }
    );

    if (!res.ok) {
      throw new Error("Failed to fetch catalog items");
    }

    const allItems: CatalogItem[] = await res.json();

    // Filter to only items that actually match the author
    // (since search is broader and searches title, ISBN, etc.)
    const filteredItems = allItems.filter(
      (item) => item.author?.toLowerCase() === decodedAuthor.toLowerCase()
    );

    return filteredItems;
  } catch (error) {
    console.error("Error fetching items by author:", error);
    return [];
  }
}

export default async function AuthorPage({ params }: AuthorPageProps) {
  const { authorName } = params;
  const decodedAuthor = decodeURIComponent(authorName);
  const t = await getTranslations("catalog");

  const items = await getItemsByAuthor(authorName);

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
