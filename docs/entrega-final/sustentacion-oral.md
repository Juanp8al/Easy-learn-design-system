# Guia de sustentacion oral - EasyLearn Design System

> Duracion sugerida: 15 a 20 minutos. Ajustar nombres de integrantes. Ambos deben participar en proporcion similar.

## Distribucion recomendada

### Integrante 1

- Introduccion.
- Problema.
- Publico objetivo.
- Metodologia.
- Identidad visual.
- Principios UX.

### Integrante 2

- Arquitectura del sistema.
- Roles y casos de uso.
- Componentes principales.
- Accesibilidad.
- Limitaciones.
- Conclusiones.

## Guion por tiempos

### 0:00 - 1:00 | Presentacion

"Buenos dias. Somos [nombres] y presentamos EasyLearn Design System, una plataforma academica tipo LMS desarrollada como proyecto final de Interaccion Hombre Computador. El objetivo fue construir una experiencia clara, accesible y consistente para estudiantes, docentes y administradores."

### 1:00 - 2:30 | Problema

"Identificamos que en muchos entornos academicos la informacion se encuentra dispersa: cursos, entregas, fechas, apuntes, usuarios y matriculas. Esto genera sobrecarga cognitiva y dificulta que cada usuario priorice sus tareas. Por eso planteamos una solucion centrada en roles."

### 2:30 - 4:00 | Solucion

"EasyLearn centraliza la experiencia academica. El estudiante consulta cursos, actividades y material de estudio; el docente revisa cursos asignados y entregas; el administrador gestiona usuarios, carreras, periodos, cursos ofertados y matriculas."

### 4:00 - 5:30 | Metodologia

"La metodologia fue incremental. Primero analizamos necesidades, luego revisamos referentes como Material Design, Human Interface Guidelines, Fluent, Carbon y Nielsen Norman Group. Despues definimos paleta, tipografia y componentes, y finalmente implementamos el prototipo funcional en Django."

### 5:30 - 7:00 | Sistema visual

"La identidad visual usa azul profundo para navegacion institucional, azul claro para acciones principales, verde para exito, amarillo para advertencias y rojo para errores. La tipografia es Inter porque ofrece buena legibilidad en interfaces digitales."

### 7:00 - 9:00 | Arquitectura funcional

"El sistema esta dividido en modulos Django. `accounts` maneja usuarios y roles; `academia` gestiona programas, periodos, cursos ofertados y matriculas; `notes` permite organizar apuntes; `glossary` gestiona terminos; y `revision` permite manejar objetivos y fechas de repaso."

### 9:00 - 11:00 | Roles y casos de uso

"Un usuario inicia sesion y el sistema lo redirige segun su rol. El estudiante entra al dashboard y ve cursos matriculados, actividades y calendario. El docente ve sus cursos asignados y estudiantes activos. El administrador tiene acciones rapidas para crear usuarios, carreras, cursos, periodos y matriculas."

### 11:00 - 13:00 | Componentes

"Los componentes principales son login, sidebar, header con busqueda, cards resumen, tablas, botones, badges, calendario y catalogo de cursos. Estos componentes mantienen consistencia visual y reducen el esfuerzo de aprendizaje del usuario."

### 13:00 - 15:00 | Accesibilidad

"Aplicamos practicas de accesibilidad como idioma en español, labels para formularios, textos ocultos para lectores de pantalla, atributos ARIA, estados de foco visibles y soporte para usuarios con reduccion de movimiento. Ademas, los estados no dependen solo del color, tambien incluyen texto."

### 15:00 - 17:00 | Valor diferencial y mejoras

"El valor diferencial es que EasyLearn no es solo una maqueta visual: tiene una base funcional, modelos de datos y roles reales. Como mejoras futuras, se propone conectar promedio y calendario real, ampliar el modelo de entregas y ejecutar pruebas de accesibilidad mas completas."

### 17:00 - 18:30 | Conclusion

"Concluimos que EasyLearn cumple con los objetivos del proyecto porque aplica principios de IHC, presenta una biblioteca visual coherente, incluye accesibilidad y resuelve un problema academico real. Es una base escalable para una plataforma LMS profesional."

### 18:30 - 20:00 | Preguntas

"Quedamos atentos a sus preguntas."

## Preguntas tecnicas probables y respuestas

### ¿Por que usaron azul como color principal?

Porque comunica confianza, tecnologia y estabilidad. En EasyLearn se usa para navegacion y acciones principales. Los colores de estado se separan: verde para exito, amarillo para advertencia y rojo para error.

### ¿Como aplicaron accesibilidad?

Con etiquetas semanticas, `aria` en menus, foco visible, `role="status"`, soporte para reduccion de movimiento y textos que acompañan los colores de estado.

### ¿Que diferencia a EasyLearn de un LMS comun?

La propuesta une un LMS academico con un sistema de diseno propio, roles diferenciados y herramientas personales como apuntes, glosario y objetivos de repaso.

### ¿Que principio UX consideran mas importante en el proyecto?

La consistencia. Al mantener estructura, colores, botones y estados coherentes, el usuario aprende una vez y puede usar diferentes secciones sin confusion.

### ¿El proyecto es solo visual?

No. Tiene implementacion funcional en Django, modelos de usuarios, roles, programas, periodos, cursos ofertados, matriculas, cursos personales, glosario y objetivos de repaso.

### ¿Que falta para llevarlo a produccion?

Completar integraciones con datos academicos reales, ampliar pruebas, fortalecer seguridad segun despliegue, implementar entregas y calificaciones reales, y realizar evaluaciones de usabilidad con usuarios.

## Checklist antes de sustentar

- [ ] Abrir el proyecto y probar login.
- [ ] Tener capturas de estudiante, docente y administrador.
- [ ] Revisar que ambos integrantes conozcan los modulos.
- [ ] Practicar el tiempo de exposicion.
- [ ] Preparar respuesta sobre accesibilidad y colores.
- [ ] Llevar PDF del documento y presentacion.
- [ ] Confirmar nombres de archivos segun la guia.

