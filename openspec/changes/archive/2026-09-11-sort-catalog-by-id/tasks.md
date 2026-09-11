## 1. Chronological Ordering

- [x] 1.1 Add Catalog ID parsing and comparison helpers in `catalog-table.tsx` for numeric catalog numbers, two-digit years with the fixed `00-49`/`50-99` pivot, and direct four-digit years; verify the examples `155/25 > 9/24 > 503/23`, `100/24 > 10/24 > 9/24`, and `113/1958` produce their specified chronological keys and order.
- [x] 1.2 Partition supported and unsupported Catalog IDs, apply deterministic natural comparison to unsupported values, and verify unsupported IDs remain after supported IDs in both directions.
- [x] 1.3 Add descending-by-default direction state and derive a memoized sorted copy without mutating the `items` prop; verify replacing the item array after a search preserves the selected direction.

## 2. Table Interaction

- [x] 2.1 Convert only the Catalog ID header into a direction toggle using existing UI and icon dependencies; verify the default indicator is descending and repeated activation alternates ascending and descending.
- [x] 2.2 Expose the active direction through `aria-sort` while leaving Title, Author, Type, Status, and Actions non-sortable; verify keyboard operation and accessibility state in the rendered table.

## 3. Verification

- [x] 3.1 Run `npx tsc --noEmit` and `npm run build`, and resolve any type or production-build failures introduced by the catalog sorting change.
- [x] 3.2 Exercise the catalog with existing two-digit and four-digit IDs in both directions and after changing search text; verify all scenarios in `specs/catalog-sorting/spec.md` and confirm no API, filter, or other catalog-consumer behavior changed.
