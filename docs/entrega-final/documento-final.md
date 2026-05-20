# ProyectoFinal_GrupoXX_Final - Documento escrito final

> Reemplazar `GrupoXX`, integrantes, codigos, docente y fecha antes de exportar a PDF.

## Portada

**Universidad de Santander - UDES**  
**Programa:** Ingenieria de Software  
**Asignatura:** Interaccion Hombre Computador  
**Proyecto:** EasyLearn Design System  
**Entrega:** Entrega final integral  
**Integrantes:**  
- Nombre integrante 1 - Codigo estudiantil  
- Nombre integrante 2 - Codigo estudiantil  
**Docente:** Nombre del docente  
**Fecha:** 2026A

---

## 1. Introduccion

EasyLearn Design System es una propuesta de plataforma academica tipo LMS orientada a mejorar la experiencia de estudiantes, docentes y administradores en la gestion de cursos, actividades, apuntes y procesos institucionales. El proyecto integra una interfaz visual coherente, componentes reutilizables y una base funcional desarrollada en Django.

La propuesta nace desde la necesidad de que los usuarios academicos encuentren informacion clave sin sobrecarga visual: cursos matriculados, actividades prioritarias, fechas proximas, material personal de estudio, usuarios, periodos y matriculas. Para esto se diseno un sistema con navegacion lateral, cabecera de busqueda, tarjetas resumen, tablas, estados visuales, botones, badges y flujos de autenticacion.

El desarrollo se enmarca en los principios de Interaccion Hombre Computador: usabilidad, consistencia, retroalimentacion, prevencion de errores, jerarquia visual, accesibilidad e inclusion. El resultado no se limita a una apariencia grafica: el sistema demuestra estructura funcional, patrones de navegacion y reglas de uso que permiten su escalabilidad.

## 2. Justificacion

En entornos universitarios, la informacion suele encontrarse distribuida entre varias plataformas, correos y documentos. Esta fragmentacion incrementa la carga cognitiva del estudiante y dificulta que docentes y administradores tengan una vision clara del estado academico.

EasyLearn propone centralizar la experiencia academica en tres portales:

- **Estudiante:** consulta de cursos, actividades prioritarias, calendario, calificaciones y material personal.
- **Docente:** visualizacion de cursos asignados, estudiantes activos, entregas pendientes y fechas relevantes.
- **Administrador:** gestion de usuarios, carreras/programas, periodos, cursos ofertados y matriculas.

La justificacion del sistema se apoya en la necesidad de una interfaz consistente, accesible y comprensible. Los colores no se usan de forma decorativa sino semantica: azul para acciones y navegacion, verde para exito, amarillo para advertencias o pendientes y rojo para errores o peligro. Esta convencion reduce ambiguedades y facilita la toma de decisiones.

## 3. Objetivos

### 3.1 Objetivo general

Diseñar y desarrollar un sistema de diseno funcional para EasyLearn, una plataforma academica que facilite la gestion de cursos, actividades y usuarios mediante una experiencia coherente, accesible y centrada en el usuario.

### 3.2 Objetivos especificos

- Definir una identidad visual propia para EasyLearn mediante paleta, tipografia, espaciado, radios, estados y componentes reutilizables.
- Implementar portales diferenciados para estudiante, docente y administrador segun necesidades de uso.
- Aplicar principios de usabilidad e Interaccion Hombre Computador en la navegacion, jerarquia visual, retroalimentacion y prevencion de errores.
- Incorporar buenas practicas de accesibilidad mediante etiquetas, contraste, navegacion clara, estados visibles y soporte para reduccion de movimiento.
- Documentar los componentes principales, casos de uso y decisiones de diseno para facilitar la sustentacion tecnica del proyecto.

## 4. Marco conceptual

### 4.1 Interaccion Hombre Computador

La Interaccion Hombre Computador estudia la relacion entre las personas y los sistemas digitales. Su objetivo es que la tecnologia sea util, comprensible, eficiente y segura para los usuarios. En EasyLearn, la IHC se evidencia en la organizacion de informacion por rol, la navegacion persistente, la busqueda contextual y los estados visuales.

### 4.2 Usabilidad

