# EasyLearn Campus LMS

EasyLearn es una plataforma universitaria de gestion del aprendizaje construida con Django. El proyecto toma como base los informes del sistema de diseno EasyLearn y organiza la experiencia alrededor de estudiantes, docentes y administradores, con foco en claridad, accesibilidad, consistencia visual y seguimiento academico.

## Propuesta del producto

EasyLearn busca resolver problemas frecuentes de los LMS universitarios: navegacion compleja, interfaces inconsistentes, sobrecarga cognitiva y baja accesibilidad. La solucion se orienta a cursos por periodo academico, semanas de clase, materiales de estudio, actividades, entregas, calificaciones, avisos y notificaciones.

## Estado actual del repositorio

El proyecto ya incluye:

- Autenticacion con redireccion por rol: estudiante, docente y administrador.
- Portal EasyLearn con sidebar, barra superior, buscador, breadcrumbs, dashboard, cursos y calificaciones.
- Panel docente con cursos asignados, entregas, foros/avisos e historial de calificaciones.
- Panel administrador con usuarios, carreras/programas, cursos ofertados, matriculas y periodos academicos.
- Modelos institucionales base: `Program`, `AcademicPeriod`, `Offering` y `Enrollment`.
- Modulos heredados de apoyo academico: notas, glosario y revision personal.
- Interfaz responsive con tokens de marca EasyLearn: azul institucional `#1E3A8A`, verde tecnologico `#10B981`, naranja de apoyo `#F59E0B`, tipografia Inter y foco visible.

## Documentacion del proyecto

- [`docs/easylearn-professionalization.md`](docs/easylearn-professionalization.md): analisis de los documentos entregados y plan tecnico para dejar el proyecto profesional.
- [`docs/requirements-traceability.md`](docs/requirements-traceability.md): trazabilidad entre requerimientos, casos de uso, MER y estado actual de implementacion.

## Stack tecnico

- Python 3.10+
- Django
- PostgreSQL en produccion o SQLite para desarrollo local
- WhiteNoise para archivos estaticos
- HTML, CSS y JavaScript vanilla para el shell EasyLearn

## Instalacion local

1. Crear y activar un entorno virtual.

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias.

```bash
pip install -r requirements.txt
```

3. Crear el archivo `.env` a partir del ejemplo.

```bash
cp .env.example .env
```

4. Para desarrollo rapido con SQLite, definir:

```bash
DEVELOPMENT_MODE=True
DEBUG=True
```

5. Aplicar migraciones y ejecutar el servidor.

```bash
python manage.py migrate
python manage.py runserver
```

6. Abrir `http://localhost:8000/`.

## Variables de entorno principales

Ver `.env.example` para una plantilla completa. En produccion se debe definir `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.

## Roles principales

- **Estudiante:** consulta cursos inscritos, semanas academicas, materiales, actividades, entregas, calendario y calificaciones.
- **Docente:** gestiona cursos asignados, publica contenido, revisa entregas, califica, retroalimenta y comunica avisos.
- **Administrador:** gestiona usuarios, roles, carreras, cursos ofertados, matriculas y periodos academicos.

## Prioridades tecnicas pendientes

1. Completar el MER con modelos de semana academica, material, actividad, entrega, calificacion, foro, participacion, aviso y notificacion.
2. Conectar las pantallas demo del portal con datos reales de esos modelos.
3. Homologar las pantallas heredadas de notas, glosario y revision con el sistema visual EasyLearn.
4. Agregar pruebas de permisos por rol, restricciones de inscripcion y flujos de entrega/calificacion.
5. Documentar componentes reutilizables conforme al Informe 3.

## Licencia

Pendiente de definicion.
