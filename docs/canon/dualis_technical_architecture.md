# DUALIS — Arquitectura Técnica

**Versión:** 1.0 — Propuesta moderna
**Stack:** Python 3.11+ + pygame-ce 2.5+
**Estado:** Solo documentación. No escribir código. No crear archivos fuente.
**Depende de:** `docs/dualis_design_bible.md` (visión vinculante) y lecciones técnicas de `references/Head-Over-Heels` (Filmation II) y `references/HeadOverHeels_CPC`. Nada de código, assets o lore se copia de esas referencias.

---

## 1. Objetivos y restricciones

### 1.1 Objetivos

1. Sostener la biblia con tecnología mínima y legible: dos agentes vinculados, rooms cerradas isométricas, poderes cognitivos (Observar, Transformar, Marca temporal), 7 regiones, muerte barata.
2. Lógica determinista a paso fijo desacoplada del render, testeable sin ventana.
3. Datos por delante del código: rooms, objetos y comportamientos como datos versionables, no como `if` desperdigados.
4. Rendimiento sobrado en hardware modesto (60 fps con cientos de sprites pintados a mano) sin motor 3D.
5. Herramientas de autoría y verificación desde el día uno: visor de rooms, validador de grafo, tests de física.

### 1.2 Restricciones

- Solo `pygame-ce`, stdlib y Pillow (herramientas). Sin numpy / motores / ECS externos en v1. Si hace falta, se justifica contra esta arquitectura.
- Python puro para lógica; nada de extensiones nativas en v1.
- Sin red, sin 3D, sin shaders. Todo 2D por composición.
- Estructura de proyecto propuesta (no crear aún):

```
src/dualis/
  config.py    # constantes, paletas por región, timing — sin pygame
  iso.py       # matemática isométrica pura — sin pygame
  world.py     # datos: Room, GameObject, load_room — sin pygame
  physics.py   # gravedad + colisiones AABB 3D — sin pygame
  behaviours.py# registro dispatch de tipos + Ecos/Bibliotecarios/etc — sin pygame
  duo.py       # vínculo Uno-Dos, Observar, Transformar, Marca — sin pygame
  game.py      # bucle paso fijo + input a ejes de mundo
  render.py    # único módulo que conoce pygame (pintor + cámara)
  audio.py     # efectos y música por prioridades
  save.py      # persistencia JSON + “la estación recuerda”
  rooms/*.json # rooms como datos
tests/test_*.py# asserts planos, sin ventana
tools/         # visor, validador, contact sheet
```

Esta separación replica la lección del scaffold `reimpl/` de la referencia (matemática ↔ datos ↔ render ↔ control) y permite el enfoque “oráculo determinista”: simular ticks sin abrir ventana.

---

## 2. Lecciones de Head Over Heels que se adoptan (y cómo se modernizan)

