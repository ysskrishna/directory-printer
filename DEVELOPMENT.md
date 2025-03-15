# Development Guide

## Installation from Source

This project uses Poetry for dependency management. To install from source:

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

## Usage for Developers

To run the application:

```bash
poetry run directory-printer
```

Or activate the virtual environment and run directly:

```bash
poetry shell
directory-printer
```

## Development Practices

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

### Adding a New Package

To add a new package to the project using Poetry:

1. Add the package:
   ```bash
   poetry add package_name
   ```
   This will add the package to the `pyproject.toml` file and install it in the virtual environment.

2. If the package is only needed for development (e.g., testing, linting), add it as a development dependency:
   ```bash
   poetry add --dev package_name
   ```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks run:
- black (code formatting)
- isort (import sorting)

#### Setup

1. Install dev dependencies:
```bash
poetry install
```

2. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

#### Usage

The hooks will run automatically on every commit. There are two ways to bypass the hooks if needed:

1. Skip all hooks:
```bash
git commit -m "your message" --no-verify
```

2. Skip specific hooks:
```bash
SKIP=black,isort git commit -m "your message"
```

You can also run the hooks manually on all files:
```bash
poetry run pre-commit run --all-files
``` 