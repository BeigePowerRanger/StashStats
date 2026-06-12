from stashies.db import DBManager

pool = DBManager.get_pool()
conn = pool.getconn()
cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_original_stash_id ON original_values(stash_id);")
conn.commit()
cur.close()
pool.putconn(conn)
print("Created index!")