| HoH original (referencia) | Lección | DUALIS moderno |
|---|---|---|
| Bucle 50 Hz: leer input → actualizar objetos → proyectar → componer en buffer → volcar rect sucio. IRQ + `v_sync_ctr`. | Paso fijo. Lógica separada de fps. | Bucle paso fijo **50 Hz lógica**, render a fps libre con interpolación opcional o step-lock. `game.py` acumula dt y ejecuta ticks enteros. Nunca lógica atada a `clock.get_fps()`. |
| `project_iso &A231`: `col=(X−Y)+128`, `row=2Z−(X+Y)+127`. 2:1 dimetric, 7 ALU ops, sin MUL/DIV. | Proyección entera barata, unidireccional (nunca pantalla→mundo para lógica). | `iso.py::project(x,y,z)` en coma flotante o enteros de mundo (a elegir, ver §4), misma fórmula reescalada a píxeles. Lógica siempre en mundo 3D; proyección solo render. Picking por intersección de rayo si se necesita editor, nunca en gameplay. |
| `render_room &93B0` recorre lista `&AF80` atrás→adelante; 12 variantes de blit enmascarado; buffer `&B800` + flush rect sucio `&93E8`. | Pintor + composición con máscara + dirty-rect. | Pintor por `depth_key = x+y+z` (o variante con altura), sprites con alfa pre-multiplicada, composición en `Surface` de room + dirty-rects por defecto de pygame-ce. En hardware moderno, redibujo completo a 60 fps también viable; dirty-rect como optimización, no como corrección de flicker. |
| Colisión objeto-vs-objeto, sin tilemap. Bloques actor 18 bytes stride `&12`, `X/Y/Z` en `+5/+6/+7`, dispatch por tipo 1–37 vía tablas `&83BC/&8406`. | Mundo de cubos + dispatch tabular extensible. | Colisión **AABB 3D objeto-vs-objeto** en `physics.py`, sin grid de colisión global. Registro `REGISTRY` tipo→comportamiento (`behaviours.py`), añadir tipo = una clase, sin tocar bucle. |
| Rooms bit-packed en `&5B00–&702F`, 301 rooms en 2 directorios, decode `room_decode &780E` + macros `≥&C0` recursivas. | Rooms como datos compactos + grupos compartidos. | Rooms como **JSON legible** en v1 (ver §6), con macros/grupos (`defs/`) equivalentes a códigos `≥&C0`. Compresión/binario solo si el corpus crece (>500 rooms) y siempre con round-trip verificado. |
| Input mapea a ejes de mundo (diagonales en pantalla). Física (gravedad, salto, glide) corre sobre `X/Y/Z`. | Control en mundo, no en pantalla. | Igual: teclas → vectores de mundo; cámara isométrica solo visual. Evita ambigüedad de profundidad en lógica. |
| Sonido beeper/AY por prioridades, `sound &9675/music &964F`. | Audio por prioridad, no polifonía ingenua. | `audio.py` con canales y prioridades (UI < ambiente < evento < Uno/Dos < aviso vínculo). Congelar tiempo filtra/atenúa, no silencia de golpe. |
| Verificación byte-exacta (`make verify`, SHA-256) y emulador para probar rutinas. | Verdad ejecutable. | Tests deterministas + `verify_roundtrip` de rooms (JSON→mundo→JSON idéntico) + golden images de proyección. |

Lo que **no** se hereda: vidas BCD, bolsa con agujeros, teletransportadores arbitrarios, interruptor remoto ciego, tablas Z80, memoria paginada, font residente. Ver biblia §8.

---

## 3. Bucle principal y timing

### 3.1 Paso fijo 50 Hz

- `TICK = 1/50 s`. Acumulador en `game.py`. Máximo 5 ticks por frame para evitar espiral; si se supera, se dropea tiempo (slow-mo suave, nunca cascada).
- Orden por tick (herencia `main_update_chain &706B`):

```
leer input → duo (vínculo, poderes) → behaviours (cada objeto) → física (mover+colidir)
→ eventos/muertes baratas → аудио cues → marcar dirty
```

- Render lee estado interpolado o último tick; nunca muta mundo.
- Pausa y Observar (congelar 2 s = 100 ticks) se implementan como escalado de `dt_mundo = 0` manteniendo `dt_ui` vivo para planificar cámara. No es `sleep`; es bandera de simulación.

### 3.2 Estados globales mínimos

Inspirado en `v_game_mode &B218`, pero legible: `PLAY | FREEZE_OBSERVE | ROOM_ENTER | ROOM_EXIT | DEATH_SOFT | CHOICE_FINAL`. Nada de modales anidados. `ROOM_ENTER` ejecuta decode + fundido + `attr`/paleta regional; `DEATH_SOFT` respawnea en entrada de room sin contador de vidas y notifica a `save.py` (“la estación recuerda”).

---

## 4. Mundo, coordenadas y proyección

### 4.1 Unidades

- Unidad lógica = celda (ej.: 1 celda = 32×16 px en pantalla para tile base 2:1, altura 1 nivel = 24 px — a tunear con arte pintado, no al revés).
- Posiciones en coma flotante para Dos (inercia) y Uno (arco), pero colisión con AABB y resolución a epsilon fijo para determinismo. Semilla RNG por room para Ecos/patrullas, serializable.
- `Z` = altura. Techo por room (`Z_max`, equivalente a `cp &84`). Soporte = max Z bajo pies (`v_support_z` moderno).

### 4.2 Proyección (pura, sin pygame)

```text
# iso.py — especificación, no código
col = (x - y) * TILE_W/2 + origin_x
row = (x + y) * TILE_H/2 - z * LIFT + origin_y
depth_key = x + y + z * K   # K ~ 1.2–2 para que altura ocluya bien
```

- `TILE_W: TILE_H = 2:1` (26.565°, `atan(1/2)`), bordes nítidos sin antialiasing agresivo.
- Origen por room centrado + cámara con lerp y clamp a diamante. Sin rotación: el ángulo es fijo, por eso los sprites nunca rotan (lección Filmation).
- Inversa solo para editor (`unproject_floor` con `z=0` + test de altura front-to-back). Gameplay nunca la usa.

