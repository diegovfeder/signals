"""
Vercel FastAPI Entrypoint

Vercel auto-detects FastAPI apps at these locations:
- index.py (this file) ✅
- app.py
- server.py
- src/index.py, src/app.py, src/server.py

This file imports the existing FastAPI app from api/main.py
so Vercel can find and run it automatically.
"""

from api.main import app

# Vercel will auto-detect this app instance and deploy it as a Function
__all__ = ["app"]