La usabilidad se relaciona con que el usuario pueda cumplir sus objetivos con eficacia, eficiencia y satisfaccion. EasyLearn usa patrones conocidos como dashboards, tarjetas resumen, tablas, botones de accion y menus laterales, lo cual reduce el aprendizaje inicial.

### 4.3 Sistema de diseno

Un sistema de diseno es un conjunto de reglas, componentes y patrones reutilizables que permiten construir interfaces consistentes. EasyLearn define tokens de color, tipografia Inter, radios de borde, botones, badges, tablas, cards, sidebar, header y componentes de dashboard.

### 4.4 Accesibilidad digital

La accesibilidad busca que personas con diferentes capacidades puedan usar el sistema. El proyecto incorpora atributos `aria`, etiquetas ocultas con `.visually-hidden`, mensajes con `role="status"`, foco visible, estructura semantica y soporte para `prefers-reduced-motion`.

### 4.5 Diseno centrado en el usuario

El diseno centrado en el usuario implica entender los perfiles, objetivos, limitaciones y contexto de uso. EasyLearn separa las tareas por usuario: el estudiante consulta y organiza, el docente revisa y acompaña, y el administrador configura y controla.

## 5. Metodologia

La metodologia aplicada fue incremental:

1. **Analisis del problema:** identificacion de necesidades academicas: cursos, entregas, calendario, notas, usuarios y roles.
2. **Benchmarking conceptual:** revision de sistemas de diseno reconocidos como Material Design, Fluent, Carbon, Atlassian y Bootstrap.
3. **Definicion visual:** seleccion de paleta institucional azul, acentos por estado, tipografia Inter y componentes tipo dashboard.
4. **Prototipado funcional:** implementacion en Django con plantillas HTML, CSS y JavaScript progresivo.
5. **Organizacion por rol:** creacion de vistas diferenciadas para estudiante, docente y administrador.
6. **Evaluacion UX:** revision de consistencia, jerarquia, feedback, accesibilidad y claridad de flujos.
7. **Documentacion final:** preparacion de documento, brief, presentacion y sustentacion.

## 6. Desarrollo del sistema

### 6.1 Arquitectura general

El proyecto esta desarrollado con Django. La estructura se divide en aplicaciones:

| Modulo | Funcion |
| --- | --- |
| `accounts` | Usuarios, roles, autenticacion, perfiles y redireccion por rol. |
| `academia` | Programas, periodos academicos, cursos ofertados e inscripciones. |
| `notes` | Cursos personales, temas, subtemas y apuntes. |
| `glossary` | Terminos academicos y definiciones por curso. |
| `revision` | Objetivos de repaso, fechas, estado de progreso y vencimiento. |
| `templates/easylearn` | Portales visuales de estudiante, docente y administrador. |
| `static/easylearn` | CSS, JavaScript e identidad visual del sistema. |

### 6.2 Roles del sistema

EasyLearn trabaja con tres roles principales:

- **Estudiante:** consulta cursos matriculados, actividades, calendario, calificaciones y apuntes.
- **Docente:** revisa cursos asignados, estudiantes activos, entregas y foros.
- **Administrador:** gestiona usuarios, programas, periodos, cursos ofertados y matriculas.

El modelo `Student` incluye el campo `role` y el metodo `get_dashboard_url_name()`, que redirige al usuario al panel correspondiente despues del login.

### 6.3 Flujo de autenticacion

El login se implementa en `templates/registration/login.html` y usa estilos especificos en `static/easylearn/css/login-page.css`. La pantalla incluye:

- Marca EasyLearn.
- Formulario de usuario y contrasena.
- Recordarme.
- Enlace a recuperacion de contrasena.
- Boton principal de inicio de sesion.
- Fondo visual con gradiente y luces ambientales.

### 6.4 Portal estudiante

El portal estudiante muestra:

- Saludo personalizado.
- Cursos inscritos.
- Actividades pendientes.
- Promedio actual.
- Tabla de cursos matriculados.
- Actividades prioritarias.
- Calendario visual.
- Proximas evaluaciones.
- Catalogo de apuntes personales.

### 6.5 Portal docente

El portal docente muestra:

- Cursos asignados por la institucion.
- Estudiantes activos.
- Entregas pendientes.
- Fechas proximas.
- Accesos a cursos, entregas, foros e historial.

