---
name: sqlite-concurrency
description: Guidelines for managing SQLite concurrency, enabling WAL mode, handling pooled connections, profiling slow queries, indexing, and batching operations.
risk: safe
source: community
date_added: "2026-06-12"
---

# SQLite Concurrency & Performance Guidelines

Use when modifying database schema, executing SQL queries, or managing SQLite connection pools.

## Use this skill when

- Encountering "database is locked" errors in concurrent environments
- Writing migrations or adding database tables
- Optimizing database queries or fixing N+1 query patterns
- Setting up SQLite connection pools and transaction boundaries

## Database Guidelines

### 1. WAL (Write-Ahead Logging) Mode
- Enable WAL mode upon establishing connection. WAL mode allows concurrent readers and non-blocking writers, drastically reducing lock contention.
- Run `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` on connection setup.

### 2. Thread Safety and Connection Pooling
- Avoid sharing single sqlite3 connection across threads. SQLite connections not thread-safe by default.
- Use pool (`SQLitePool` or thread-local storage) to acquire and release connections per thread/request.
- Explicitly close or return connections back to pool in `finally` block.

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
- Do not run queries in loop (e.g., executing select for each row in parent query).
- Use `IN` clauses with bulk parameters to fetch related records in single query.
- Wrap multiple inserts or updates inside single explicit transaction (`BEGIN TRANSACTION` / `COMMIT`) to avoid writing to disk for every row.

### 4. Indexing & Query Profiling
- Create indices on columns frequently used in `WHERE`, `JOIN`, and `ORDER BY` statements.
- Avoid indexing columns with low cardinality (e.g. booleans).
- Run `EXPLAIN QUERY PLAN` on complex queries to verify indices utilized correctly.
