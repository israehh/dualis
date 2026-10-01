# DUALIS — Estado Global F35

**Fecha de auditoría:** 2026-10-01  
**Estado:** F35 — auditoría y fotografía del estado global. Solo documentación; no introduce cambios de juego.

## 1. Resumen ejecutivo

DUALIS es un juego de exploración y resolución de patrones para UNO y DOS. La simulación es cartesiana; la proyección isométrica solo presenta el mundo. El progreso se expresa mediante cooperación y el lenguaje existente: OBSERVE, TRANSFORM, MOUNT y LINK.

La filosofía vigente desde F28 es que los JSON describen la historia registrada de las salas. Las brechas del grafo jugable se corrigen con overlays en memoria en `src/dualis/world/campaign.py`; no se reescriben los blueprints congelados. F34 cerró la continuidad R5 entre R5_04 y R5_05. La ruta principal es continua desde ROOM_SLICE hasta R5_EXAM.

La suite actual tiene **314 tests aprobados**. R1–R5 están implementadas; R5_EXAM es el terminal actual de la campaña. R6 y el Núcleo todavía no están implementados.

## 2. Estadísticas

| Área | Rooms de campaña |
|---|---:|
| ROOM_SLICE | 1 |
| R1 — Vestíbulo | 14 |
| R2 — Biblioteca | 8 |
| R3 — Taller de los Ecos | 9 |
| R4 — Jardín Invertido, incluido R4_EXAM | 9 |
| R5 — Torre de los Nombres, incluido R5_EXAM | 9 |
| **Total de campaña** | **50** |

Hay **2 exámenes**: R4_EXAM y R5_EXAM. Hay **6 aristas de overlay** activas y **8 requisitos LINK** registrados. La suite contiene **314 tests**, todos aprobados en la validación F35.

Como distinción de inventario: existen 69 definiciones JSON de salas distribuidas entre `data/rooms/` (3), `data/blueprints/` (44), `data/link_rooms/` (4), `data/r4_rooms/` (9) y `data/r5_rooms/` (9). De esas 69, 50 forman la campaña principal; el resto son salas auxiliares o aisladas de prueba. Las 44 entradas de `data/blueprints/` permanecen congeladas.

## 3. Cadena principal completa

La cadena lineal de avance es:

`ROOM_SLICE → VEST_01 → … → VEST_14 → BIB_01 → … → BIB_08 → TAL_01 → … → TAL_09 → R4_01 → … → R4_08 → R4_EXAM → R5_01 → … → R5_08 → R5_EXAM`

En total son 50 nodos. La integración de la cadena depende de seis enlaces de campaña en memoria; las conexiones internas que ya están declaradas en los datos permanecen sin cambios.

## 4. Exámenes existentes

- **R4_EXAM — Jardín Invertido:** combina OBSERVE, TRANSFORM y MOUNT con una salida que exige LINK en TENSION. Al completarse, su estado permanece COMPLETED mientras el dúo se separa para abrir la salida.
- **R5_EXAM — Torre de los Nombres:** reutiliza los verbos y el ExamRuntime existente; combina observación, transformación, montaje y TENSION. No introduce una idea o runtime nuevo y es el terminal actual.

## 5. Overlays de campaña activos

`with_integration()` copia el mapa recibido y sustituye las listas de enlaces únicamente para las rooms enumeradas. La entrada original no se muta.

| Origen | Destino añadido | Fase / función |
|---|---|---|
| TAL_09 | R4_01 | F28: bisagra R3→R4 |
| R4_04 | R4_05 | F28: continuidad interna R4 |
| R4_08 | R4_EXAM | F28: acceso al examen R4 |
| R4_EXAM | R5_01 | F33: bisagra R4→R5 |
| R5_08 | R5_EXAM | F33: acceso al examen R5 |
| R5_04 | R5_05 | F34: continuidad interna R5 |

Los enlaces originales de estas rooms permanecen en sus JSON; el overlay es el mapa de navegación efectivo de campaña.

## 6. Gates LINK existentes

