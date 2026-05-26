# codeowners-cli

Python codeowners parser with a CLI — look up file owners from your `CODEOWNERS` file.

## Install

```bash
# Run once with uvx
uvx codeowners-cli <filenames>

# Or install persistently
uv tool install codeowners-cli
```

## CLI Usage

```bash
# Auto-detects CODEOWNERS in the current git repo
codeowners-cli src/foo.py tests/bar.py

# Explicit path
codeowners-cli --codeowners .github/CODEOWNERS src/foo.py

# Only show files that have owners
codeowners-cli --only-owners src/foo.py src/bar.py

# Structured output
codeowners-cli --output json src/foo.py
codeowners-cli --output csv  src/foo.py
codeowners-cli --output tsv  src/foo.py
```

Default text output:

```
filename        owners
src/foo.py      @alice @team/backend
src/bar.py      user@example.com
```

## Library Usage

```python
from codeowners import CodeOwners

owners = CodeOwners(open("CODEOWNERS").read())
print(owners.of("src/foo.py"))
# [('USERNAME', '@alice'), ('TEAM', '@team/backend')]
```

## Development

```bash
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run ty check
```
