## Purpose

Defines repeatable automated validation for MiniBiblio changes so contributors and GitHub-hosted runners can detect frontend, backend, database, and build regressions before merge.

## ADDED Requirements

### Requirement: Repeatable frontend validation
The project SHALL provide documented package commands that run frontend linting, static type checking, automated tests, and a production build without requiring an interactive process.

#### Scenario: Contributor validates the frontend
- **WHEN** a contributor installs the locked frontend dependencies and invokes the documented validation commands
- **THEN** lint, type checking, automated tests, and the production build each terminate with a success or failure status

#### Scenario: Frontend regression violates catalog behavior
- **WHEN** catalog sorting or author-specific filtering no longer satisfies its documented behavior
- **THEN** at least one frontend automated test fails

### Requirement: Repeatable backend validation
The project SHALL provide non-interactive commands that run Python linting and automated backend tests against an explicitly designated PostgreSQL test database.

#### Scenario: Contributor validates the backend
- **WHEN** a PostgreSQL test database is available, its connection URL is supplied, and the contributor invokes the documented backend validation commands
- **THEN** database migrations, Python linting, and automated tests each terminate with a success or failure status

#### Scenario: Backend API regression occurs
- **WHEN** covered health, authentication, or catalog API behavior regresses
- **THEN** at least one backend automated test fails

### Requirement: Migrated database integration tests
Backend integration tests SHALL exercise the FastAPI application against a dedicated PostgreSQL schema created by applying the project's Alembic migration chain and SHALL isolate persisted state between tests.

#### Scenario: Integration suite starts with an empty test database
- **WHEN** the migration chain and backend integration tests run against an empty PostgreSQL test database
- **THEN** the schema is created successfully and the tests execute against that migrated schema

#### Scenario: Tests mutate persistent state
- **WHEN** one integration test creates or changes database records
- **THEN** later tests do not observe that test's persisted state unless they create equivalent fixtures themselves

#### Scenario: Non-test database is configured
- **WHEN** the integration suite is invoked without an explicitly designated test database
- **THEN** the suite refuses to perform destructive database isolation operations

### Requirement: Pull-request continuous integration
The repository SHALL automatically run independent frontend and backend validation jobs on GitHub-hosted runners for pull requests and pushes to the main branch.

#### Scenario: Pull request updates the application
- **WHEN** a pull request is opened or updated
- **THEN** GitHub Actions runs both frontend and backend validation and reports each job's result on the revision

#### Scenario: Change reaches main
- **WHEN** a revision is pushed to the main branch
- **THEN** GitHub Actions runs both frontend and backend validation for that revision

#### Scenario: One validation area fails
- **WHEN** either frontend or backend validation fails
- **THEN** the workflow reports a failed result without concealing the other job's independently reported result

### Requirement: Reproducible and least-privilege CI execution
Continuous integration SHALL install dependencies from committed lockfiles, use runtime versions aligned with the application's container configuration, avoid application secrets, and grant only repository read permission unless an additional permission is required for validation.

#### Scenario: CI installs project dependencies
- **WHEN** either validation job installs dependencies
- **THEN** it uses the corresponding committed lockfile and fails rather than silently changing the locked dependency resolution

#### Scenario: CI runs untrusted pull-request code
- **WHEN** validation runs for a pull request
- **THEN** the jobs receive no application credentials and have read-only repository contents permission

### Requirement: Release publishing remains independent
The pull-request validation workflow SHALL NOT publish container images or packages, and the existing version-tag publication workflow SHALL remain separately triggered.

#### Scenario: Pull-request validation succeeds
- **WHEN** all continuous-integration jobs pass for a pull request
- **THEN** no MiniBiblio container image is published as a consequence of that validation run
