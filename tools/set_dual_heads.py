import os
import sqlite3

db = os.path.join(os.environ.get('APPDATA', ''), 'TK-OPS-ASSISTANT', 'tk_ops.db')
conn = sqlite3.connect(db)
cur = conn.cursor()

# Need both heads present so merge migration can run
# Current: c31b3b654b07 only. Insert 91c9d4b7e2aa as second row.
cur.execute('SELECT version_num FROM alembic_version')
rows = cur.fetchall()
print('Before:', rows)

# Delete all and insert both heads
cur.execute('DELETE FROM alembic_version')
cur.execute("INSERT INTO alembic_version VALUES ('c31b3b654b07')")
cur.execute("INSERT INTO alembic_version VALUES ('91c9d4b7e2aa')")
conn.commit()

cur.execute('SELECT version_num FROM alembic_version')
print('After:', cur.fetchall())
conn.close()
print('Done - both heads now in alembic_version')
