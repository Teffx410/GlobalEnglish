# Ejecutar todo en local (resumen)

1. Levanta Oracle (Docker):
   docker start oracle-xe   # o docker run ... si no existe

2. Crear el schema (si aún no lo hiciste):
   cd globalenglish-backend
   python -m venv venv
   source venv/bin/activate
   pip install oracledb fastapi uvicorn python-dotenv pyjwt
   python scripts/create_schema.py

3. Cargar datos de prueba:
   python scripts/seed_data.py

4. Ejecutar triggers/funciones:
   -- Conéctate en VSCode con GLOBALENGLISH y corre triggers_and_functions.sql

5. Levantar backend:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

6. Abrir documentación interactiva:
   http://localhost:8000/docs
