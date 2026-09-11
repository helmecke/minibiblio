## Purpose

Defines how the catalog presents and interactively orders items by the chronology encoded in their Catalog IDs.

## ADDED Requirements

### Requirement: Default chronological Catalog ID order
The system SHALL initially display catalog items in descending Catalog ID chronology, comparing the interpreted catalog year first and the numeric catalog number second.

#### Scenario: Items span multiple years
- **WHEN** the catalog contains items `155/25`, `9/24`, and `503/23`
- **THEN** the system displays them in the order `155/25`, `9/24`, `503/23`

#### Scenario: Items share a year
- **WHEN** the catalog contains items `9/24`, `10/24`, and `100/24`
- **THEN** the system displays them in the order `100/24`, `10/24`, `9/24`

### Requirement: Catalog year interpretation
The system SHALL interpret two-digit Catalog ID years from `00` through `49` as 2000 through 2049, interpret years from `50` through `99` as 1950 through 1999, and use four-digit years directly.

#### Scenario: Two-digit years cross the century pivot
- **WHEN** the catalog contains `1/49` and `1/50`
- **THEN** the system treats their years as 2049 and 1950 respectively

#### Scenario: Four-digit historical year
- **WHEN** the catalog contains `113/1958`
- **THEN** the system treats its year as 1958

### Requirement: Catalog ID sort direction control
The system SHALL provide a sort control on the Catalog ID table header that toggles between descending and ascending chronological order and indicates the active direction accessibly and visually.

#### Scenario: User reverses the default order
- **WHEN** the catalog is in its default descending order and the user activates the Catalog ID sort control
- **THEN** the system displays items in ascending year and number order and indicates ascending order

#### Scenario: User restores descending order
- **WHEN** the catalog is in ascending order and the user activates the Catalog ID sort control
- **THEN** the system displays items in descending year and number order and indicates descending order

### Requirement: Sorting scope
The system SHALL expose sorting only for the Catalog ID column and SHALL preserve the selected direction while the displayed result set changes during the current catalog-page session.

#### Scenario: Search results change
- **WHEN** a user selects ascending Catalog ID order and then changes the catalog search
- **THEN** the resulting items remain ordered by Catalog ID ascending

#### Scenario: Other columns are displayed
- **WHEN** the catalog table is displayed
- **THEN** Title, Author, Type, Status, and Actions do not expose sort controls

### Requirement: Unsupported Catalog ID handling
The system SHALL place Catalog IDs that do not match `number/YY` or `number/YYYY` after supported IDs in either direction and SHALL order unsupported IDs deterministically.

#### Scenario: Result set contains an unsupported ID
- **WHEN** supported and unsupported Catalog IDs appear in the same result set
- **THEN** supported IDs follow the selected chronological order and unsupported IDs appear afterward in deterministic order