### 4.3 Profundidad y composición

- Orden pintor: `sorted(objetos, key=depth_key)` far→near cada frame o al invalidarse (lista casi ordenada; insertion sort suficiente).
- Cada sprite = par (color, máscara/alfa) preprocesado al cargar región. Composición `(bg AND mask) OR gfx` clásica se traduce a `blit` con alfa + `colorkey` según asset; sin rotación/escalado en runtime (variantes pre-escaladas si hace falta).
- Paredes vecinas y merge de puertas (lección `build_room_frame &84E4` + `room_load_neighbor &77E0`): al entrar se componen muros decorados + suelo diamante completo, no fragmentos. Validador exige suelo conexo y salidas declaradas.

---

## 5. Física y colisiones

### 5.1 Modelo

- Cuerpos = AABB 3D alineados a ejes (`pos + size`). Sin mallas, sin motores físicos.
- Gravedad por tick, salto de Uno con velocidad inicial + corte al soltar (arco controlable), carrera de Dos con aceleración/fricción y energía cinética = `|v|²` para embestidas.
- Soporte: escanear AABBs bajo pies → `support_z`; si `z > support_z` → caer; si `z == support_z` → apoyado; carry si soporte es plataforma móvil (herencia `carry-allowed` bit5).
- Techo, paredes y esquinas por proyección de AABB sobre ejes, resolución por eje mínimo (X→Y→Z), nunca teletransporte correctivo.

### 5.2 Objeto-vs-objeto

Sin tilemap de colisión. Cada tick: broadphase por solape de rangos en `x+y` (barato, mundo pequeño por room <200 objetos), narrowphase AABB 3D. Determinista, sin dependencias de frame.

Casos DUALIS:

- **Montar:** Dos es soporte dinámico; Uno hereda velocidad de Dos + offset.
- **Lanzar:** Dos imparte impulso balístico a Uno; Uno en vuelo es sensor que al impactar rebota o activa.
- **Puente humano:** ambos en pose → AABB temporal transitable 3 s (150 ticks).
- **Marca temporal:** plataforma efímera con TTL 3 s, colisionable solo por Uno/Dos según diseño.
- **Péndulo / sala giratoria / gravedad cambiante:** plataformas cinemáticas con velocidad conocida; el jugador hereda delta.

### 5.3 Muerte barata

`flag_kill` moderno = evento, no game over: disuelve agente(s), 60 ticks de fundido, respawn en puerta de entrada con vínculo restaurado, sin pérdida de comprensión. `save.py` registra contador por room para “recuerdo” (luz, eco visual), nunca para bloquear.

---

## 6. Datos de rooms

### 6.1 Formato v1: JSON legible

Una room = un archivo (o una entrada en atlas regional). Ejemplo de esquema (especificación, no archivo creado):

```text
{
  "id": "vestibulo_03",
  "region": "vestibulo",
  "size": {"w": 12, "d": 10, "h": 5},
  "palette": "gris_ambar",
  "spawns": {"uno": [2,2,0], "dos": [3,2,0]},
  "exits": [{"to": "vestibulo_04", "at": [11,5,0], "dir": "+x", "kind": "obvia"},
            {"to": "vestibulo_02s", "at": [0,8,1], "dir": "-x", "kind": "secreta"}],
  "objects": [
    {"type": "bloque", "pos": [5,5,0], "size": [1,1,1]},
    {"type": "pendulo", "pos": [6,5,2], "params": {"periodo": 100}},
    {"type": "marca_eco", "params": {"retardo": 250}}
  ],
  "macros": ["grupo_puerta_opinion_A"],
  "tags": ["ensena:montar", "foco:bloque_alto"]
}
```

- `defs/*.json` = grupos compartidos (equivalente moderno a macros `≥&C0`): puertas con opiniones, relojes, espejos. Reutilización sin duplicar.
- Validador obligatorio por room: legible (foco declarado), ≥2 salidas, resoluble con vínculo 10u, sin poder futuro, memoria (forma única hash visual aproximado), ritmo etiquetado.

### 6.2 Pipeline de autoría

`papel → JSON → visor (tools/viewer) → contact sheet (todas las rooms en rejilla, herencia `rooms_contact_sheet.png`/`world_map.png`) → playtest ciego`. Conversión binaria futura solo con `verify_roundtrip.sh` equivalente: `JSON → bin → JSON` idéntico + golden renders.

