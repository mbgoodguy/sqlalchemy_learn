from sqlalchemy import create_engine, text

engine = create_engine(url="sqlite:///conn_vs_begin.sqlite3", echo=True)
with engine.connect() as conn:
    # sqlalchemy.exc.ObjectNotExecutableError: Not an executable object: 'SELECT VERSION()':
    # q = conn.execute("SELECT sqlite_version();")

    q = conn.execute(text("SELECT sqlite_version();"))
    result = q.fetchone()
    print("SQLite version:", result[0])

"""
2024-03-21 18:54:36,977 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2024-03-21 18:54:36,977 INFO sqlalchemy.engine.Engine SELECT sqlite_version();
2024-03-21 18:54:36,977 INFO sqlalchemy.engine.Engine [generated in 0.00024s] ()
SQLite version: 3.37.2
2024-03-21 18:54:36,978 INFO sqlalchemy.engine.Engine ROLLBACK
"""


with engine.begin() as conn:
    q = conn.execute(text("SELECT sqlite_version();"))
    result = q.fetchone()
    print("SQLite version:", result[0])
"""
2024-03-21 18:54:36,978 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2024-03-21 18:54:36,978 INFO sqlalchemy.engine.Engine SELECT sqlite_version();
2024-03-21 18:54:36,978 INFO sqlalchemy.engine.Engine [cached since 0.0006369s ago] ()
SQLite version: 3.37.2
2024-03-21 18:54:36,978 INFO sqlalchemy.engine.Engine COMMIT
"""


# Разница в том, что при begin будет выполнен в конце COMMIT