`src/dualis/world/link_gate.py` declara ocho requisitos. LIMIT nunca abre una salida.

| Room | Estado requerido |
|---|---|
| LNK_01 | CONNECTED |
| LNK_02 | TENSION |
| LNK_03 | CONNECTED |
| LNK_04 | CONNECTED |
| R4_05 | TENSION |
| R4_EXAM | TENSION |
| R5_04 | TENSION |
| R5_EXAM | TENSION |

El gate es un predicado que lee el estado del vínculo y el estado del runtime; no mueve actores ni implementa una mecánica nueva.

## 7. Sistemas implementados

- **Core:** bus de eventos, loop de paso fijo, escenas y gestión de estado.
- **Lenguaje y cooperación:** LINK, observación, transformación, cooperación y montaje de UNO sobre DOS.
- **Puzzles y runtimes existentes:** SlicePuzzle, registro de transformables/observables y runtimes para OBSERVE_TO_CROSS, HEIGHT, TRANSFORM_TO_REACH, TIMED_WINDOW, SHARED_PASSAGE y exámenes.
- **Mundo:** carga y validación de blueprints, construcción de salas, entidades, tránsito automático, entrada determinista, colisiones y puertas LINK.
- **Campaña:** overlay de enlaces en memoria mediante `with_integration()`.
- **Presentación:** renderer 2D e isométrico, proyección, viewport, elevación visual, tiles y sprites. La elevación no altera la simulación.
- **Persistencia suave:** conserva la sala actual y la sala anterior; el progreso global de runtimes no se serializa.

## 8. Funcionalidades aún no implementadas

- R6 — Archivo de lo que no fue.
- Núcleo y examen final de campaña.
- Atajo DOOR TO BEFORE para retorno rápido tras hitos.
- Hub global.
- Muerte suave y reaparición.
- Persistencia completa del progreso de puzzles/runtimes.

World_z jugable, gravedad, saltos, combate, inventario y pathfinding obligatorio no son pendientes implícitos: están fuera de las restricciones actuales de diseño.

## 9. Riesgos abiertos

- **Retorno desde R5_EXAM:** la ruta de avance termina correctamente en el examen. Sin embargo, el tránsito automático al entrar desde R5_08 no ofrece retorno: `next_room` recibe R5_08 como origen y el examen tiene un único enlace a esa misma sala. Esto queda fuera de F34 y requiere una fase que pueda revisar el comportamiento de tránsito si se quiere resolver.
- **Documentación de continuidad desactualizada:** `DUALIS_CONTEXT.md` conserva cifras anteriores (265 tests), presenta R5 como siguiente fase y describe el cierre F28, no el estado F34. Debe leerse como historial de continuidad, no como inventario actualizado a F35.
- **Requisitos LINK y geometría:** las puertas que requieren TENSION dependen de que la salida permita colocar al dúo en ese estado. Cambios futuros deben validar conjuntamente gate y geometría.
- **Cobertura de reglas frente a experiencia:** los tests verifican contratos y recorridos; no sustituyen playtests de legibilidad y ritmo de las habitaciones.
- **Advertencias de pytest:** la suite informa 24 advertencias de colección por clases auxiliares con constructor, aunque los 314 tests pasan.
- **Sin Git:** el workspace no tiene historial de control de versiones, lo que dificulta recuperar estados previos y auditar cambios.

## 10. Preparación para R6

R5_EXAM es el extremo previsto para extender la columna vertebral a R6, sin insertar regiones entre R1–R5. La arquitectura ya establece el patrón: rooms futuras en un directorio aislado, carga explícita de blueprints y una nueva arista de integración en `campaign.py`; los datos congelados se mantienen como historia.

R6 debe reutilizar OBSERVE, TRANSFORM, MOUNT y LINK para reinterpretar patrones existentes. No debe añadir verbos ni mecánicas, reabrir regiones intermedias ni convertir el Núcleo en una región con ideas nuevas. La continuidad de retorno desde R5_EXAM y el DOOR TO BEFORE siguen siendo decisiones pendientes antes de asumir que el backtracking está resuelto.
