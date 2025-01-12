# Directory Printer

A GUI application for viewing and exporting directory structures. This tool provides a simple and intuitive way to visualize the structure of directories and their contents.

## Features

- Interactive GUI for directory selection
- Tree-like visualization of directory structures
- Handles permission errors gracefully
- Cross-platform compatibility

## Installation

This project uses Poetry for dependency management. To install:

1. Make sure you have Poetry installed:
   ```bash
   pip install poetry
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/directory-printer.git
   cd directory-printer
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

## Usage

To run the application:

```bash
poetry run directory-printer
```

Or activate the virtual environment and run directly:

```bash
poetry shell
directory-printer
```

## Development

This project follows these development practices:
- Code formatting with Black
- Import sorting with isort
- Linting with Pylint

To run the development tools:

```bash
# Format code
poetry run black .
poetry run isort .

# Run linting
poetry run pylint directory_printer
```

## License

Copyright (c) 2025 [Y. Siva Sai Krishna](https://github.com/ysskrishna)

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