### 6.3 Grafo de mundo

Grafo dirigido de rooms + aristas de exits. Sin teletransportadores globales. Análisis estático: ¿hay bloqueo global? ¿toda room tiene ruta alternativa si se ignora su secreta? ¿qué conocimiento (no objeto) desbloquea cada región? Esto implementa biblia P6.

---

## 7. Comportamientos (dispatch tabular)

`behaviours.py::REGISTRY: tipo → clase` con hooks `update(obj, room, tick)` / `on_touch` / `on_activate`. Añadir tipo = una clase, como en `reimpl/objects.py` y tablas `&83BC`.

Tipos v1 mínimos:

- `bloque, plataforma, plataforma_temporal, pendulo, puerta_opinion, espejo, eco, reloj, agua, cinta, prensa, jardinero, bibliotecario, nominador, marca_temporal, puente_humano, interruptor_diegético, salida`.
- Enemigos-patrulla clásicos solo como `eco_patrulla` legible (ruta predecible, nunca daño injusto). Sin HP.

Cada comportamiento documenta: ¿enseña / desafía / recompensa / revela? Si ninguno, no se registra.

---

## 8. Dúo: vínculo y poderes (módulo `duo.py`)

- **Vínculo:** cada tick mide distancia euclídea en celdas entre Uno y Dos. >10u → rampa de viñeta + ralentí + drenaje estabilidad. Histeresis para no parpadear en el borde (entra a 10, sale a 9).
- **Observar (Uno):** congela `dt_mundo` 100 ticks, 1 uso por entrada a room (recargable al reentrar). UI permite mover cámara y ver sombras/patrones con highlight. No mueve agentes.
- **Transformar (Dos):** 1 uso por room. Tabla de reinterpretaciones por tipo (`silla→plataforma`, etc.). Irreversible en visita, reversible al reentrar. Requiere affordance visual + confirmación implícita (soltar junto a objeto elegible), nunca menú modal.
- **Marca temporal (Uno):** deja plataforma en ápice 150 ticks, cooldown por room. Solo transitable por el dúo.
- **Montar/Lanzar/Puente:** implementados como estados de `duo.py` + soporte de `physics.py`, no como scripts de room. Las rooms los invocan por geometría, no por trigger textual.

Input: un solo mando/teclado controla al activo; `Tab` o botón cambia activo; `mantener` invoca acción conjunta contextual (montar/lanzar/puente según proximidad y postura). Nada de combos oscuros.

---

## 9. Render (único módulo pygame)

- Capas: suelo diamante → muros/fondo → objetos far→near → Uno/Dos → FX (viñeta vínculo, eco fantasma, congelado) → UI mínima (sin texto tutorial; solo indicadores diegéticos de Transformar/Observar disponibles).
- Assets pintados a mano por región, atlas por región (herencia `gfx/` + `hoh_graphics.md` pero con arte original). Resolución base 1280×720, escalado entero opcional. Paleta limitada por región definida en `config.py`.
- Cámara fija por room con micro-lerp al dúo; sin scroll libre dentro de room (cada room es diorama). Transición entre rooms por disolvencia de glifo/dirty (homenaje `screen_flush_dissolve &9422`, reinterpretado).
- Texto casi ausente en gameplay; cuando exista (nombres en Torre), render de fuente propia, no importada. Efecto máquina de escribir + doble altura opcional como guiño, no como copia.

Performance: <500 blits/frame, surfaces convertidas, `DirtySprite` groups o redibujo completo (a 720p es trivial para pygame-ce). Presupuesto: lógica <6 ms, render <10 ms en portátil modesto.

---

## 10. Audio

- `audio.py`: mixer pygame-ce, bancos por región, prioridades (ambiente < evento < dúo < vínculo < reloj). Sin chiptune imitativo; diseño contemporáneo íntimo (mármol, papel mojado, metal, respiración).
- Sonido como información: rooms “el sonido es el mapa” exigen modo accesible visual alternativo (no excluir por audición). Subtítulos diegéticos opcionales de eventos, nunca tutoriales hablados.
- Observar atenúa mundo −12 dB + filtro; Transformar tiene firma por región; vínculo al límite late como pulso, no como alarma.

---

## 11. Persistencia y “la estación recuerda”

