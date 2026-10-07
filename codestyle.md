# Code Style

## Python

This project follows the basic principles of PEP 8.

### Naming

- Variables and functions use `snake_case`.
- Classes use `PascalCase`.
- Constants use uppercase names where appropriate.

### Formatting

- Use 4 spaces for indentation.
- Keep functions focused on a single responsibility.
- Add blank lines between major logical sections.
- Avoid unnecessary deeply nested logic.

### Security

- Do not use `eval()` or `exec()` to evaluate user expressions.
- Validate all user input before calculation.
- Use parameterized SQL statements to prevent SQL injection.

### API Design

- Use RESTful HTTP methods.
- Return meaningful HTTP status codes.
- Return clear error messages for invalid input.