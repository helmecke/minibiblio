import { describe, expect, it, vi } from "vitest";
import { type AuthorCatalogItem, getItemsByAuthor } from "./author-data";

function item(overrides: Partial<AuthorCatalogItem> = {}): AuthorCatalogItem {
  return {
    id: "item-id",
    catalog_id: "1/26",
    type: "book",
    title: "A Book",
    author: "Ursula K. Le Guin",
    status: "available",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

function response(items: AuthorCatalogItem[], ok = true) {
  return {
    ok,
    json: vi.fn().mockResolvedValue(items),
  } as unknown as Response;
}

describe("getItemsByAuthor", () => {
  it("URL-encodes the author name", async () => {
    const request = vi.fn().mockResolvedValue(response([]));

    await getItemsByAuthor("Octavia E. Butler", request);

    expect(request).toHaveBeenCalledWith(
      "http://localhost:3000/api/python/catalog?search=Octavia+E.+Butler",
      { cache: "no-store" },
    );
  });

  it("keeps only case-insensitive exact author matches", async () => {
    const exact = item({ author: "ursula k. le guin" });
    const titleMatch = item({ id: "title", title: "Ursula K. Le Guin", author: "Other" });
    const partial = item({ id: "partial", author: "Ursula K. Le Guin and Another" });
    const request = vi.fn().mockResolvedValue(response([exact, titleMatch, partial]));

    await expect(getItemsByAuthor("Ursula K. Le Guin", request)).resolves.toEqual([
      exact,
    ]);
  });

  it("returns an empty result distinctly from a request failure", async () => {
    const emptyRequest = vi.fn().mockResolvedValue(response([]));
    await expect(getItemsByAuthor("Nobody", emptyRequest)).resolves.toEqual([]);

    const failedRequest = vi.fn().mockResolvedValue(response([], false));
    await expect(getItemsByAuthor("Nobody", failedRequest)).rejects.toThrow(
      "Failed to fetch catalog items",
    );
  });
});