### 6.6 Portal administrador

El portal administrador muestra:

- Usuarios activos.
- Cursos ofertados.
- Matriculas activas.
- Periodo actual.
- Acciones rapidas para crear usuario, carrera, curso, matricula y periodo.
- Alertas administrativas como cursos sin docente o estudiantes sin carrera.

## 7. Principios UX aplicados

| Principio | Aplicacion en EasyLearn |
| --- | --- |
| Consistencia | Sidebar, header, cards, botones y tablas mantienen estilos compartidos. |
| Jerarquia visual | Cards superiores resumen lo mas importante; tablas detallan informacion secundaria. |
| Feedback | Mensajes del sistema, badges de estado y cambios visuales al interactuar. |
| Prevencion de errores | Roles separados, acciones identificadas por color y textos explicativos en estados vacios. |
| Reconocimiento antes que memoria | Menus visibles, breadcrumbs y botones con verbos claros. |
| Flexibilidad | Busqueda contextual, filtros de cursos y vistas por tarjeta/lista/resumen. |
| Control del usuario | Navegacion lateral, menu de cuenta y acciones rapidas visibles. |

## 8. Accesibilidad

El proyecto incorpora buenas practicas de accesibilidad:

- Idioma del documento configurado como `lang="es"`.
- Formularios con labels visibles u ocultos semanticamente.
- Clase `.visually-hidden` para textos necesarios para lectores de pantalla.
- Menus con `aria-expanded`, `aria-haspopup` y `aria-controls`.
- Mensajes con `role="status"`.
- Estados de foco con `:focus-visible`.
- Soporte para usuarios con reduccion de movimiento mediante `prefers-reduced-motion`.
- Colores por estado con apoyo textual, no solo color.

### Recomendaciones de mejora

- Verificar contraste de textos amarillos sobre fondos claros y preferir `#b45309` para texto de advertencia.
- Evitar acciones deshabilitadas como `span` si deben comportarse como enlaces en version final.
- Documentar pruebas manuales de teclado y lector de pantalla.

## 9. Componentes principales

| Componente | Uso | Evidencia |
| --- | --- | --- |
| Login | Acceso al sistema y recuperacion de cuenta | `templates/registration/login.html` |
| Sidebar | Navegacion principal por rol | `portal_sidebar*.html` |
| Header | Busqueda, notificaciones y menu de usuario | `portal_header.html` |
| Cards resumen | Indicadores clave de dashboard | `portal_dashboard.html`, `portal_admin_dashboard.html` |
| Tablas | Cursos, usuarios, matriculas y actividades | Componentes `.sheet` |
| Badges | Estados visuales: activo, pendiente, borrador, completado | `.badge-txt`, `.el-badge` |
| Botones | Acciones primarias, secundarias, outline y pequenas | `.btn-main`, `.btn-outline`, `.btn-accent`, `.btn-sm` |
| Catalogo de cursos | Visualizacion de material academico | `portal_cursos.html` |
| Calendario | Fechas y proximas evaluaciones | Mini calendario y vistas de revision |

## 10. Guia cromatica

| Color | Token | Uso recomendado |
| --- | --- | --- |
| Azul principal | `#3b82f6` | Ver curso, ver mas, guardar, continuar, navegacion y accion principal. |
| Azul profundo | `#171f4d` | Sidebar, header, fondos institucionales. |
| Verde | `#059669` | Exito, completado, confirmado, activo. |
| Amarillo | `#f59e0b` | Pendiente, aviso, fecha limite cercana, revision pendiente. |
| Rojo | `#ef4444` | Error, vencido, eliminar, peligro. |
| Blanco/neutral | `#ffffff`, `#f9fafb` | Superficies limpias, lectura y contraste. |

## 11. Casos de uso

### CU-01 Iniciar sesion

**Actor:** usuario registrado.  
**Objetivo:** entrar al sistema segun su rol.  
**Flujo:** ingresa credenciales, el sistema valida, inicia sesion y redirige a estudiante, docente o administrador.  
**Principio UX:** feedback inmediato y reduccion de pasos.

### CU-02 Consultar cursos matriculados

