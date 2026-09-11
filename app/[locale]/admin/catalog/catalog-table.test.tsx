import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CatalogTable } from "./catalog-table";

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
}));

vi.mock("@/i18n/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

function item(id: string, catalogId: string) {
  return {
    id,
    catalog_id: catalogId,
    type: "book" as const,
    title: `Title ${catalogId}`,
    author: "Author",
    status: "available" as const,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  };
}

function renderedCatalogIds() {
  return screen
    .getAllByRole("row")
    .slice(1)
    .map((row) => within(row).getAllByRole("cell")[0].textContent);
}

describe("CatalogTable sorting", () => {
  const items = [item("a", "1/24"), item("b", "2/25"), item("c", "3/24")];

  it("renders newest IDs first with accessible descending state", () => {
    render(<CatalogTable items={items} />);

    expect(renderedCatalogIds()).toEqual(["2/25", "3/24", "1/24"]);
    expect(screen.getByRole("columnheader", { name: "catalogId" })).toHaveAttribute(
      "aria-sort",
      "descending",
    );
  });

  it("toggles between ascending and descending order", async () => {
    const user = userEvent.setup();
    render(<CatalogTable items={items} />);

    await user.click(screen.getByRole("button", { name: "catalogId" }));
    expect(renderedCatalogIds()).toEqual(["1/24", "3/24", "2/25"]);
    expect(screen.getByRole("columnheader", { name: "catalogId" })).toHaveAttribute(
      "aria-sort",
      "ascending",
    );

    await user.click(screen.getByRole("button", { name: "catalogId" }));
    expect(renderedCatalogIds()).toEqual(["2/25", "3/24", "1/24"]);
  });

  it("preserves direction when items change", async () => {
    const user = userEvent.setup();
    const { rerender } = render(<CatalogTable items={items} />);
    await user.click(screen.getByRole("button", { name: "catalogId" }));

    rerender(<CatalogTable items={[...items, item("d", "4/23")]} />);

    expect(renderedCatalogIds()).toEqual(["4/23", "1/24", "3/24", "2/25"]);
    expect(screen.getByRole("columnheader", { name: "catalogId" })).toHaveAttribute(
      "aria-sort",
      "ascending",
    );
  });
});
