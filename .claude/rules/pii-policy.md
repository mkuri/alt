# PII Policy (Public Repository)

This is a public repository. Never hardcode personal information.

## Blocked Content

The following must never appear in committed code or docs:

- Personal GitHub usernames — use `<owner>` as placeholder in docs, generic strings in code
- Private project or service names that are not public OSS
- Brand names of personal health products (supplements, medications, etc.)
- Personal body measurements (height, weight, body composition) — use environment variables or config files (gitignored)
- Personal schedules, pet information, home device details
- Discord channel IDs or other service-specific numeric IDs

## How to Handle

- **Docs and examples**: use generic placeholders (`<owner>`, `example.com`, `my-app`)
- **Tests**: use generic values (e.g., height=1.75, weight=70.0)
- **Runtime config**: read personal values from environment variables or `alt.toml` (gitignored), never hardcode
- **Pre-commit hook**: `.githooks/pre-commit` checks staged changes against patterns in `.githooks/pii-patterns` (gitignored). Copy `.githooks/pii-patterns.example` and add your own patterns.
