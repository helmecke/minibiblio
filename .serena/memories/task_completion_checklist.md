# Task Completion Checklist

When completing a task, ensure the following steps are performed:

## Code Quality
- [ ] Run linting: `npm run lint`
- [ ] Fix any ESLint errors or warnings
- [ ] Ensure TypeScript strict mode compliance (no type errors)

## Testing
- [ ] Manual testing in development: `npm run dev`
- [ ] Verify both Next.js and FastAPI endpoints work correctly
- [ ] Test in browser at http://localhost:3000

## Build Verification
- [ ] Ensure production build succeeds: `npm run build`

## Python Changes
- [ ] If Python dependencies were added, update `requirements.txt`
- [ ] Verify FastAPI endpoints work via `/api/py/docs`

## Before Committing
- [ ] Review changed files
- [ ] Ensure no sensitive data is committed
- [ ] Write clear commit message