**Actor:** estudiante.  
**Objetivo:** ver asignaturas activas del periodo.  
**Flujo:** entra al dashboard, revisa tabla de cursos, usa busqueda o entra a Mis cursos.  
**Principio UX:** visibilidad de informacion prioritaria.

### CU-03 Revisar actividad pendiente

**Actor:** estudiante.  
**Objetivo:** identificar actividades activas o atrasadas.  
**Flujo:** el dashboard muestra badges, fechas y accion para abrir/completar.  
**Principio UX:** jerarquia visual y prevencion de errores.

### CU-04 Gestionar cursos asignados

**Actor:** docente.  
**Objetivo:** revisar sus cursos y estudiantes activos.  
**Flujo:** ingresa al portal docente y consulta resumen de cursos, estudiantes y entregas.  
**Principio UX:** contenido adaptado al rol.

### CU-05 Crear matricula

**Actor:** administrador.  
**Objetivo:** inscribir estudiante en curso ofertado.  
**Flujo:** usa acciones rapidas o administracion Django, selecciona curso y estudiante, guarda.  
**Principio UX:** tareas administrativas agrupadas y visibles.

### CU-06 Recuperar contrasena

**Actor:** usuario sin acceso a su cuenta.  
**Objetivo:** solicitar enlace de recuperacion.  
**Flujo:** desde login selecciona "Olvidaste tu contrasena", ingresa correo y recibe instrucciones.  
**Principio UX:** asistencia para recuperacion ante errores de acceso.

## 12. Valor diferencial

EasyLearn se diferencia porque combina:

- LMS academico con roles claros.
- Material de estudio personal y glosario.
- Revision por objetivos y fechas.
- Administracion academica integrada.
- Sistema visual documentable y escalable.
- Enfoque de accesibilidad e IHC desde la interfaz.

## 13. Limitaciones actuales

- Algunas metricas como promedio y proxima clase aparecen como placeholders hasta conectar informacion academica real.
- El conteo de entregas pendientes del docente esta preparado pero requiere modelo especifico de entregas.
- Se recomienda ampliar pruebas de accesibilidad automatizadas y manuales.
- La exportacion final a PDF debe hacerse despues de agregar capturas y datos reales del grupo.

## 14. Conclusiones

EasyLearn demuestra una aplicacion integral de principios de Interaccion Hombre Computador en un contexto academico realista. La division por roles reduce la complejidad y permite que cada usuario encuentre rapidamente las acciones que necesita. La paleta de colores y los componentes visuales refuerzan jerarquia, estados y consistencia.

El sistema de diseno facilita la escalabilidad porque define patrones reutilizables para botones, tablas, tarjetas, navegacion y estados. Ademas, la implementacion en Django permite sustentar que la propuesta no es solo visual, sino tambien funcional y conectada a modelos de datos.

Como trabajo final, EasyLearn cumple con los criterios de investigacion, aplicacion de IHC, calidad visual, biblioteca de componentes, accesibilidad, documentacion y valor diferencial. Las mejoras futuras se orientan a conectar datos academicos reales, fortalecer pruebas de accesibilidad y ampliar los flujos de entregas y calificaciones.

## 15. Bibliografia preliminar en APA

Apple. (2024). *Human Interface Guidelines*. https://developer.apple.com/design/human-interface-guidelines/

Google. (2024). *Material Design*. https://m3.material.io/

IBM. (2024). *Carbon Design System*. https://carbondesignsystem.com/

International Organization for Standardization. (2019). *ISO 9241-210: Ergonomics of human-system interaction - Human-centred design for interactive systems*. ISO.

Krug, S. (2014). *Don't make me think, revisited: A common sense approach to web usability* (3rd ed.). New Riders.

Microsoft. (2024). *Fluent 2 Design System*. https://fluent2.microsoft.design/

Nielsen Norman Group. (2024). *10 usability heuristics for user interface design*. https://www.nngroup.com/articles/ten-usability-heuristics/

Norman, D. A. (2013). *The design of everyday things: Revised and expanded edition*. Basic Books.

Tidwell, J., Brewer, C., & Valencia, A. (2020). *Designing interfaces: Patterns for effective interaction design* (3rd ed.). O'Reilly Media.

World Wide Web Consortium. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*. https://www.w3.org/TR/WCAG22/

