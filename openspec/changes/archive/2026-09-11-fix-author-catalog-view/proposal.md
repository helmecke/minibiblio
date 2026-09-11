## Why

Author-specific catalog pages currently show no items even when matching catalog records exist because the route reads asynchronous Next.js parameters synchronously. This makes author links unreliable and presents the resulting invalid lookup as a legitimate empty result.

## What Changes

- Resolve dynamic author route parameters using the Next.js 16 asynchronous page contract before decoding or querying by author.
- Display catalog items whose author exactly matches the author selected from the catalog table.
- Reserve the empty-author state for successful lookups with no matching items instead of suppressing request or route failures as an empty collection.
- Keep the existing catalog API search contract, author links, catalog table behavior, and matching semantics unchanged.

## Capabilities

### New Capabilities

- `author-catalog-view`: Defines author route resolution, exact-author item display, and the distinction between empty results and lookup failures.

### Modified Capabilities

None.

## Impact

- Affects the server-rendered author page in `app/[locale]/admin/catalog/author/[authorName]/page.tsx`.
- Uses the existing `/api/python/catalog?search=...` endpoint and client-side exact-author filtering; no API, database, dependency, translation, or URL format changes are required.
- Adds focused verification for asynchronous route parameters, URL-encoded author names, successful empty results, and failed catalog requests.
