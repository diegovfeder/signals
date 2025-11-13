# Lab Setup Guide

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:
   - Ensure `../pipe/.env` exists with database credentials
   - See `../pipe/.env.example` for required variables

3. **Run marimo notebooks**:
   ```bash
   marimo edit notebooks/strategy_lab.py
   ```

## Important: Import Pattern

**All notebooks must import `lab_init` first** to set up the environment:

```python
import lab_init  # Must be first! Sets up sys.path and loads .env

# Now you can import from pipe and notebook_helpers
from lib.strategies import Strategy  # From pipe/lib
from notebook_helpers.strategies import get_strategy  # Lab adapters
from notebook_helpers.db import fetch_price_history  # Lab DB helpers
```

## Directory Structure

- `notebook_helpers/` - Lab-specific helper modules (adapters for pipe code)
- `notebooks/` - Marimo notebooks for interactive analysis
- `data/` - Local data cache
- `outputs/` - Generated charts and reports
- `templates/` - Notebook templates

## Required Environment Variables (in `../pipe/.env`)

```bash
# Database
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname

# Optional: API Keys
OPENAI_API_KEY=sk-...
POSTHOG_PROJECT_API_KEY=phc_...
```

## Troubleshooting

### Import Errors
- Make sure `import lab_init` is the FIRST import in your notebook
- Check that `../pipe/` exists and has a `.env` file

### Database Connection Errors
- Verify DATABASE_URL in `../pipe/.env`
- Test connection: `uv run python -c "import lab_init; from notebook_helpers.db import test_connection; test_connection()"`

### Module Not Found
- Run `uv sync` to ensure all dependencies are installed
- Check that you're running inside the lab directory
