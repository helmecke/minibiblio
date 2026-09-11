## Why

The catalog currently displays items in creation-time order, which does not provide a useful chronology for imported collections whose creation timestamps are identical. Catalog users need the inventory sequence to default to newest catalog year and number while retaining an easy way to reverse that order.

## What Changes

- Make the Catalog ID table header the catalog's only sortable column.
- Display catalog items in descending catalog chronology by default.
- Let users toggle Catalog ID ordering between descending and ascending.
- Interpret two-digit years with a stable century pivot and support existing four-digit years.
- Keep malformed or unsupported Catalog IDs deterministic and separate from valid chronological IDs.
- Preserve the current behavior of the catalog API and all non-catalog-page consumers.

## Capabilities

### New Capabilities

- `catalog-sorting`: Defines chronological Catalog ID ordering and the catalog table's sorting interaction.

### Modified Capabilities

None.

## Impact

- Affects the client-side catalog table in `app/[locale]/admin/catalog/catalog-table.tsx`.
- Does not change API parameters, database schema, persisted data, dependencies, or sorting behavior in other catalog consumers.
