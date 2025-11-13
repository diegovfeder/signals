"""Initialize lab environment by adding pipe to sys.path."""

import sys
from pathlib import Path

# Add pipe directory to Python path
PIPE_DIR = Path(__file__).parent.parent / "pipe"
if PIPE_DIR.exists() and str(PIPE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPE_DIR))
    print(f"[lab_init] Added {PIPE_DIR} to sys.path")

# Load environment variables - check lab/.env first, then pipe/.env
from dotenv import load_dotenv

LAB_ENV = Path(__file__).parent / ".env"
PIPE_ENV = PIPE_DIR / ".env"

if LAB_ENV.exists():
    load_dotenv(LAB_ENV)
    print(f"[lab_init] Loaded environment from {LAB_ENV}")
elif PIPE_ENV.exists():
    load_dotenv(PIPE_ENV)
    print(f"[lab_init] Loaded environment from {PIPE_ENV} (fallback)")
else:
    print(f"[lab_init] WARNING: No .env file found.")
    print(f"[lab_init] Copy lab/.env.example to lab/.env and configure it.")
