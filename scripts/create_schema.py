import oracledb
import os

USER = os.getenv("DB_USER", "GLOBALENGLISH")
PASSWORD = os.getenv("DB_PASS", "oracle")
DSN = os.getenv("DB_DSN", "localhost:1521/XEPDB1")

DDL_FILE = os.path.join(os.path.dirname(__file__), "..", "ddl.sql")

def run_ddl():
    print("Conectando a Oracle como", USER)
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    cur = conn.cursor()
    with open(DDL_FILE, 'r', encoding='utf-8') as f:
        ddl = f.read()
    # Separar instrucciones por punto y coma al final de línea.
    stmts = [s.strip() for s in ddl.split(';') if s.strip()]
    for s in stmts:
        try:
            print("Ejecutando...")
            cur.execute(s)
        except Exception as e:
            print("ERROR ejecutando statement:", e)
            print("STATEMENT (truncado):", s[:200])
    conn.commit()
    cur.close()
    conn.close()
    print("DDL ejecutado.")

if __name__ == "__main__":
    run_ddl()
