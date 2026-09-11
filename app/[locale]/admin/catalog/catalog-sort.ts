export type CatalogSortDirection = "ascending" | "descending";

interface CatalogChronology {
  number: number;
  year: number;
}

const naturalCatalogIdCollator = new Intl.Collator("en", {
  numeric: true,
  sensitivity: "base",
});

export function parseCatalogChronology(
  catalogId: string,
): CatalogChronology | null {
  const match = /^(\d+)\/(\d{2}|\d{4})$/.exec(catalogId);
  if (!match) {
    return null;
  }

  const number = Number(match[1]);
  const rawYear = Number(match[2]);
  const year =
    match[2].length === 2
      ? rawYear < 50
        ? 2000 + rawYear
        : 1900 + rawYear
      : rawYear;

  return { number, year };
}

function compareNaturally(left: string, right: string) {
  const naturalOrder = naturalCatalogIdCollator.compare(left, right);
  if (naturalOrder !== 0) {
    return naturalOrder;
  }

  return left < right ? -1 : left > right ? 1 : 0;
}

export function compareCatalogIds(
  left: string,
  right: string,
  direction: CatalogSortDirection,
) {
  const leftChronology = parseCatalogChronology(left);
  const rightChronology = parseCatalogChronology(right);

  if (leftChronology && !rightChronology) {
    return -1;
  }
  if (!leftChronology && rightChronology) {
    return 1;
  }

  const directionMultiplier = direction === "ascending" ? 1 : -1;
  if (!leftChronology || !rightChronology) {
    return compareNaturally(left, right) * directionMultiplier;
  }

  const chronologicalOrder =
    leftChronology.year - rightChronology.year ||
    leftChronology.number - rightChronology.number ||
    compareNaturally(left, right);

  return chronologicalOrder * directionMultiplier;
}
