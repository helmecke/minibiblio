## 1. Author Route Resolution

- [x] 1.1 Update the author page's parameter type to the Next.js 16 promise contract, await it at the page boundary, and pass one resolved author value through display and lookup; verify `npx tsc --noEmit` succeeds and the `Justyna%20Polanska` route queries for `Justyna Polanska` rather than `undefined`.
- [x] 1.2 Preserve the successful exact-author filtering while allowing non-success responses and request exceptions to propagate instead of returning an empty array; verify a successful empty lookup renders the no-items state and a failed lookup reaches error handling without rendering that state.

## 2. Integration Verification

- [x] 2.1 Exercise an encoded author link from the catalog table and verify the author page heading and item count use the decoded author and include catalog item `195/25` for `Justyna Polanska`.
- [x] 2.2 Verify case-insensitive exact-author matching excludes records returned only through title, ISBN, or catalog ID search matches, then run `npm run build` and confirm the production build succeeds.
