from stashies.db import DBManager

pool = DBManager.get_pool()
conn = pool.getconn()
cur = conn.cursor()

cur.execute("PRAGMA index_list('original_values');")
indices = cur.fetchall()
index_names = [i[1] for i in indices]

if "idx_original_stash_id" in index_names or "sqlite_autoindex_original_values_1" in index_names:
    print("Index on original_values is present:", index_names)
else:
    print("Index missing!", index_names)

cur.close()
pool.putconn(conn)
