---
name: sqlite-concurrency
description: Guidelines for managing SQLite concurrency, enabling WAL mode, handling pooled connections, profiling slow queries, indexing, and batching operations.
risk: safe
source: community
date_added: "2026-06-12"
---

# SQLite Concurrency & Performance Guidelines

Use this skill when modifying database schema, executing SQL queries, or managing SQLite connection pools.

## Use this skill when

- Encountering "database is locked" errors in concurrent environments
- Writing migrations or adding new database tables
- Optimizing database queries or fixing N+1 query patterns
- Setting up SQLite connection pools and transaction boundaries

## Database Guidelines

### 1. WAL (Write-Ahead Logging) Mode
- Always enable WAL mode upon establishing a connection. WAL mode allows concurrent readers and non-blocking writers, drastically reducing lock contention.
- Run `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` on connection setup.

### 2. Thread Safety and Connection Pooling
- Avoid sharing a single sqlite3 connection across threads. SQLite connections are not thread-safe by default.
- Use a pool (like `SQLitePool` or thread-local storage) to acquire and release connections per thread/request.
- Explicitly close or return connections back to the pool in a `finally` block.

Example:
```python
conn = DBManager.get_pool().getconn()
try:
    cur = conn.cursor()
    # execute queries...
finally:
    DBManager.get_pool().putconn(conn)
```

### 3. Batching & N+1 Prevention
- Do not run queries in a loop (e.g., executing a select for each row in a parent query).
- Use `IN` clauses with bulk parameters to fetch related records in a single query.
- Wrap multiple inserts or updates inside a single explicit transaction (`BEGIN TRANSACTION` / `COMMIT`) to avoid writing to disk for every row.

### 4. Indexing & Query Profiling
- Always create indices on columns frequently used in `WHERE`, `JOIN`, and `ORDER BY` statements.
- Avoid indexing columns with low cardinality (e.g. booleans).
- Run `EXPLAIN QUERY PLAN` on complex queries to verify that indices are being utilized correctly.
