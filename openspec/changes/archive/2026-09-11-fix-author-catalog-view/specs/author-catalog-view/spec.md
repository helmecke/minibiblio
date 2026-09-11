## Purpose

Defines how an author-specific catalog route resolves the selected author and presents matching catalog items or lookup failures.

## ADDED Requirements

### Requirement: Author route resolves the selected author
The system SHALL resolve the author represented by an author-specific catalog URL before using that value to retrieve catalog items.

#### Scenario: URL contains an encoded author name
- **WHEN** a user opens an author-specific catalog URL containing an encoded author name such as `Justyna%20Polanska`
- **THEN** the system resolves the selected author as `Justyna Polanska` and performs the catalog lookup for that author

### Requirement: Author view displays exact author matches
The system SHALL display every catalog item returned by the catalog lookup whose author matches the selected author case-insensitively, and SHALL exclude broader search results that match only another searchable field.

#### Scenario: Catalog contains an item by the selected author
- **WHEN** the selected author is `Justyna Polanska` and a catalog item has `Justyna Polanska` as its author
- **THEN** the author view includes that catalog item

#### Scenario: Search returns a non-author match
- **WHEN** the catalog lookup returns an item because another searchable field matches the selected author text but the item's author does not
- **THEN** the author view excludes that item

### Requirement: Empty results are distinguished from lookup failures
The system SHALL present the no-items state only after a successful catalog lookup yields no exact author matches, and SHALL surface a catalog lookup failure as an error instead of presenting it as an empty author collection.

#### Scenario: Successful lookup has no exact matches
- **WHEN** the catalog lookup succeeds and no returned item has an author matching the selected author
- **THEN** the author view presents the no-items state

#### Scenario: Catalog lookup fails
- **WHEN** the author view cannot complete the catalog lookup successfully
- **THEN** the system reports an error and does not claim that the author has no catalog items
