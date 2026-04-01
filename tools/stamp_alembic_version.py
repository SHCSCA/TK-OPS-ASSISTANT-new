import os
import sqlite3

db = os.path.join(os.environ.get('APPDATA', ''), 'TK-OPS-ASSISTANT', 'tk_ops.db')
print(f'DB path: {db}')
conn = sqlite3.connect(db)
cur = conn.cursor()

# Check current tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print('Tables:', [r[0] for r in cur.fetchall()])

# Check alembic_version
cur.execute('SELECT * FROM alembic_version')
print('alembic_version before:', cur.fetchall())

# Stamp as c31b3b654b07 since tables already exist
cur.execute("UPDATE alembic_version SET version_num='c31b3b654b07'")
conn.commit()
cur.execute('SELECT * FROM alembic_version')
print('alembic_version after:', cur.fetchall())
conn.close()
print('Done')
