## Context

The catalog endpoint returns the complete filtered item collection ordered by `created_at` descending. `CatalogContent` stores that response and passes it unchanged to the client-side `CatalogTable`. The table currently renders five non-interactive data headers and has no pagination or sorting infrastructure.

Catalog IDs are configurable strings, but the existing collection overwhelmingly uses `number/YY`, with historical data also containing `number/YYYY`. Importing many records at once can assign identical creation timestamps, so creation time cannot reproduce inventory chronology. See `proposal.md` for motivation and `specs/catalog-sorting/spec.md` for required behavior.

## Goals / Non-Goals

**Goals:**

- Keep chronological ordering local to the catalog page.
- Use a deterministic comparator for existing two- and four-digit year formats.
- Preserve sort direction as search replaces the displayed item array.
- Make the Catalog ID header's state understandable visually and to assistive technology.

**Non-Goals:**

- Adding server-side sorting, pagination, or URL-persisted sort state.
- Making Title, Author, Type, Status, or Actions sortable.
- Adding or changing catalog filters.
- Supporting arbitrary configured Catalog ID formats as chronological values.

## Decisions

### Sort the complete result set in `CatalogTable`

`CatalogTable` will own a two-value direction state initialized to descending and derive a sorted copy of `items`. This preserves the API's current contract and prevents the catalog checkout selector and other endpoint consumers from inheriting a new default order. It also makes direction changes immediate because the catalog currently fetches all matching items.

Server-side query parameters were considered for future pagination, but they would add an API contract and a network request for each toggle without benefiting the current unpaginated table.

### Parse supported IDs into explicit chronological keys

A supported ID matches `number/YY` or `number/YYYY`. The comparator will parse both components numerically and normalize years as follows:

- `00` through `49` become 2000 through 2049.
- `50` through `99` become 1950 through 1999.
- Four-digit years are used directly.

Supported IDs compare by normalized year and then catalog number. Direction is applied to those chronological keys rather than to the raw string, avoiding lexical results such as `9/24` preceding `100/24` in descending order.

A current-year-relative pivot was rejected because the interpretation of persisted IDs would change as time passes. Raw natural-string comparison was rejected because it prioritizes the number before the year.

### Partition supported and unsupported IDs

Supported IDs will always appear before unsupported IDs, independent of selected direction. Direction applies within each partition: chronological comparison for supported IDs and deterministic natural-string comparison for unsupported IDs. Keeping partition placement independent of direction avoids malformed data unexpectedly becoming the most prominent entries when users reverse the sort.

### Use the existing table header as the control

The Catalog ID header will contain a button that toggles direction. The active arrow will communicate direction visually, and the header will expose the matching `aria-sort` value. Other headers remain plain text so the interface does not imply unsupported sorting.

The implementation can use the project's existing button and Lucide icon dependencies; no new translation strings or packages are required.

## Risks / Trade-offs

- [Configured IDs use another format] -> Treat them as unsupported, place them after recognized chronological IDs, and sort them deterministically rather than guessing their date semantics.
- [The collection eventually requires pagination] -> Move the same sort contract to validated API parameters before introducing pagination; client-side sorting is correct only while the full result set is loaded.
- [The fixed pivot cannot represent 2050+ with two digits] -> Keep the stable documented interpretation and use a four-digit year format before that boundary rather than changing historical ordering over time.
- [Sorting a copied array adds client work] -> The current collection size is modest and memoizing by item array and direction avoids sorting on unrelated renders.

## Migration Plan

No data or deployment migration is required. Deploy the frontend change normally. Rollback consists of restoring the static Catalog ID header and rendering the input array directly; persisted data and APIs remain untouched.
