# Planificación del Proyecto: Academia de Héroes

## 1. Resumen y Metodología

- **Nombre del Proyecto:** Academia de Héroes
- **Cliente:** SurpriseGames
- **Desarrollador:** 1 Persona
- **Herramienta de Gestión:** GitHub Projects & GitHub Actions
- **Fecha de Entrega y Presentación:** 21/04/2026
- **Tecnologías:** Python, Django, ORM de Django, HTML (sin frameworks), CSS puro, Plotly.

## 2. Configuración de GitHub Projects

Para realizar el seguimiento del desarrollo de forma clara, el tablero del proyecto en GitHub se ha configurado usando campos personalizados (Custom Fields) detallados a continuación:

### Estados (Status)

Los flujos por los que pasará cada respectiva tarea son:

- **Por hacer** (Tareas pendientes de iniciar)
- **En desarrollo** (Tareas que se están trabajando en el momento)
- **Terminada** (Tareas concluidas tras validación)

### Etiquetas (Labels)

Para categorizar el enfoque y esfuerzo de cada tarea, se usarán las siguientes etiquetas literales:

- `Bug`: Empleada para identificar y corregir errores funcionales.
- `Codigo`: Tareas asociadas directamente a programación backend (vistas, modelos, lógica).
- `Diseño`: Hace referencia a la creación de interfaces estéticas, HTML/CSS, generación de mockups, diseño de la arquitectura (BBDD/UML), etc.
- `Documentacion`: Escribir tutoriales, notas de los desarrollos, y explicaciones del mismo proyecto.
- `Investigacion`: Tareas centradas en el aprendizaje o POC (Prueba de Concepto), como el aprendizaje integral de Django, su ORM y Plotly.
- `tests`: Creación y ejecución de la suite de pruebas automatizadas.

### Prioridades (Priority)

- **P0**: Crítica/Bloqueante. Su resolución habilita el avance del proyecto.
- **P1**: Alta. Parte de los requisitos funcionales del proyecto.
- **P2**: Media/Baja. Mejoras estéticas y optimizaciones.

### Tamaños (Size)

Estimación nominal de esfuerzo por tarea:

- **XS**: <= 2 horas
- **S**: 3 - 4 horas
- **M**: 5 - 6 horas
- **L**: 7 - 8 horas
- **XL**: > 8 horas

## 3. RoadMap y Desglose de Sprints

Se han programado **3 Sprints de 2 semanas de duración cada uno**. En una jornada de una persona trabajando a un ritmo de 15 horas a la semana, esto garantiza **30 horas lectivas por Sprint** (90 horas de desarrollo totales).

*Nota: Todas las tareas inician con el estado **Por hacer**.*

---

### Sprint 1: Arquitectura, Modelado e Infraestructura Base (30 Horas)

**Objetivo del Sprint**: Estructuración del entorno de trabajo CI/CD, curva de aprendizaje resuelta y un sistema inicial de base de datos interconectado en el framework elegido, aportando un modelado inicial de la interfaz web con estilos estables básicos construidos de cero.

| Tarea | Etiquetas | Prioridad | Tamaño | Estimación |
| :--- | :--- | :--- | :--- | :--- |
| Configurar e inicializar repositorio y Github Projects | `Documentacion`, `Codigo` | P0 | XS | 2 horas |
| Investigación sobre configuraciones de Django y su ORM | `Investigacion` | P0 | M | 5 horas |
| Diseñar la arquitectura técnica de clases, base de datos y mockups | `Diseño` | P1 | M | 5 horas |
| Creación de modelos de BBDD en Django y migraciones (Personaje, etc) | `Codigo` | P0 | M | 5 horas |
| Maquetación base global en HTML y CSS puro | `Diseño`, `Codigo` | P1 | M | 6 horas |
| Desarrollo de la suite de tests unitarios iniciales para los modelos | `tests` | P0 | S | 3 horas |
| Configurar GitHub Actions (Integración para correr tests automatizados) | `Codigo` | P0 | S | 4 horas |
| **Total Sprint 1** | | | | **30 horas** |

