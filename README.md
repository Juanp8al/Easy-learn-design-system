# EasyLearn Design System

EasyLearn es un prototipo funcional desarrollado en Django para una plataforma academica tipo LMS. El proyecto combina un sistema visual propio con flujos reales de autenticacion, portales por rol y gestion academica basica para estudiantes, docentes y administradores.

El repositorio sirve como evidencia tecnica para el proyecto final de Interaccion Hombre Computador: muestra decisiones de diseno, componentes reutilizables, principios UX, accesibilidad y una base funcional que permite sustentar la propuesta frente a criterios academicos y profesionales.

## Alcance del sistema

- **Autenticacion y recuperacion de cuenta**: inicio de sesion, cierre de sesion, cambio y recuperacion de contrasena mediante vistas de Django.
- **Roles de usuario**: estudiante, docente y administrador, con redireccion a dashboard segun el rol.
- **Portal estudiante**: resumen de cursos matriculados, actividades prioritarias, calendario visual, rendimiento y material de estudio personal.
- **Portal docente**: cursos asignados, estudiantes activos, entregas pendientes y resumen del periodo.
- **Portal administrador**: gestion de usuarios, programas, periodos, cursos ofertados y matriculas.
- **Gestion academica**: modelo de carrera/programa, periodo academico, curso ofertado e inscripcion.
- **Material de estudio**: cursos personales, temas, subtemas, entradas de apuntes, glosario y objetivos de repaso.
- **Design system**: paleta, tipografia, sidebar, header, botones, tarjetas, tablas, badges, estados, formularios y patrones responsive.

## Tecnologias principales

- Python
- Django
- HTML con plantillas Django
- CSS modular en `static/easylearn/css/`
- JavaScript progresivo en `static/easylearn/js/easylearn-app.js`
- SQLite para desarrollo local por defecto

## Estructura relevante

```text
accounts/                 Usuarios, roles, autenticacion y perfiles
academia/                 Programas, periodos, cursos ofertados e inscripciones
notes/                    Cursos personales, temas, subtemas y apuntes
glossary/                 Terminos academicos por curso
revision/                 Objetivos de repaso y seguimiento de fechas
templates/easylearn/      Portales estudiante, docente y administrador
static/easylearn/css/     Sistema visual de dashboard y login
static/easylearn/js/      Navegacion por vistas, busqueda y filtros
docs/entrega-final/       Material base para la entrega final integral
```

## Paleta base

| Uso | Token | Color |
| --- | --- | --- |
| Navegacion principal | `--sidebar-deep` | `#171f4d` |
| Sidebar activo | `--sidebar-active-bg` | `#3b4cb8` |
| Accion/informacion | `--info-500` | `#3b82f6` |
| Exito/confirmacion | `--success-700` | `#059669` |
| Advertencia/pendiente | `--warning-500` | `#f59e0b` |
| Error/peligro | `--error-500` | `#ef4444` |
| Fondo neutral | `--neutral-bg` | `#f9fafb` |
| Texto principal | `--text-primary` | `#111827` |

## Instalacion local

1. Crear y activar un entorno virtual.
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Aplicar migraciones:

```bash
python manage.py migrate
```

4. Ejecutar el servidor:

```bash
python manage.py runserver
```

5. Abrir el navegador en `http://localhost:8000/`.

## Entrega final integral

El proyecto incluye borradores en `docs/entrega-final/` para preparar:

- Documento escrito final.
- Brief ejecutivo.
- Presentacion profesional.
- Guia de sustentacion oral.

Estos archivos estan pensados como fuente editable antes de exportar a PDF con los nombres solicitados por la guia de la asignatura.
