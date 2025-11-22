✅ README.md (listo para copiar y pegar)
# GlobalEnglish – Configuración de Entorno (Backend + Base de Datos)

Este documento explica cómo cualquier miembro del equipo puede configurar **Oracle XE en Docker**, crear el usuario del proyecto y generar automáticamente todas las tablas usando el script incluido.

> **IMPORTANTE:** Cada integrante tendrá su **propio contenedor Docker** y su **propio usuario GLOBALENGLISH**.  
> Nada se comparte entre computadoras, por eso todos deben repetir este proceso.

---

# 1️⃣ Clonar el repositorio

bash:
git clone https://github.com/Teffx410/GlobalEnglish
cd GlobalEnglish


#2️⃣ Instalar dependencias
✔ Instalar Docker Desktop

https://www.docker.com/products/docker-desktop/

✔ Instalar extensión de Oracle para Visual Studio Code

Oracle SQL Developer Extension for VSCode
(Aparece en el Marketplace)

#3️⃣ Crear la base de datos Oracle XE en Docker

Ejecutar en CMD o PowerShell:

docker run -d ^
 --name oracle-xe ^
 -e ORACLE_PASSWORD=oracle ^
 -p 1521:1521 ^
 -p 5500:5500 ^
 gvenzl/oracle-xe


⚠ Nota: La descarga de la imagen puede tardar bastante.

#4️⃣ Verificar que Oracle está listo

Ejecutar:

docker logs oracle-xe | findstr "DATABASE IS READY"


Si aparece:

DATABASE IS READY TO USE!


entonces todo está correcto.

#5️⃣ Crear conexión en VSCode (como SYSTEM)

Abrir el panel de conexiones (Oracle Developer en VSCode) y crear una conexión con:

Campo	Valor
User	SYSTEM
Password	oracle
Host	localhost
Port	1521
Service Name	XEPDB1
Connection Type	Basic

Conectarse para continuar.

#6️⃣ Crear el usuario del proyecto

Ejecutar en VSCode conectado como SYSTEM:

CREATE USER GLOBALENGLISH IDENTIFIED BY oracle;
GRANT CONNECT, RESOURCE TO GLOBALENGLISH;
ALTER USER GLOBALENGLISH QUOTA UNLIMITED ON USERS;


✔ Todos deben usar el mismo usuario y contraseña:

Usuario: GLOBALENGLISH

Contraseña: oracle

#7️⃣ Crear conexión como GLOBALENGLISH

Hacer una nueva conexión en VSCode:

Campo	Valor
User	GLOBALENGLISH
Password	oracle
Host	localhost
Port	1521
Service Name	XEPDB1

A partir de aquí, no se usa SYSTEM nunca más.

#8️⃣ Generar todas las tablas automáticamente

En el repositorio existe el archivo:

create_schema.py


Este script ejecuta automáticamente el archivo ddl.sql, que contiene todas las instrucciones de creación de tablas.

📝 Ajustar las credenciales antes de ejecutarlo

Abrir el archivo y modificar estas líneas según tu instalación local (normalmente las mismas para todos):

# Config - ajusta según tu entorno
USER = "GLOBALENGLISH"
PASSWORD = "oracle"
DSN = "localhost:1521/XEPDB1"

Si crearon su usuario como GLOBALENGLISH y con contraseña "oracle" no deben cambiar nada

▶ Ejecutar el script
python create_schema.py


Si todo va bien, aparecerán mensajes indicando que las tablas fueron creadas correctamente.

#9️⃣ ¡Listo! 🎉

Ahora ya todos tienen:

✔ Oracle XE funcionando en Docker
✔ Usuario GLOBALENGLISH creado
✔ Conexión configurada
✔ Todas las tablas creadas automáticamente
✔ Entorno backend listo para usarse
