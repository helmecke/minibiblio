## Context

The author page is a server component under the dynamic `[authorName]` route. Next.js 16 supplies page parameters as a promise, and all other dynamic pages in this project await that promise; this page instead types and destructures `params` synchronously. The unresolved author becomes `undefined`, which is converted into the search text `undefined`; the catalog endpoint successfully returns an empty array and the page incorrectly renders its no-items state. See `proposal.md` for motivation and `specs/author-catalog-view/spec.md` for required behavior.

The existing catalog endpoint performs a broad case-insensitive search across catalog ID, title, author, and ISBN. The author page then applies a case-insensitive exact-author filter. A direct lookup for `Justyna Polanska` returns the expected catalog item, so neither the endpoint nor persisted author data needs to change.

## Goals / Non-Goals

**Goals:**

- Follow the asynchronous route-parameter pattern already used by the project's other dynamic pages.
- Ensure one resolved author value drives the heading, catalog request, and exact-author filtering.
- Allow genuine request failures to reach Next.js error handling instead of converting them into an empty collection.
- Keep successful empty results and exact matching behavior intact.

**Non-Goals:**

- Adding a dedicated author endpoint or changing catalog search semantics.
- Changing author URL structure, catalog table links, author normalization, or database values.
- Introducing a test framework, page-specific error boundary, translations, or loading UI.
- Refactoring shared server-side API URL construction.

## Decisions

### Await the dynamic parameters at the page boundary

The author page prop will use `Promise<{ authorName: string }>` and the async page component will await it before deriving any author value. This matches the Next.js 16 contract and the established pattern in the project's catalog, patron, and circulation dynamic pages.

Using React's `use` was rejected because the page is already an async server component. Preserving synchronous parameter access was rejected because Next.js 16 no longer supports that contract.

### Use one resolved author value throughout the request

The page will resolve and decode the route author before invoking the lookup helper, and the helper will receive that usable author value rather than an unresolved route segment. The same value will be used for display and case-insensitive exact matching after the broad API search.

Replacing the broad search with a new backend `author` parameter was rejected because the existing endpoint returns the correct data and an API change would expand the scope without addressing the route defect.

### Propagate lookup failures

The lookup helper will continue checking `res.ok`, but it will not catch every exception and return `[]`. A failed request will therefore propagate to Next.js error handling, while an actual successful empty response can still produce the no-items state required by the spec.

A page-local error presentation was considered but rejected for this focused repair because the project has no existing page error boundary or author-specific error copy. Logging and returning an empty list was rejected because it makes operational failures indistinguishable from valid domain results.

## Risks / Trade-offs

- [Framework error UI is generic] -> Preserve truthful failure semantics now; a consistent application-wide error experience can be designed separately.
- [Broad API search may return unrelated records] -> Retain the existing exact-author post-filter required by the author view.
- [Author text may contain inconsistent whitespace or punctuation] -> Preserve exact matching semantics and leave normalization or author identity modeling outside this bug fix.

## Migration Plan

No data or deployment migration is required. Deploy the page change normally and verify an existing encoded author link resolves its matching item. Rollback consists of restoring the previous page implementation; APIs and persisted data are unchanged.
