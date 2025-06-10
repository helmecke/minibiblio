# MiniBiblio

A comprehensive library management system for small libraries, built with Python and Tkinter.

## Features

- **Book Management**: Add, edit, delete, and search books
- **Reader Management**: Manage library members and their information
- **Loan Operations**: Check out and return books, extend loan periods
- **Audit Logging**: Complete audit trail of all library operations
- **Search Interface**: Advanced search across books, readers, and loans
- **Statistics**: Loan statistics and reader activity reports

## Requirements

- Python 3.8 or higher
- Standard library modules only (no external dependencies for core functionality)

## Installation

### Using uv (Recommended)

1. Install [uv](https://docs.astral.sh/uv/) if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/helmecke/minibiblio.git
   cd minibiblio
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   uv sync
   ```

4. Run the application:
   ```bash
   uv run python src/main.py
   ```

### Alternative Installation Methods

#### Using pip and venv

1. Clone the repository:
   ```bash
   git clone https://github.com/helmecke/minibiblio.git
   cd minibiblio
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies (optional):
   ```bash
   pip install -e ".[dev]"
   ```

4. Run the application:
   ```bash
   python src/main.py
   ```

## Development

### Setting up Development Environment

Using uv:
```bash
# Install all development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run linting
uv run ruff check src tests

# Format code
uv run black src tests
```

### Testing

The project includes comprehensive tests with over 95% coverage:

```bash
# Run all tests
uv run pytest

# Run specific test files
uv run pytest tests/test_book_service.py

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html
```

### Building for Distribution

#### Creating Executable (Windows)

```bash
# Install build dependencies
uv sync --extra build

# Build executable
uv run python setup.py build
```

#### Creating Python Package

```bash
# Build wheel and source distribution
uv build

# Install locally
uv pip install dist/minibiblio-1.0.0-py3-none-any.whl
```

## Usage

1. **First Run**: The application will create a SQLite database (`library.db`) in the project directory
2. **Main Interface**: Navigate through different sections using the menu bar
3. **Adding Books**: Use the Book Management section to add new books to the library
4. **Managing Readers**: Register new library members in the Reader Management section
5. **Loan Operations**: Check out and return books through the Lending Operations section
6. **Search**: Use the Search Interface to find books, readers, or loans
7. **Audit Trail**: View all library activities in the Audit Log Viewer

## Project Structure

```
minibiblio/
├── src/
│   ├── business/          # Business logic services
│   │   ├── audit_service.py
│   │   ├── book_service.py
│   │   ├── loan_service.py
│   │   └── reader_service.py
│   ├── database/          # Database layer
│   │   ├── db_manager.py
│   │   ├── models.py
│   │   └── schema.sql
│   ├── ui/               # User interface components
│   │   ├── main_window.py
│   │   ├── book_management.py
│   │   ├── reader_management.py
│   │   ├── lending_operations.py
│   │   ├── search_interface.py
│   │   └── audit_log_viewer.py
│   └── main.py           # Application entry point
├── tests/                # Comprehensive test suite
├── pyproject.toml        # Project configuration
├── setup.py             # cx_Freeze build script
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`uv run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.