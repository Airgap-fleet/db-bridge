#!/usr/bin/env python3
import os
from asyncpg import create_pool

print("=== Checking database connection ===")

# Try to connect with the correct password
password = "postgres"
dsn = f"postgresql://postgres:{password}@localhost:5432/postgres"

print(f"Trying to connect with DSN: {dsn}")

try:
    pool = create_pool(dsn)
    print("✓ Pool created successfully")
    
    # Test query
    async def test_query():
        async with pool.acquire() as conn:
            # Test if we can query
            result = await conn.fetch("SELECT 1 as test")
            print(f"✓ Query returned: {result}")
            
            # Check test_users table
            result = await conn.fetch("SELECT COUNT(*) as count FROM test_users")
            print(f"✓ test_users count: {result[0]['count']}")
            
            # Check test_orders table  
            result = await conn.fetch("SELECT COUNT(*) as count FROM test_orders")
            print(f"✓ test_orders count: {result[0]['count']}")
            
            # Try to create tables if they don't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS test_users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS test_orders (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES test_users(id),
                    product TEXT NOT NULL,
                    amount DECIMAL(10,2),
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # Insert test data
            await conn.execute("TRUNCATE test_orders, test_users RESTART IDENTITY CASCADE")
            
            await conn.execute("""
                INSERT INTO test_users (name, email, age) VALUES
                    ('Alice', 'alice@example.com', 30),
                    ('Bob', 'bob@example.com', 25),
                    ('Charlie', 'charlie@example.com', 35)
            """)
            
            await conn.execute("""
                INSERT INTO test_orders (user_id, product, amount, status) VALUES
                    (1, 'Laptop', 999.99, 'completed'),
                    (1, 'Mouse', 29.99, 'completed'),
                    (2, 'Keyboard', 79.99, 'pending')
            """)
            
            print("✓ Test tables created and populated")
            
    import asyncio
    asyncio.run(test_query())
    
    # Close pool
    pool.close()
    await pool.wait_closed()
    print("✓ Pool closed")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

