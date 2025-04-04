# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Run Commands
- Setup: `pip install -r requirements.txt`
- Run: `python main.py`
- Lint: `flake8 .`
- Type check: `mypy .`
- Test all: `pytest`
- Test single file: `pytest path/to/test.py`
- Test specific function: `pytest path/to/test.py::test_function_name`

## Code Style Guidelines
- **Formatting**: Use Black with default settings
- **Imports**: Sort with isort, group standard lib, third-party, local
- **Types**: Use type hints for function params and return values
- **Naming**: 
  - snake_case for variables, functions, methods
  - PascalCase for classes
  - UPPER_SNAKE_CASE for constants
- **Error Handling**: Use explicit exception types, avoid bare except
- **Documentation**: Docstrings in Google style format