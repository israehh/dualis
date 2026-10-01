# DUALIS DEVLOG
Bitácora de Diseño y Desarrollo

Versión: 1.0

Este documento registra decisiones importantes del proyecto.

No es documentación técnica.

No es canon.

No sustituye DUALIS_CONTEXT.md.

Su objetivo es conservar el razonamiento detrás de las decisiones para evitar perder el rumbo del proyecto.

---

# ORIGEN

DUALIS nace como una reinterpretación moderna del espíritu de Head Over Heels.

La intención nunca fue crear un clon.

El objetivo es construir un juego basado en:

- observación
- cooperación
- lenguaje visual
- resolución de patrones

usando una identidad propia.

---

# REFERENCIAS PRINCIPALES

Referencias estructurales:

- OpenHoH
- Head Over Heels (RetroRemakes)

Se utilizan para estudiar:

- estructura de habitaciones
- progresión
- organización del mundo
- ritmo de puzzles

No se copian:

- mapas
- personajes
- objetos
- habilidades
- lore

---

# FILOSOFÍA

DUALIS no busca dificultad extrema.

Busca comprensión.

El jugador debe sentir:

"Ahora entiendo."

más que:

"Por fin lo conseguí."

---

# LOS DOS PERSONAJES

UNO y DOS son un sistema.

No son dos campañas.

No son dos héroes independientes.

El núcleo del juego es el vínculo.

La pregunta principal de DUALIS es:

¿Cómo cooperan dos entidades para comprender un sistema?

---

# EL LENGUAJE

Actualmente el lenguaje base es:

OBSERVE
TRANSFORM
MOUNT
LINK

Todo contenido futuro debe derivar de estos verbos.

---

# EVOLUCIÓN DEL PROYECTO

## F17

Nacimiento de la representación isométrica.

Primer paso para abandonar la vista abstracta.

---

## F18

Capas visuales.

Ground
Actors
Effects
UI

La lógica permanece cartesiana.

---

## F19

Ambientación regional.

Las regiones empiezan a tener identidad visual.

---

## F20

Elevación visual.

El mundo adquiere volumen.

Importante:

sin world_z jugable.

---

## F21

Consolidación estética.

Objetos regionales.

Lectura visual más clara.

---

## F22

Mundo sólido.

Los personajes dejan de atravesar decorados.

Nacen las colisiones reales.

---

## F23

El vínculo existe.

CONNECTED
TENSION
LIMIT

dejaron de ser colores.

Pasaron a ser lenguaje jugable.

### Objetivo

Convertir LINK en una condición jugable real usando exclusivamente
link.distance, link.state y los estados ya existentes, sin mecánicas,
teclas, acciones ni sistemas nuevos.

### Decisiones

- Cuatro rooms nuevas de prueba, cada una con una sola idea:
  LNK_01 (salida exige CONNECTED), LNK_02 (salida ancha que exige
  TENSION), LNK_03 (LIMIT rechaza, se completa al volver),
  LNK_04 (ROOM_DENIED correcto antes de la quietud).
- Predicado puro world/link_gate.py en world/, no en systems/:
  no es un sistema, no mueve, no emite, no renderiza.
- El jugador lee la solución con lo que ya existe: posición de UNO,
  posición de DOS, línea de vínculo y HUD actual. Cero indicadores.
- Las rooms viven en data/link_rooms/, no en data/blueprints/.

### Problemas encontrados

- Una salida pequeña exige CONNECTED por geometría (TENSION no cabe
  dentro), pero exigir TENSION pedía una puerta lógica: la geometría
  sola solo permite, no exige. De ahí el gate + la salida ancha.
- Añadir blueprints a data/blueprints/ rompía
  test_todos_los_blueprints_cargan (44 exactos). Las rooms de prueba
  quedaron aisladas en su propia carpeta: cero impacto en la suite.

### Consecuencias para diseño futuro

- El vínculo ya puede sustituir a llaves, habilidades e inventario
  como condición de resolución (world plan §12).
- Toda región futura puede declarar requisitos CONNECTED/TENSION
  sin tocar sistemas: el patrón es datos + predicado + tests.

---

