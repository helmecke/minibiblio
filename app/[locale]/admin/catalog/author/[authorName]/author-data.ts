export interface AuthorCatalogItem {
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

export async function getItemsByAuthor(
  authorName: string,
  request: typeof fetch = fetch,
): Promise<AuthorCatalogItem[]> {
  const params = new URLSearchParams({ search: authorName });
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";
  const response = await request(
    `${baseUrl}/api/python/catalog?${params.toString()}`,
    { cache: "no-store" },
  );

  if (!response.ok) {
    throw new Error("Failed to fetch catalog items");
  }

  const allItems: AuthorCatalogItem[] = await response.json();
  return allItems.filter(
    (item) => item.author?.toLowerCase() === authorName.toLowerCase(),
  );
}
