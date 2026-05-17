# Profesionalizacion de EasyLearn

Este documento resume el analisis de los informes y documentos entregados para orientar el proyecto hacia una presentacion profesional, coherente y viable como LMS universitario.

## Documentos analizados

- Informe 1: definicion conceptual de EasyLearn Design System, publico objetivo, benchmark, principios de diseno e identidad de marca.
- Informe 2: sistema visual, logo, paleta, tipografia, espaciado, grid, iconografia, estados y tokens.
- Informe 3: biblioteca de componentes e interaccion para botones, campos, select, checkbox, radio, modal, card, tabla, navbar, sidebar, alertas y formularios.
- Requerimientos del sistema: requerimientos funcionales RF-01 a RF-62 y no funcionales RNF-01 a RNF-36.
- Caso de uso: actores Usuario, Estudiante, Docente, Administrador y Servicio de notificaciones, con relaciones include/extend.
- MER: entidades academicas para roles, usuarios, periodos, cursos, inscripciones, semanas, materiales, actividades, entregas, calificaciones, foros, avisos y notificaciones.

## Direccion de producto

EasyLearn debe presentarse como un LMS universitario, no como una aplicacion generica de notas. La narrativa profesional del proyecto debe destacar:

1. Gestion academica por roles.
2. Cursos asociados a periodos academicos y programas.
3. Organizacion de contenido por semanas.
4. Flujo completo de actividad: instrucciones, borrador, validacion, entrega, retroalimentacion y calificacion.
5. Seguimiento del progreso academico en dashboards claros.
6. Interfaz accesible, responsive y consistente con el design system.

## Ajustes aplicados

- README actualizado para describir EasyLearn Campus LMS y no el producto heredado PKMS.
- Logo SVG normalizado y conectado a login/sidebar para evitar referencias rotas a `LOGOOOOOOOO (1).png`.
- Tokens visuales alineados a los informes:
  - `#1E3A8A` como azul institucional.
  - `#10B981` como verde tecnologico para accion/progreso.
  - `#F59E0B` como acento de atencion.
  - escala modular de 8px para espacios principales.
- Mejoras de accesibilidad:
  - enlace "Saltar al contenido principal";
  - foco visible global;
  - region principal con `main`;
  - rutas internas con `aria-hidden` al cambiar vistas;
  - foco programatico al cambiar de vista en el shell.
- Configuracion regional actualizada a `es-co` y `America/Bogota`.
- Documentacion de trazabilidad para separar lo implementado, lo parcial y lo pendiente.

## Estado tecnico actual

### Fortalezas existentes

- Base Django organizada por apps.
- Usuario personalizado con roles de estudiante, docente y administrador.
- Dashboards separados por rol.
- Modelos academicos iniciales: programa, periodo, curso ofertado e inscripcion.
- Portal visual con sidebar, header, breadcrumbs, cards, tablas y formularios.
- Flujo demo de entrega de actividad alineado con el Informe 3.

### Brechas frente al MER

Faltan modelos de dominio centrales:

- Semana academica.
- Material de estudio.
- Actividad.
- Entrega.
- Calificacion.
- Foro.
- Participacion en foro.
- Aviso.
- Notificacion.

Mientras no existan estos modelos, algunas pantallas funcionan como prototipo visual y no como flujo academico completo.

## Recomendacion de arquitectura

Para mantener el proyecto profesional y escalable, conviene crear una app de dominio academico ampliado, por ejemplo `learning`, o extender `academia` si se prefiere concentrar el MER institucional. La separacion recomendada es:

- `accounts`: usuarios, roles, perfil y permisos.
- `academia`: programas, periodos, cursos ofertados e inscripciones.
- `learning`: semanas, materiales, actividades, entregas, calificaciones, foros, avisos y notificaciones.
- `notes`, `glossary`, `revision`: modulos de apoyo, integrados visualmente a EasyLearn o mantenidos como funcionalidad complementaria.

## Criterios de calidad para siguientes cambios

- Todo dato academico visible debe venir de modelos y consultas reales.
- Ningun estudiante debe ver cursos donde no esta inscrito.
- Ningun docente debe gestionar cursos que no tiene asignados.
- Las acciones criticas deben tener validacion, feedback y mensajes claros.
- Los estados no deben depender solo del color: siempre deben incluir texto o etiqueta.
- Las nuevas pantallas deben reutilizar tokens, componentes y patrones del shell EasyLearn.
- Las pruebas deben cubrir permisos por rol, reglas de negocio y flujos de entrega/calificacion.

## Prioridades siguientes

1. Modelar el MER faltante con migraciones y admin.
2. Conectar dashboard, cursos, semanas y actividades a datos reales.
3. Implementar entrega de actividades con archivo/comentario/borrador.
4. Implementar calificacion y retroalimentacion docente.
5. Implementar avisos/notificaciones internas.
6. Homologar notas, glosario y revision al layout EasyLearn.
7. Agregar pruebas automatizadas de reglas de negocio y permisos.
