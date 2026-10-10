# FinGuard API 🛡️💳

Motor de transacciones financieras de alta concurrencia y auditoría asíncrona construido con **Django REST Framework**, **PostgreSQL** y **Celery**.

## 🚀 Arquitectura y Patrones de Diseño
- **Aislamiento Transaccional ACID:** Prevención de *race conditions* en transferencias monetarias mediante `select_for_update()` a nivel de fila y ordenamiento de IDs para prevenir *deadlocks*.
- **Diseño en 4 Capas:** Vistas desacopladas mediante Capa de Servicios (`services.py`), Selectores de consulta anti-N+1 (`selectors.py`), Serializadores y Modelos con `CheckConstraint` físicos en PostgreSQL.
- **Seguridad Defensiva:** Autenticación JWT (`SimpleJWT`), mitigación de BOLA/IDOR con permisos por objeto (`BasePermission`) y Rate Limiting restrictivo en endpoints críticos.
- **Procesamiento Asíncrono en Background:** Tareas de auditoría y detección de operaciones de riesgo delegadas a **Celery** con **Redis** como Message Broker mediante `transaction.on_commit()`.

## 🛠️ Stack Tecnológico
- Python 3.12+
- Django 5.x & Django REST Framework
- PostgreSQL 16 (Motor de persistencia física)
- Redis 7 (Message Broker)
- Celery 5.x (Workers asíncronos)
- Docker & Docker Compose

## ⚡ Instalación y Ejecución Rápida

1. Clonar el repositorio y configurar variables de entorno:
   ```bash
   cp .env.example .env