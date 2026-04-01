import os
import sqlite3

db = os.path.join(os.environ.get('APPDATA', ''), 'TK-OPS-ASSISTANT', 'tk_ops.db')
print(f'DB path: {db}')
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("UPDATE alembic_version SET version_num='8a7d9fd32c11'")
conn.commit()
cur.execute('SELECT * FROM alembic_version')
print('After fix:', cur.fetchall())
conn.close()
print('Done')
