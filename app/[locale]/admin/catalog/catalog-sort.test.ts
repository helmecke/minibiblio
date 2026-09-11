import { describe, expect, it } from "vitest";
import { compareCatalogIds, parseCatalogChronology } from "./catalog-sort";

function sort(ids: string[], direction: "ascending" | "descending") {
  return [...ids].sort((left, right) =>
    compareCatalogIds(left, right, direction),
  );
}

describe("catalog ID chronology", () => {
  it("sorts by year before sequence number", () => {
    expect(sort(["1/24", "99/23", "2/24"], "ascending")).toEqual([
      "99/23",
      "1/24",
      "2/24",
    ]);
  });

  it("sorts same-year sequence numbers numerically", () => {
    expect(sort(["10/24", "2/24", "1/24"], "ascending")).toEqual([
      "1/24",
      "2/24",
      "10/24",
    ]);
  });

  it("uses 50 as the two-digit century pivot", () => {
    expect(parseCatalogChronology("1/49")).toEqual({ number: 1, year: 2049 });
    expect(parseCatalogChronology("1/50")).toEqual({ number: 1, year: 1950 });
  });

  it("accepts four-digit years", () => {
    expect(parseCatalogChronology("12/2024")).toEqual({
      number: 12,
      year: 2024,
    });
  });

  it("reverses chronological order for descending sorts", () => {
    const ids = ["1/23", "2/24", "1/24"];
    expect(sort(ids, "descending")).toEqual(["2/24", "1/24", "1/23"]);
  });

  it("places unsupported IDs after chronological IDs deterministically", () => {
    const ids = ["legacy-10", "2/24", "legacy-2", "1/24"];
    expect(sort(ids, "ascending")).toEqual([
      "1/24",
      "2/24",
      "legacy-2",
      "legacy-10",
    ]);
    expect(sort(ids, "descending")).toEqual([
      "2/24",
      "1/24",
      "legacy-10",
      "legacy-2",
    ]);
  });
});