---

### Sprint 2: Lógica Base CRUD, Combates y Entrenamientos (30 Horas)

**Objetivo del Sprint**: Integración de los flujos del héroe: la habilidad para crear sus datos, su interacción en combates funcionales procesados eficientemente y subida de exp/niveles, plasmados estéticamente sin frameworks adicionales.

| Tarea | Etiquetas | Prioridad | Tamaño | Estimación |
| :--- | :--- | :--- | :--- | :--- |
| Vistas y lógica para crear un personaje (Tipos y Atributos) | `Codigo` | P0 | S | 4 horas |
| Vistas y lógica de lista personajes e interfaz responsive | `Diseño`, `Codigo` | P1 | M | 5 horas |
| Funcionalidad y lógica para entrenar al personaje (subir nivel) | `Codigo` | P0 | S | 4 horas |
| Funcionalidad para eliminar un personaje | `Codigo` | P2 | XS | 2 horas |
| Algoritmo simulador de combate entre dos personajes y guardado | `Codigo` | P0 | L | 7 horas |
| Renderizado HTML visual del combate con animaciones/estilos CSS puros | `Diseño`, `Codigo` | P1 | S | 4 horas |
| Pruebas unitarias de las funcionalidades de combate y acciones CRUD | `tests` | P0 | S | 4 horas |
| **Total Sprint 2** | | | | **30 horas** |

---

### Sprint 3: Dashboard, Refinamiento e Implantación de Entornos (30 Horas)

**Objetivo del Sprint**: Incorporación de estadísticas completas representadas de forma atractiva con Plotly, solución a errores finales detectados, y automatización al 100% de los entornos de Pruebas y Producción mediante flujos CI/CD respaldados en los tests requeridos.

| Tarea | Etiquetas | Prioridad | Tamaño | Estimación |
| :--- | :--- | :--- | :--- | :--- |
| Investigar integración del framework Plotly con Django | `Investigacion` | P1 | XS | 2 horas |
| Consultar y formatear métricas estadísticas desde el ORM de Django | `Codigo` | P1 | M | 5 horas |
| Generación de gráficos (Dashboard interactivo de Plotly) | `Codigo`, `Diseño` | P1 | L | 8 horas |
| Estilizado general del Dashboard y ajustes resolutivos (CSS Puro) | `Diseño` | P1 | M | 5 horas |
| Solución de bugs derivados de pruebas manuales y revisiones | `Bug` | P0 | S | 3 horas |
| CI/CD: Extender Actions para despliegue automatizado a Testing y Prod | `Codigo` | P0 | M | 5 horas |
| Documentación sobre uso de la app y resumen de proyecto para entrega | `Documentacion` | P2 | XS | 2 horas |
| **Total Sprint 3** | | | | **30 horas** |

---

## 4. Requisitos del Pipeline de CI/CD (GitHub Actions)

Dado que es **imperativo** respaldar los despliegues de la aplicación mediante la superación de tests y poder desplegar de forma segura en distintos entornos, se define el siguiente pipeline detallado para GitHub Actions:

1. **Continuous Integration (CI):**
   - Cada Pull Request o Push hacia una rama de integración (`develop` o `main`) lanzará un Workflow automático que construirá el entorno en servidor aislado.
   - Ejecutará toda la suite de `tests` (unitarios). Si algún test falla, Action marcará el build en estado rojo e imposibilitará el *merge*/cambio previniendo roturas en los entornos destino.

2. **Continuous Deployment (CD) - Entorno de Pruebas (Staging):**
   - Una vez los tests pasen exitosamente y se integre el código en una rama dedicada a pruebas, se lanzará un step de despliegue sobre el servidor de Testing. Aquí el equipo de desarrollo y el cliente pueden observar las integraciones.

3. **Continuous Deployment (CD) - Entorno Productivo:**
   - Exclusivamente cuando la rama `main` sea actualizada (tras validar su paso por el entorno de prueba y habiendo superado nuevamente los pipelines de tests exigidos), se procederá al despliegue transparente en el entorno productivo final, haciéndolo público y entregable.
