# EasyLearn — LMS universitario

Plataforma Django que conecta **configuración institucional → aula docente → cursado estudiante**, con apuntes personales separados en **Repaso**.

> **Resumen:** Conectar el flujo semana → actividad → entrega → nota en el aula, dejar los apuntes en Repaso (`notes`), y usar el mismo shell visual en los tres roles — eso eleva el proyecto de demo a LMS profesional.

Repositorio: [Easy-learn-design-system](https://github.com/Juanp8al/Easy-learn-design-system).

## Requisitos

- Python 3.10+
- pip

## Cómo correr el proyecto (antes de presentar)

```bash
cd "Easy learn design system"
copy .env.example .env          # Windows (opcional)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # obligatorio: simulación completa (cuentas demo + aula + repaso)
python manage.py runserver
```

Abrir: http://127.0.0.1:8000/

**Recarga forzada en el navegador** (`Ctrl+F5`) si cambió CSS/JS.

En desarrollo, los archivos subidos se sirven desde `media/` (entregas y materiales).

## Cuentas de demostración (`seed_demo`)

Contraseña para todas: **`EasyLearn_Demo_2026`**

| Usuario | Rol | Panel |
|---------|-----|--------|
| `estudiante_demo` | Estudiante | `/dashboard` (Inicio, Calificaciones, Calendario, Mensajes, Repaso) |
| `docente_demo` | Docente | `/accounts/panel/docente/` |
| `admin_demo` | Administrador | `/accounts/panel/administrador/` |

También se crean `maria_demo`, `juan_demo`, `sofia_demo`, `diego_demo` (misma contraseña) para llenar tablas del administrador.

Comandos útiles:

```bash
python manage.py seed_demo
python manage.py check
python manage.py test accounts classroom
```

`seed_demo` ya ejecuta `seed_classroom --weeks 5 --force` (5 semanas, materiales, foros, actividades y entrega pendiente de `estudiante_demo`).

## Guion de presentación (~18 min)

### 1. Sitio público (1 min)

- `/home/` → mensaje institucional → **Iniciar sesión**.

### 2. Estudiante — `estudiante_demo` (5 min)

| Paso | Qué mostrar |
|------|-------------|
| Login | Logo, formulario limpio |
| `/dashboard` | Inicio, KPIs, mini calendario |
| Menú | **Calificaciones**, **Calendario**, **Mensajes** (avisos del curso) |
| **Aula virtual** `/aula/` | Cursos IHC, BD1, ALG, RED → entrar a **IHC** |
| Semana | Materiales (lectura + video) y actividades (5 semanas) |
| Entrega | Tarea «Ensayo · principios de UX» → formulario de entrega |
| Perfil | Avatar → **Ir a mi perfil** → layout tipo Moodle → **Cambiar contraseña** en Miscelánea |
| Repaso | Menú **Repaso** → materiales por curso + objetivos personales |

### 3. Docente — `docente_demo` (6 min)

| Paso | Qué mostrar |
|------|-------------|
| Panel | Inicio, **Mis cursos**, **Entregas**, **Foros y avisos**, **Historial** |
| Entregas | Entrega de `estudiante_demo` **sin calificar** (para calificar en vivo) |
| Calificar | Formulario profesional → guardar nota → vuelve al panel |
| Gestionar curso | `/aula/docente/curso/<id>/` → tabla de semanas, **publicar aviso**, foros abrir/cerrar |
| Foros | Pestaña foros: foros por semana (sembrados en `seed_demo`) |

### 4. Administrador — `admin_demo` (4 min)

| Paso | Qué mostrar |
|------|-------------|
| Panel | Usuarios, carreras, ofertas, matrículas, períodos |
| CRUD institucional | Botones **Editar / Crear** → Django Admin (`/admin/`) — válido para demo académica |
| Perfil | Mismo shell que estudiante/docente |

### 5. Cierre honesto (2 min)

**Qué sí es producto listo para demo**

- Tres roles con el mismo design system (claro/oscuro).
- Matrícula → aula → entrega → calificación → avisos.
- Notificaciones en campana.
- Perfil y contraseña dentro del portal.

**Qué no es “100% LMS sin Admin”** (decirlo con claridad)

| Falta | Impacto |
|-------|---------|
| Hilos y respuestas en foros | Solo metadatos del foro + abrir/cerrar |
| Docente crea semanas/materiales en portal | Hoy: `seed_classroom` o Django Admin |
| Chat alumno ↔ docente | Mensajes = avisos institucionales |
| CRUD nativo en panel admin bonito | Enlaces a `/admin/` |
| Producción en la nube | Local + SQLite por ahora |

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
| Estudiante | `/dashboard` · `/aula/` · `/accounts/profile/` · **Repaso** → `/revision/` |
| Docente | `/accounts/panel/docente/` · gestión `/aula/docente/curso/<id>/` |
| Administrador | `/accounts/panel/administrador/` |
| Design system (solo `DEBUG`) | `/design-system/` |

El menú **Aula virtual** lleva a `/aula/` (cursos institucionales). Los apuntes de `notes.Course` no aparecen como “curso universitario” en el menú principal.

## Git y archivos locales

- Inicialice el repositorio **solo** en la carpeta del proyecto (`Easy learn design system`), no en `C:\Users\Familia`.
- No versionar: `.env`, `db.sqlite3`, `staticfiles/`, `media/`, `.venv/` (ya listados en `.gitignore`).
- Plantilla de entorno: `.env.example` (`DJANGO_SECRET_KEY`, `DEBUG`, `DEVELOPMENT_MODE`, `DATABASE_URL`).
- **Antes de entregar:** `git add`, `git commit`, `git push` para que el docente vea el repo actualizado.

## Design system

Tokens (Informe 2): azul `#1E3A8A`, verde `#10B981`, naranja `#F59E0B`, neutros `#F8FAFC` / `#E2E8F0` / `#64748B` / `#0F172A`.

Con `DEBUG=True`, vista de referencia: http://127.0.0.1:8000/design-system/

## Contribuciones

Issues y pull requests en GitHub.
