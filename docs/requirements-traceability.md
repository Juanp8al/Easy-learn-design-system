# Trazabilidad de requerimientos EasyLearn

Esta matriz resume como los documentos funcionales, casos de uso y MER se relacionan con el estado actual del codigo.

## Leyenda

- **Implementado:** existe funcionalidad conectada a vistas/modelos reales.
- **Parcial:** existe interfaz, prototipo o base de datos incompleta.
- **Pendiente:** requiere nuevos modelos, vistas o reglas de negocio.

## Requerimientos funcionales

| Bloque | Estado | Evidencia actual | Siguiente paso |
| --- | --- | --- | --- |
| RF-01 Inicio de sesion | Implementado | `accounts.views.login`, `templates/registration/login.html` | Mantener pruebas de autenticacion y sesion. |
| RF-02 Dashboard | Implementado | `notes.views.dashboard`, `accounts.views.dashboard_teacher`, `accounts.views.dashboard_admin` | Conectar mas KPIs a modelos academicos reales. |
| RF-03 Navegacion persistente | Implementado | `templates/easylearn/includes/portal_sidebar*.html` | Agregar Configuracion cuando exista modulo. |
| RF-04 Breadcrumbs | Implementado | `bread-nav` y `easylearn-app.js` | Mantener consistencia en nuevas vistas. |
| RF-05 Busqueda superior | Parcial | Busqueda filtra vistas y usa `notes:search` | Ampliar busqueda a actividades/materiales cuando existan. |
| RF-06 Notificaciones | Parcial | Icono visual en header y mensajes Django | Crear modelo `Notification` y centro de notificaciones. |
| RF-07 a RF-13 Dashboard academico | Parcial | Cards, tablas y eventos del portal | Sustituir datos demo por actividades, avisos y calificaciones reales. |
| RF-14 a RF-21 Cursos | Parcial | `Offering`, `Enrollment`, catalogo y detalle demo | Crear detalle real por curso ofertado y semanas. |
| RF-22 a RF-26 Semanas academicas | Pendiente | Vista demo de semana | Crear modelo `AcademicWeek`. |
| RF-27 a RF-32 Materiales | Pendiente | Filas demo de recursos | Crear modelo `StudyMaterial` y permisos de publicacion. |
| RF-33 a RF-44 Actividades y entregas | Parcial | Flujo demo en `_portal_views_extra.html` | Crear `Activity` y `Submission`; conectar archivos, borradores y validaciones. |
| RF-45 a RF-51 Calificaciones | Parcial | Vista de calificaciones y panel docente | Crear `Grade` asociado a entregas. |
| RF-52 a RF-55 Recordatorios y avisos | Parcial | Objetivos de revision y avisos demo | Crear `Announcement` y `Notification`. |
| RF-56 a RF-62 Componentes UI | Implementado parcial | CSS EasyLearn, cards, tablas, alertas, botones, formularios | Extraer componentes reutilizables o documentar clases estables. |

## Requerimientos no funcionales

| Bloque | Estado | Observacion |
| --- | --- | --- |
| RNF-01 a RNF-05 Usabilidad | Parcial | El portal reduce carga cognitiva, pero modulos heredados aun usan otra experiencia visual. |
| RNF-06 a RNF-10 Accesibilidad | Parcial | Hay `lang`, labels, foco visible, skip link y textos en iconos; falta auditoria WCAG completa. |
| RNF-11 a RNF-14 Consistencia visual | Parcial | Portal y login estan alineados; notas/glosario/revision necesitan homologacion. |
| RNF-15 a RNF-17 Responsive | Parcial | CSS tiene breakpoints; falta validacion en todas las pantallas heredadas. |
| RNF-18 a RNF-20 Rendimiento | Parcial | Vistas simples; falta medir con datos academicos reales. |
| RNF-21 a RNF-24 Seguridad | Parcial | Hay login y decoradores por rol; faltan pruebas exhaustivas de permisos por curso/inscripcion. |
| RNF-25 a RNF-28 Mantenibilidad | Parcial | Apps separadas; CSS monolitico grande requiere modularizacion futura. |
| RNF-29 a RNF-32 Calidad de interaccion | Parcial | Hay feedback en flujo demo; falta persistencia real de entregas/calificaciones. |
| RNF-33 a RNF-36 Marca | Implementado parcial | Paleta, Inter, logo SVG y tokens estan alineados al design system. |

## Casos de uso por actor

| Actor | Implementado | Parcial/Pendiente |
| --- | --- | --- |
| Usuario | Iniciar sesion, cerrar sesion, recuperar password, consultar perfil | Notificaciones reales |
| Estudiante | Ver dashboard, cursos personales, cursos inscritos, calificaciones demo, calendario/revision | Semana real, materiales, entrega real, foros, progreso real |
| Docente | Panel docente, cursos asignados, tablas de matriculas | Crear semanas, publicar materiales, crear actividades, revisar/calificar entregas |
| Administrador | Usuarios, roles, carreras, cursos ofertados, matriculas, periodos via admin/panel | Reportes institucionales y auditoria avanzada |
| Servicio de notificaciones | Pendiente | Integracion interna o externa para avisos automaticos |

## MER: entidades y estado

| Entidad del MER | Estado en codigo |
| --- | --- |
| Rol | Implementado como `Student.Role` |
| Usuario | Implementado como `accounts.Student` |
| Estudiante | Parcial: rol + perfil + programa/semestre |
| Docente | Parcial: rol + asignacion en `Offering.teacher` |
| Administrador | Parcial: rol + `is_staff` |
| Periodo academico | Implementado como `academia.AcademicPeriod` |
| Curso | Parcial: `academia.Offering` y `notes.Course` coexisten |
| Inscripcion | Implementado como `academia.Enrollment` |
| Semana academica | Pendiente |
| Material de estudio | Pendiente |
| Actividad | Pendiente |
| Entrega | Pendiente |
| Calificacion | Pendiente |
| Foro | Pendiente |
| Participacion en foro | Pendiente |
| Aviso | Pendiente |
| Notificacion | Pendiente |

## Decision recomendada

El proyecto debe evolucionar desde el prototipo visual actual hacia un dominio academico completo. La prioridad no es agregar mas pantallas demo, sino crear los modelos faltantes del MER y conectar las vistas existentes a datos reales con permisos por rol.
