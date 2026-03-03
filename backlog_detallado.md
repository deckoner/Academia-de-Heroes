# Backlog Detallado y Atómico: Academia de Héroes (Refactorización a Django)

Este documento desglosa el proyecto en tareas granulares, adaptando el código base existente (CLI puro con SQLite) hacia una arquitectura web con el framework Django, manteniendo las prioridades de CI temprano y testing continuo.

## Sprint 1: Setup, Modelado Funcional y Migración del CRUD (30h)

*Objetivo: Migrar la lógica base y los modelos del CLI a la arquitectura ORM/MTV de Django, construyendo la primera capa de interfaz visual en HTML/CSS.*

| Tarea | Etiqueta | Prioridad | Tamaño | Est. (h) | Descripción |
| :--- | :--- | :--- | :--- | :--- | :--- |
| S1.1: Inicialización de Proyecto Django | `Codigo` | P0 | S | 3 | Crear el proyecto Django, configuración base de apps y estructura de carpetas (separándose de `main.py`). |
| S1.2: Refactorización a Modelos ORM | `Codigo` | P0 | M | 6 | Mapear las clases base (`Personaje`, `Guerrero`, `Mago`, `Arquero`) y el código de `db/` y `repository/` hacia modelos de Django ORM con migraciones. |
| S1.3: Migrar Lógica de Creación (Vistas y Formularios) | `Codigo` | P0 | M | 5 | Transformar la función interactiva `crear_personaje()` de consola en una vista Django (View) con su propio Template HTML (`ModelForm`). |
| S1.4: Migrar Lógica de Listado y Borrado | `Codigo` | P1 | M | 5 | Transformar `listar_personajes()` y `eliminar_personaje()` en vistas basadas en clases/funciones con HTML y ruteo dinámico. |
| S1.5: UI: Maquetación Base Global (CSS Puro) | `Diseño` | P0 | M | 6 | Diseñar e implementar layout base, sistema de grid, navegación y paleta de colores nativa sin frameworks. |
| S1.6: Adaptación de Tests Unitarios (Modelos y Vistas) | `tests` | P0 | M | 5 | Refactorizar los tests existentes para emplear `django.test.TestCase` validando el nuevo acceso a BBDD. |

## Sprint 2: Motor de Combate Web, Entrenamiento y Pipeline CI (30h)

*Objetivo: Llevar la interactividad compleja de las batallas mostradas en consola hacia peticiones web de Django y disponer del entorno preparado para Integración Continua.*

| Tarea | Etiqueta | Prioridad | Tamaño | Est. (h) | Descripción |
| :--- | :--- | :--- | :--- | :--- | :--- |
| S2.1: Lógica Backend del Simulador de Combates | `Codigo` | P0 | L | 7 | Refactorizar la función secuencial `simular_combate()` de `main.py` para operar sobre peticiones HTTP y recolectar logs de turnos de Django. |
| S2.2: Renderizado Visual del Combate (UI/UX) | `Diseño` | P1 | M | 6 | Construcción de plantillas HTML y animaciones CSS exclusivas para la vista de combate (despliegue de turnos y daño). |
| S2.3: Vista de Entrenamiento del Personaje | `Codigo` | P1 | S | 4 | Sustituir el flujo `entrenar_personaje()` del CLI por una acción rápida (`POST`) en la vista de lista de personajes. |
| S2.4: Pruebas de Integración Web | `tests` | P0 | M | 5 | Escribir tests del cliente de pruebas de Django simulando la secuencia entera de un combate y entrenamiento. |
| S2.5: Configuración de GitHub Actions (CI) | `Investigacion` | P0 | M | 5 | Setup del workflow de Github Actions para ejecutar los tests de Django en cada commit/PR automáticamente. |
| S2.6: Refinamiento de Estilos en Formularios | `Diseño` | P2 | S | 3 | Perfeccionamiento visual y responsive design en el listado y paneles informativos usando CSS purista. |

## Sprint 3: Visualización de Datos, QA y CD (30h)

*Objetivo: Integrar gráficos métricos solicitados utilizando la información recolectada, limpiar deficiencias técnicas y automatizar el despliegue al cliente final.*

| Tarea | Etiqueta | Prioridad | Tamaño | Est. (h) | Descripción |
| :--- | :--- | :--- | :--- | :--- | :--- |
| S3.1: Consultas de Agregación (ORM) para el Dashboard | `Codigo` | P1 | M | 6 | Traducir requisitos de consultas analíticas (horas de uso, héroe más fuerte, atributos ganadores) al lenguaje de Django ORM. |
| S3.2: Integración de Plotly en Django | `Investigacion` | P1 | S | 4 | Investigar la inyección de gráficos generados en el Server-Side (Python/Plotly) hacia plantillas visuales en el front-end. |
| S3.3: UI: Construcción del Dashboard Estadístico | `Diseño` | P1 | M | 6 | Ensamblaje de las gráficas Plotly en un grid de interfaz limpio e interactivo para que el usuario consulte las estadísticas. |
| S3.4: Bug Fixing General y Cierre de Interfaz | `Bug` | P0 | M | 5 | Pruebas manuales transversales corrigiendo flujos rotos, problemas de renderizado de CSS y enlaces de Django caídos. |
| S3.5: Pipeline de Despliegue CI/CD a Entornos (Staging/Prod) | `Codigo` | P0 | L | 7 | Expansión de GH Actions añadiendo steps condicionales para el CD, realizando despliegues automáticos a los servidores. |
| S3.6: Redacción de Documentación Técnica de la Migración | `Documentacion` | P2 | S | 2 | Completar `README.md` detallando la nueva manera de ejecutar Django y correr las migraciones comparado al setup viejo. |

---
**Total Proyecto: 90 horas**
**Dedicación: 15h/semana (Total de 6 semanas)**
