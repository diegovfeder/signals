"""
Database Setup Script

Initialize PostgreSQL database with schema and seed data.
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_database_url():
    """Get database URL from environment."""
    return os.getenv('DATABASE_URL', 'postgresql://signals_user:signals_password@localhost:5432/trading_signals')


def run_sql_file(cursor, file_path: Path):
    """Execute SQL commands from a file."""
    print(f"Running {file_path.name}...")
    with open(file_path, 'r') as f:
        sql = f.read()
        cursor.execute(sql)
    print(f"✓ Completed {file_path.name}")


def setup_database():
    """Set up database schema and seed data."""
    print("=" * 60)
    print("Trading Signals - Database Setup")
    print("=" * 60)

    # Connect to PostgreSQL
    db_url = get_database_url()
    print(f"\nConnecting to database...")

    try:
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("✓ Connected successfully")

        # Get project root
        project_root = Path(__file__).parent.parent
        db_dir = project_root / 'db'

        # Run schema
        print("\n1. Creating database schema...")
        schema_file = db_dir / 'schema.sql'
        if not schema_file.exists():
            # Try migration file as fallback
            schema_file = db_dir / 'migrations' / '001_initial_schema.sql'
        run_sql_file(cursor, schema_file)

        # Run seed data
        print("\n2. Seeding initial data...")
        seeds_file = db_dir / 'seeds' / 'symbols.sql'
        run_sql_file(cursor, seeds_file)

        # Verify setup
        print("\n3. Verifying setup...")
        cursor.execute("SELECT symbol, name FROM symbols;")
        symbols = cursor.fetchall()
        print(f"✓ Found {len(symbols)} symbols:")
        for symbol, name in symbols:
            print(f"  - {symbol}: {name}")

        # Close connection
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✓ Database setup complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_database()
