# create_schema.py
import oracledb
import os

# Config - ajusta según tu entorno
USER = "GLOBALENGLISH"
PASSWORD = "oracle"
DSN = "localhost:1521/XEPDB1"

ddl_file = "DDL_GLOBALENGLISH.sql"  # si prefieres mantener el DDL en un archivo

def run_ddl(ddl_text):
    print("Conectando a Oracle...")
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    cur = conn.cursor()
    statements = [s.strip() for s in ddl_text.split(';') if s.strip()]
    for stmt in statements:
        try:
            cur.execute(stmt)
        except Exception as e:
            print("Error ejecutando sentencia:", e)
            print(stmt[:2000])
            # Dependiendo del error, seguir o abortar
    conn.commit()
    cur.close()
    conn.close()
    print("DDL ejecutado.")

if __name__ == "__main__":
    with open(ddl_file, 'r', encoding='utf-8') as f:
        ddl = f.read()
    run_ddl(ddl)
