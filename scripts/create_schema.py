# scripts/create_schema.py
import oracledb
import os

USER = os.getenv("DB_USER", "GLOBALENGLISH")
PASSWORD = os.getenv("DB_PASS", "oracle")
DSN = os.getenv("DB_DSN", "localhost:1522/XEPDB1")

DDL_FILE = os.path.join(os.path.dirname(__file__), "..", "ddl.sql")

def run_ddl():
    print("Conectando a Oracle como", USER)
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    cur = conn.cursor()
    with open(DDL_FILE, 'r', encoding='utf-8') as f:
        ddl = f.read()
    # split statements by semicolon that are at line end; Oracle accepts single statements so we do best-effort split
    stmts = [s.strip() for s in ddl.split(';') if s.strip()]
    for s in stmts:
        try:
            cur.execute(s)
        except Exception as e:
            print("ERROR executing statement:", e)
            print("STATEMENT (truncated):", s[:200])
    conn.commit()
    cur.close()
    conn.close()
    print("DDL executed.")

if __name__ == "__main__":
    run_ddl()

