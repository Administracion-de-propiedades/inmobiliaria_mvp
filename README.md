# Inmobiliaria MVP

## Variables de entorno (.env)

Las siguientes variables son soportadas en `.env` en la raíz del proyecto:

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

## Ejecución rápida

```
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python migrate.py         # aplica migraciones (idempotente)
python src/app.py
```

## Migraciones

- Archivos SQL: `src/migrations/` (convención: `000N_descripcion.sql`).
- Ejecutar: `python migrate.py` desde la raíz del proyecto.
- Idempotente: las migraciones ya aplicadas no se vuelven a ejecutar.
