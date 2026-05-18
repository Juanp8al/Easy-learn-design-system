# EasyLearn — LMS universitario

Plataforma Django que conecta **configuración institucional → aula docente → cursado estudiante**, con apuntes personales separados en **Repaso**.

> **Resumen:** Conectar el flujo semana → actividad → entrega → nota en el aula, dejar los apuntes en Repaso (`notes`), y usar el mismo shell visual en los tres roles — eso eleva el proyecto de demo a LMS profesional.

Repositorio: [Easy-learn-design-system](https://github.com/Juanp8al/Easy-learn-design-system).

## Requisitos

- Python 3.10+
- pip

## Cómo correr el proyecto

```bash
cd "Easy learn design system"
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # datos de prueba (opcional)
python manage.py runserver
```

Abrir: http://127.0.0.1:8000/

En desarrollo, los archivos subidos se sirven desde `media/` (entregas y materiales).

## Roles de prueba (`seed_demo`)

Contraseña para todos: **`demo1234`**

| Usuario | Rol | Panel |
|---------|-----|--------|
| `estudiante1` | Estudiante | `/dashboard` |
| `estudiante2` | Estudiante | `/dashboard` |
| `prof.demo` | Docente | `/accounts/panel/docente/` |
| `admin.demo` | Administrador | `/accounts/panel/administrador/` |

Comandos útiles:

```bash
python manage.py seed_demo              # período, 2 cursos, matrículas, 1 semana con actividad
python manage.py seed_classroom --weeks 1 --force
python manage.py check
python manage.py test classroom accounts
```

## Estructura de apps

| App | Responsabilidad |
|-----|-----------------|
| **academia** | Carreras, períodos, cursos ofertados, matrículas |
| **classroom** | Aula: semanas, materiales, actividades, entregas, notas, avisos |
| **accounts** | Login, roles, perfil, notificaciones del portal |
| **notes** | Apuntes personales (solo **Repaso**, no menú principal de cursos) |
| **revision** | Objetivos y calendario de repaso personal |
| **glossary** | Glosario ligado a apuntes |

## URLs principales

| Rol | Rutas |
|-----|--------|
| Estudiante | `/dashboard` (inicio, calificaciones, calendario, mensajes) · `/aula/` (cursos matriculados) · **Repaso** → `/revision/` |
| Docente | `/accounts/panel/docente/` |
| Administrador | `/accounts/panel/administrador/` |
| Design system (solo `DEBUG`) | `/design-system/` |

El menú **Aula virtual** lleva a `/aula/` (cursos institucionales). Los apuntes de `notes.Course` no aparecen como “curso universitario” en el menú principal.

## Git y archivos locales

- Inicialice el repositorio **solo** en la carpeta del proyecto (`Easy learn design system`), no en `C:\Users\Familia`.
- No versionar: `.env`, `db.sqlite3`, `staticfiles/`, `media/`, `.venv/` (ya listados en `.gitignore`).

## Design system

Tokens (Informe 2): azul `#1E3A8A`, verde `#10B981`, naranja `#F59E0B`, neutros `#F8FAFC` / `#E2E8F0` / `#64748B` / `#0F172A`.

Con `DEBUG=True`, vista de referencia: http://127.0.0.1:8000/design-system/

## Contribuciones

Issues y pull requests en GitHub.