- `save.py`: JSON por slot + autosave por room. Guarda: room actual, posiciones, usos de Transformar/Observar consumidos en visita, contadores de visitas/muertes suaves por room, flags de comprensión (no de inventario), variante Archivo visitada.
- “Recuerda” = cambios cosméticos-narrativos (luz, objetos desplazados, ecos) derivados de contadores, nunca bloqueo ni castigo. Borrado total disponible (respeto al jugador).
- Formato versionado (`dualis_save_v1`), migración explícita si cambia esquema.

---

## 12. Testing y verificación

- `tests/test_iso.py`: proyección directa/inversa suelo + golden values de fórmula 2:1.
- `tests/test_physics.py`: caída, soporte, carry, techo, lanzamiento balístico — sin pygame, ticks simulados.
- `tests/test_duo.py`: vínculo 10u con histeresis, Observar congela mundo no UI, Transformar 1×/room.
- `tests/test_rooms.py`: valida todas las `rooms/*.json` (2 salidas, foco, resoluble con vínculo, sin poder futuro) + round-trip JSON→mundo→JSON.
- `tools/validate.py`, `tools/viewer.py`, `tools/contact_sheet.py`: visor y sábana de rooms para memoria visual (herencia `world_map.py`, `room_map.py`).
- Playtest ciego como test de aceptación biblia §10: sin explicación, ¿entiende vínculo? ¿recuerda rooms al día siguiente?

---

## 13. Roadmap técnico (sin código aún)

- **M0 Bucle:** `game.py` paso fijo 50 Hz + ventana + input a ejes mundo. Criterio: cubo se mueve en diagonal correcta.
- **M1 Iso:** `iso.py` + `render.py` pintor con cubos placeholder. Criterio: diamante nítido, oclusión correcta.
- **M2 Datos:** `world.py` + 3 rooms JSON + validador. Criterio: carga, 2 salidas, contact sheet.
- **M3 Física:** `physics.py` AABB + salto/carrera + soporte/carry. Criterio: tests en verde sin ventana.
- **M4 Dúo:** `duo.py` vínculo + montar/lanzar + Observar/Transformar/Marca. Criterio: room “montar” resoluble sin texto.
- **M5 Behaviours:** puertas con opiniones, ecos, relojes, espejos. Criterio: 5 rooms arquetipo jugables.
- **M6 Vestíbulo:** 8–12 rooms + recuerdo + audio base. Criterio: playtest ciego entiende vínculo.
- **M7 Regiones:** Biblioteca + Taller con paletas y macros. Criterio: grafo sin bloqueo global.
- **M8 Pulido:** transiciones, viñeta, saves, herramientas. Criterio: 60 fps + validación total.

Cada hito toca 1–2 capas como en `reimpl/`. Nada de “motor completo” antes de rooms reales.

---

## 14. Riesgos y decisiones abiertas

1. **Flotantes vs enteros de mundo:** HoH usaba enteros por necesidad. En Python, flotantes simplifican inercia pero exigen epsilon y semilla para determinismo. Decisión: flotantes + cuantización a 1/100 celda en saves/tests. Revisar si hay divergencias.
2. **Dirty-rect vs redraw:** En moderno, redraw completo es más simple y suficiente. Mantener dirty como optimización opcional de pygame-ce, no como arquitectura.
3. **Gravedad direccional (Jardín):** riesgo de legibilidad. Mitigación: prototipo de papel + una room aislada antes de generalizar vector gravedad.
4. **Nominadores (Torre):** riesgo de confusión lingüística sin texto. Mitigación: nombrar = acto visual (mirar + pulsar), no escribir.
5. **Transformar 1×/room:** riesgo de softlock por mal uso. Mitigación: reversible al reentrar + validador que exige solución alternativa o aviso diegético antes de consumir.

---

## Apéndice — Correspondencia con referencias

- Bucle, proyección, pintor, objeto-vs-objeto, dispatch, directories de rooms, input en mundo, prioridades audio: `references/Head-Over-Heels/README.md`, `docs/hoh_isometric.md`, `docs/hoh_data_structures.md`, `reimpl/README.md`, `frags/AGENT_CONTEXT.md`.
- Disassembly CPC (`references/HeadOverHeels_CPC/Disasm/fileinfo_II.txt`, `scripts/hoh_rooms.py`) como segunda fuente de estructura de rooms y sonidos; solo estructura, nunca contenido.
- Todo lore, nombres, planetas, textos y sprites de esas referencias quedan fuera de DUALIS por biblia §8.

*Fin de arquitectura v1.0. El siguiente paso no es programar: es dibujar 5 rooms en papel que cumplan la biblia.*
