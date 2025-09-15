#!/usr/bin/env python3
"""
Database Schema Setup Script
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv


async def setup_database_schema():
    """Setup database schema by running the SQL file."""
    try:
        # Load environment variables
        load_dotenv("env.local")
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False

        print("🔗 Connecting to database...")
        # Disable statement cache for pgBouncer compatibility
        conn = await asyncpg.connect(database_url, statement_cache_size=0)

        # Read SQL file
        sql_file_path = "database/sql/create_subscription_tables.sql"
        print(f"📄 Reading SQL schema from: {sql_file_path}")

        with open(sql_file_path, "r") as f:
            sql_content = f.read()

        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

        # Execute each statement separately
        print("🚀 Executing database schema...")
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    await conn.execute(statement)
                    print(f"✅ Statement {i}/{len(statements)} executed successfully")
                except Exception as e:
                    print(f"⚠️ Statement {i} failed (might already exist): {e}")

        print("✅ Database schema setup completed!")

        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'subscriptions', 'webhook_events', 'plan_mappings')
            ORDER BY table_name;
        """)

        print(f"📊 Available tables: {[row['table_name'] for row in tables]}")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Database schema setup failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(setup_database_schema())
    exit(0 if success else 1)
