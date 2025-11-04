# Inmobiliaria MVP

## Variables de entorno (.env)

Las siguientes variables son soportadas en `.env` en la raÃ­z del proyecto:

```
ENV=DEV
APP_TITLE=Inmobiliaria MVP
VERSION=0.1.0
DB_ENGINE=sqlite
DB_NAME=database.db
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
LOG_LEVEL=INFO
```

## EjecuciÃ³n rÃ¡pida

```
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python migrate.py         # aplica migraciones (idempotente)
python src/app.py
```

## Migraciones

- Archivos SQL: `src/migrations/` (convenciÃ³n: `000N_descripcion.sql`).
- Ejecutar: `python migrate.py` desde la raÃ­z del proyecto.
- Idempotente: las migraciones ya aplicadas no se vuelven a ejecutar.

## 🧍‍♂️ Entidad Usuario
Representa a los usuarios del sistema.
- Campos: id, username, password_hash, rol, activo, created_at.
- Validaciones automáticas en el constructor.
- Próximamente se agregará su repositorio y servicio de autenticación.
