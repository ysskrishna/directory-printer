# Directory Printer

A GUI application for viewing and exporting directory structures. This tool provides a simple and intuitive way to visualize the structure of directories and their contents.

## Features

- Interactive GUI for directory selection
- Tree-like visualization of directory structures
- Handles permission errors gracefully
- Cross-platform compatibility (Windows, Linux, macOS)

## Installation

### Option 1: Download Binary (Recommended)

Download the latest release for your operating system from the [Releases page](https://github.com/ysskrishna/directory-printer/releases).

- Windows: Download and extract `directory-printer-windows.zip`
- Linux: Download and extract `directory-printer-linux.zip`
- macOS: Download and extract `directory-printer-macos.zip`

### Option 2: Install from Source

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

### Creating Releases

This project uses GitHub Actions to automatically build and publish binaries when a new version tag is pushed. To create a new release:

1. Update the version in `pyproject.toml`:
   ```toml
   [tool.poetry]
   version = "x.y.z"  # Update this version
   ```

2. Create and push a new tag:
   ```bash
   # Create a new tag
   git tag v0.1.0  # Replace with your version

   # Push the tag to GitHub
   git push origin v0.1.0
   ```

3. GitHub Actions will automatically:
   - Build binaries for Windows, Linux, and macOS
   - Create a new release on GitHub
   - Attach the binaries to the release

To delete a tag if needed:
```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push --delete origin v0.1.0
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

## License

Copyright (c) 2025 [Y. Siva Sai Krishna](https://github.com/ysskrishna)

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