## F24

Tránsitos y persistencia suave.

La cadena R1→R2→R3 dejó de ser una lista de salas.

Pasó a ser un mundo navegable.

### Objetivo

Cruzar salidas COMPLETED con el dúo dentro para cambiar de sala sin
teclas debug, entrar de forma coherente según el enlace, mantener el
vínculo UNO/DOS, persistir la room actual de forma mínima y permitir
reset local sin reinicio global. Sin savegames complejos, teleports,
hubs, inventario, acciones, IA ni world_z.

### Decisiones

- Tránsito automático solo a enlaces declarados, con memoria de
  dirección (bidireccional; TAL_09 = quedarse). ROOM_SLICE resuelto
  lleva a VEST_01. Evento ROOM_TRANSIT para observarlo.
- Entrada determinista por (destino, origen): pares fijos filtrados
  contra salida y sólidos. El spawn histórico (120,280) caía dentro
  de la salida en 8 rooms (entre ellas TAL_01): medir antes de
  suponer.
- Persistencia mínima real: saves/soft.json guarda solo {room, prev}.
  El progreso vive en los runtimes, no en el fichero; fichero roto =
  ROOM_SLICE.
- Reset local = foto vars() de los actores al cargar, restaurada al
  entrar. Cableado solo en main.py; systems/, render y colliders
  intactos.

### Problemas encontrados

- Ningún par de entrada sirve para todas las rooms si no se filtra:
  la solución fue medir los 5 pares candidatos en las 31 rooms +
  slice y elegir por descarte, no por convención.
- La "muerte suave / reaparición" de la antigua propuesta F23 no se
  implementó en F23 ni en F24: queda como idea pendiente con fase
  propia si se retoma.

### Consecuencias para diseño futuro

- El jugador ya puede llegar a pie hasta TAL_09: la precondición de
  R4 está cumplida.
- DOOR TO BEFORE (world plan §14) sigue pendiente como atajo
  diseñado; el tránsito bidireccional actual evita backtracking
  forzado pero no es el retorno rápido tras hito.
- Regla confirmada: primero regiones, después atajos. No hay hub
  hasta que existan regiones que lo justifiquen.

---

# REGIONES

## R1 — El Vestíbulo

Aprender.

Introducción al lenguaje.

Piedra.

---

## R2 — Biblioteca

Interpretar.

Variaciones funcionales.

Papel.

---

## R3 — Taller de los Ecos

Combinar.

Síntesis.

Cobre.

---

# VISIÓN ARTÍSTICA

La inspiración buscada no es realismo.

Se persigue:

- atmósfera
- identidad
- misterio
- coherencia

La referencia visual ideal es un mundo que parezca vivo aunque esté construido con medios modestos.

---

# SOBRE HEAD OVER HEELS

Head Over Heels es una referencia de diseño.

No una plantilla.

La pregunta correcta nunca es:

"¿Qué hacía HoH?"

La pregunta correcta es:

"¿Por qué funcionaba?"

y después:

"¿Cómo se expresa esa idea en DUALIS?"

---

# REGLA DE ORO

No perseguir gráficos.

No perseguir tecnología.

No perseguir cantidad.

Primero:

comprensión.

Después:

mundo.

Finalmente:

belleza.

---

# ESTADO ACTUAL

El proyecto ya no se considera un experimento técnico.

Se considera la construcción de un mundo.

R1-R2-R3 constituyen el Acto I completo y navegable a pie
(F24: tránsitos automáticos + persistencia suave).

El vínculo es condición jugable verificada (F23).

Las futuras expansiones partirán desde TAL_09.

---

# PRÓXIMOS GRANDES HITOS

F24
Tránsitos y persistencia suave: completada.

R4
Jardín Invertido: siguiente fase recomendada.

R4
Jardín Invertido.

R5
Torre de los Nombres.

R6
Archivo de lo que no fue.

NÚCLEO
Examen final.

---

# RECORDATORIO

Las mejores decisiones del proyecto hasta ahora han sido aquellas que:

- añadían lenguaje
- reducían complejidad
- aumentaban claridad

Toda futura decisión debería medirse con el mismo criterio.