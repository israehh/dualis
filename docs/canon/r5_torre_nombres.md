# R5 — TORRE DE LOS NOMBRES

**Versión:** 1.0 — Diseño canónico
**Estado:** Solo diseño. No código. No blueprints. No tests. No datos. No coordenadas exactas.
**Fuentes:** `docs/canon/dualis_world_plan.md` (§9), `docs/canon/dualis_room_language.md`, `DUALIS_CONTEXT.md`, `docs/dualis_journal.md`.
**Referencias HoH:** solo contraste estructural (puzles simples, elegantes, memorables, basados en observación y relaciones espaciales). Prohibido copiar mecánicas, lore, nombres, mapas, objetos o estructuras concretas.

---

## 1. Visión general

R5 es la región de la IDENTIDAD.

R1 enseñó vocabulario. R2 enseñó variaciones. R3 enseñó síntesis. R4 enseñó inversión del espacio.

R5 enseña inversión de los roles: quién sostiene a quién.

La pregunta de la región no es dónde estoy ni cómo llego. Es quiénes somos el uno para el otro.

El jugador ya domina los cuatro verbos. R5 no añade ninguno. Cambia el sujeto: cada habitación atribuye cada mitad de la solución a uno de los dos, y la solución solo existe cuando ambos ocupan su lugar.

Principio vinculante de la región:

Ninguno basta. Ninguno sobra. Cada uno nombra al otro.

La región contiene 8 habitaciones (R5_01–R5_08) más examen (R5_EXAM). Cada habitación, una sola idea. El examen, ninguna idea nueva.

---

## 2. Fantasía

La Torre de los Nombres es un lugar vertical — visualmente vertical; la lógica sigue siendo cartesiana, sin world_z jugable — donde todo lo que importa tiene un nombre grabado: dinteles, peldaños, quicios.

La fantasía central: la Torre solo deja pasar a quienes se reconocen entre sí.

Ninguna puerta pide objeto, nivel ni contador (R18). Las puertas de R5 piden conducta de reconocimiento: detenerse a mirar, sostener al otro, ocupar el lugar propio, llegar juntos aunque sea a distancia.

La inversión de la región, dicha en una frase:

Hasta ahora DOS sostenía a UNO. En la Torre se descubre que UNO también sostenía a DOS.

No como mecánica nueva — el montaje sigue siendo el mismo gesto — sino como lectura: habitaciones donde el que observa es el que carga con el peso de la solución, donde el que transforma solo puede hacerlo porque el otro aguarda en su sitio, donde separarse a distancia (TENSION) es la prueba de que el vínculo aguanta.

Arco emocional de la región: extrañeza amable (¿por qué me pide detenerme?), responsabilidad (el otro me espera; yo le espero), reconocimiento (sé quién eres para mí). El recuerdo al día siguiente debe ser una frase, no una hazaña: "yo sostenía mirando".

---

## 3. Identidad visual

Propuesta sujeta a fase de implementación; el render no se toca en este documento.

- Materia: alabastro agrietado y tinta. Superficies claras que aceptan inscripciones oscuras: la Torre parece escrita.
- Motivo: el trazo que une dos puntos. Dinteles con dos marcas, peldaños por parejas, relieves de dos figuras. Nunca una figura sola.
- Acento regional (trim de paleta, como R1 piedra / R2 papel / R3 cobre): hueso y tinta. Detalles menores, sin alterar compatibilidad de colores congelados.
- Las salidas conservan estados LOCKED/READY/COMPLETED con contorno + glifo + baliza. La Torre no inventa señales: nombra con las que ya existen.
- Lectura en segundos (R2): cada habitación muestra un foco único — una marca donde alguien debe estar, un objeto que espera nombre, una puerta que mira.

---

## 4. Uso de los verbos

Sin verbos nuevos. Traducción de cada verbo al lenguaje de la identidad:

**OBSERVE — reconocer.** Congelar el fenómeno es detener la mirada sobre el otro. En R5, observar nunca es solo abrir paso: es el acto por el que UNO dice "te veo" y el mundo lo registra. Todo TRANSFORM de la región exige OBSERVE previo (ROOM_DENIED en caso contrario), como ya hacen R4_08 y R5_07.

**TRANSFORM — renombrar.** Transformar el objeto es darle su nombre verdadero. El objeto anuncia su affordance antes de necesitarse (R10): brilla, se comporta distinto, espera. Una sola decisión visible por visita, sin retorno dentro de la visita.

**MOUNT — sostener y ser sostenido.** El gesto mecánico no cambia (UNO sobre DOS). Lo que cambia es la atribución: habitaciones donde el portador decide el camino pero el portado decide el momento, y habitaciones donde el que espera en su marca sostiene tanto como el que carga. La cooperación es legible (R15): un observador externo entiende quién posibilita a quién.

**LINK — pertenencia.** CONNECTED es la cercanía que nombra (juntos sois vosotros). TENSION es la confianza a distancia (separados seguís siéndolo; ya probada en R4_05 y R4_EXAM, aquí con relaciones distintas). LIMIT es la ruptura: nunca abre ninguna salida, en R5 ni en ningún sitio.

---

## 5. Progresión pedagógica

La región enseña en el orden fijo del lenguaje (§7 del room language): demostración pasiva, experimentación segura, combinación forzada. Ritmo alterno entre vecinas (R14): corta, corta, media, corta, media, corta, media, corta; el examen es media.

| Habitación | Idea única | Patrón existente | Dificultad |
|---|---|---|---|
| R5_01 | ser-reconocido | PATTERN_OBSERVE_TO_CROSS | corta |
| R5_02 | el-sostenido-abre | PATTERN_HEIGHT | corta |
| R5_03 | el-nombre-verdadero | PATTERN_TRANSFORM_TO_REACH | corta |
| R5_04 | juntos-a-distancia | PATTERN_OBSERVE_TO_CROSS | media |
| R5_05 | el-que-mira-sostiene | PATTERN_TRANSFORM_TO_REACH | media |
| R5_06 | el-relevo | PATTERN_TIMED_WINDOW | corta |
| R5_07 | ninguno-solo | PATTERN_SHARED_PASSAGE | media |
| R5_08 | orden-de-reconocimiento | PATTERN_HEIGHT | corta |
| R5_EXAM | examen-torre (síntesis, sin idea nueva) | PATTERN_TRANSFORM_TO_REACH | media |

Curva: R5_01–R5_03 presentan cada verbo en clave de identidad por separado (como F25 hizo para R4). R5_04 introduce TENSION con relación nueva (llegada simultánea a distancia, no simple cruce ancho). R5_05–R5_06 invierten roles y turnan presencia. R5_07 exige atribución completa (cada mitad pertenece a uno). R5_08 ordena lo aprendido. R5_EXAM combina todo sin añadir nada (canon §11 del world plan).

Continuidad con R4: R5_01 entra desde R4_EXAM y su primera lectura también miente un poco — la puerta parece pedir prisa y pide detención — pero la inversión espacial queda atrás; aquí la inversión es de roles. Ninguna habitación exige comprensión futura (R9): todo lo mecánico viene de R1–R4.

---

## 6. Diseño de habitaciones

Convención: cada ficha declara idea única, patrón ya existente, recorrido esperado, solución real, momento ¡Ajá!, salida y reglas del room language verificadas. Sin coordenadas, sin geometría, sin implementación.

### R5_01 — El Umbral Que Mira

**Idea:** ser-reconocido. **Patrón:** PATTERN_OBSERVE_TO_CROSS. **Dificultad:** corta.

**Intención.** Abrir la región con un solo verbo en clave nueva: la puerta no pide prisa, pide detención. El jugador llega corriendo desde R4_EXAM y la habitación le enseña a parar.

**Punto focal.** Un dintel con dos marcas y un batidor central que no amenaza: marca el ritmo de la sala. La salida, al fondo, apagada hasta que alguien mira de verdad.

**Recorrido esperado.** El jugador corre a la salida y la encuentra cerrada (LOCKED, sin castigo). Prueba con uno, luego con otro. Observa por costumbre de R4 — el batidor se congela, la sala cambia de estado (READY) — y al plantarse el dúo, la salida completa.

**Solución real.** Congelar y plantarse. La solución es comprender que en la Torre primero hay que dejarse ver.

**Posibles errores.** Intentar cruzar sin observar. Observar y cruzar solo con uno.

**Momento ¡Ajá!.** No me abren porque llegue; me abren porque me detengo a mirar.

**Salida.** Una, al fondo, obvia tras comprender. La salida secreta (comprensión excedente, R22) es posicional: cruzar sin haber deshecho la observación.

**Reglas verificadas.** R1, R2, R4, R5, R6, R8, R12, R24.

**Riesgos.** Que la detención se lea como arbitrariedad (A1). Mitigación: el batidor es el foco único y su congelación produce consecuencia visible inmediata (READY).

### R5_02 — El Hombro Devuelto

**Idea:** el-sostenido-abre. **Patrón:** PATTERN_HEIGHT. **Dificultad:** corta.

**Intención.** Releer el montaje: DOS carga, pero es la llegada de UNO (el sostenido) la que completa. El portador decide el camino; el portado decide el sentido.

**Punto focal.** Un vano alto con dos marcas: una baja (donde DOS debe detenerse para ofrecer el hombro) y la salida arriba, que solo reacciona a UNO.

**Recorrido esperado.** El jugador intenta llegar a pie y confirma que no alcanza. Monta por costumbre de R4_02, cruza montado y completa. Al releer la escena entiende que DOS no podía entrar solo: la puerta esperaba al de arriba.

**Solución real.** Montar y cruzar juntos. La solución es comprender que sostener no es usar: el que carga también necesita al que lleva.

**Posibles errores.** Cruzar sin montar. Montar lejos de la marca y desorientarse (sin castigo: desmontar y reintentar).

**Momento ¡Ajá!.** Yo le llevaba, pero era él quien abría.

**Salida.** Una, en alto, obvia tras montar.

**Reglas verificadas.** R1, R2, R5, R6, R12, R15, R24.

**Riesgos.** Que se lea igual que R4_02 con otra piel (A8). Mitigación: aquí la relación varía — no es altura que se vuelve planicie, es atribución de quién abre — y el texto de la sala (dintel con dos marcas) lo declara antes de exigirse.

### R5_03 — El Nombre Verdadero

**Idea:** el-nombre-verdadero. **Patrón:** PATTERN_TRANSFORM_TO_REACH. **Dificultad:** corta.

**Intención.** Presentar TRANSFORM en clave de identidad: el objeto no es un obstáculo, es algo sin nombrar. Transformarlo es darle su nombre.

**Punto focal.** Un objeto central con affordance anunciada (brillo/conducta distinta, R10) y una salida apagada tras él.

**Recorrido esperado.** El jugador reconoce el patrón de R4_04, transforma y cruza. La novedad es solo de lectura, y basta: primera vez de la idea "renombrar" aislada (R16).

**Solución real.** Transformar una vez y plantarse. Decisión visible, sin retorno en la visita.

**Posibles errores.** Transformar sin haber mirado primero (aquí aún se permite: la exigencia de orden llega en R5_07; R16).

**Momento ¡Ajá!.** No lo rompí: lo llamé por su nombre.

**Salida.** Una, tras el objeto.

**Reglas verificadas.** R1, R2, R4, R10, R11, R12, R24.

**Riesgos.** Habitación demasiado parecida a R4_04. Mitigación: dificultad corta deliberada y foco en affordance previa; la variación real viene después (R5_05, R5_07).

### R5_04 — Juntos a Distancia

**Idea:** juntos-a-distancia. **Patrón:** PATTERN_OBSERVE_TO_CROSS. **Dificultad:** media.

**Intención.** Primera puerta TENSION de la región, con relación nueva respecto a R4_05: no basta cruzar separado, hay que LLEGAR A LA VEZ. La salida ancha solo completa con el dúo repartido en sus extremos en el mismo intervalo: simultaneidad, no prisa (cooperación simultánea).

**Punto focal.** Una salida ancha con una marca en cada extremo y un ritmo visible que invita a sincronizar.

**Recorrido esperado.** El jugador observa (congela la referencia), coloca a cada uno en un extremo y ajusta hasta que ambos están dentro a la vez. Probar por turnos falla de forma legible: la salida indica a quién le falta llegar.

**Solución real.** Observar y ocupar ambos extremos simultáneamente en TENSION. La solución es comprender que separados también son ellos, si llegan juntos.

**Posibles errores.** Cruzar juntos por el centro (completa el runtime pero el gate no abre — como R4_05). Llegar por turnos.

**Momento ¡Ajá!.** La distancia no nos rompe si la ocupamos a la vez.

**Salida.** Una, ancha, con lectura de doble marca.

**Reglas verificadas.** R1, R2, R5, R6, R12, R15, R18, R24.

**Riesgos.** Exigir sincronía perfecta como puerta principal (A10). Mitigación: la ventana es generosa; el gate pide TENSION (estado, no instante) y el runtime solo pide presencia simultánea, sin encadenado.

### R5_05 — El Que Mira Sostiene

**Idea:** el-que-mira-sostiene. **Patrón:** PATTERN_TRANSFORM_TO_REACH. **Dificultad:** media.

**Intención.** Inversión de roles declarada: UNO, el observador, se vuelve el pilar — debe aguardar en su marca mientras DOS transforma desde lejos. El que no actúa es el que sostiene.

**Punto focal.** Una marca luminosa lejos del objeto transformable: el sitio de UNO. El objeto, al otro lado, esperando a DOS.

**Recorrido esperado.** El jugador lleva a DOS al objeto y transforma… y nada completa, porque UNO no está en su sitio. Relee la sala, coloca a UNO en la marca (quietud como acción), transforma de nuevo y completa.

**Solución real.** UNO en su marca + TRANSFORM de DOS + dúo en salida. La solución es comprender que esperar en el lugar propio también es cooperar (cooperación espacial).

**Posibles errores.** Mover a UNO junto a DOS por costumbre ("los dos a todo"). Transformar antes de colocar a UNO (falla de forma legible: falta el que mira).

**Momento ¡Ajá!.** Yo no hacía nada… y era lo que más sostenía.

**Salida.** Una, central.

**Reglas verificadas.** R1, R2, R5, R6, R7, R12, R15, R24.

**Riesgos.** Que la quietud se lea como pasividad arbitraria (A1). Mitigación: la marca es el foco único y la consecuencia de ocuparla es visible (READY) antes de la transformación.

### R5_06 — El Relevo

**Idea:** el-relevo. **Patrón:** PATTERN_TIMED_WINDOW. **Dificultad:** corta.

**Intención.** Turnarse sin soltarse: la ventana temporal obliga a repartirse funcionalmente sin romper el vínculo (P9). Uno cruza mientras el otro sostiene la ventana; luego el relevo. Ritmo alterno tras dos medias (R14).

**Punto focal.** Un resonador con ventana anunciada (aviso de canal claro, P12) y un paso que solo existe durante ella.

**Recorrido esperado.** El jugador anticipa posiciones con el aviso, cruza con uno durante la ventana y trae al otro en la siguiente. Experimentación segura: fallar la ventana solo devuelve al inicio de la sala, con información.

**Solución real.** Cruzar por turnos dentro de la ventana, vínculo intacto. La solución es comprender que relevarse también es estar juntos.

**Posibles errores.** Intentar cruzar los dos a la vez en una ventana corta. Ignorar el aviso.

**Momento ¡Ajá!.** No pasamos juntos: nos pasamos el turno. Y seguimos juntos.

**Salida.** Una, tras el paso.

**Reglas verificadas.** R1, R2, R4, R8, R12, R14, R19, R24.

**Riesgos.** Ventana que castiga el descubrimiento (A3). Mitigación: la ventana solo gobierna el cruce, nunca la comprensión; el aviso precede siempre a la exigencia.

### R5_07 — Ninguno Solo

**Idea:** ninguno-solo. **Patrón:** PATTERN_SHARED_PASSAGE. **Dificultad:** media.

**Intención.** Atribución completa: la mitad OBSERVE pertenece a UNO y la mitad TRANSFORM pertenece a DOS, con orden exigido (transformar antes de observar = ROOM_DENIED, como R4_08). Ni la mitad basta. Clímax de la región antes del cierre amable.

**Punto focal.** Sombra y fuente a la vista a la vez: dos focos coordinados pero una sola idea (R2 se cumple porque la idea es la atribución misma).

**Recorrido esperado.** El jugador intenta transformar primero y recibe ROOM_DENIED legible (fallo que informa, R8). Observa con UNO, transforma con DOS, cruza el dúo. Cada uno hizo lo suyo; ninguno hizo lo del otro.

**Solución real.** OBSERVE (UNO) → TRANSFORM (DOS) → dúo en salida. Orden forzado una vez, con claridad (combinación forzada).

**Posibles errores.** Transformar antes de observar (DENIED informativo). Cruzar solo con uno.

**Momento ¡Ajá!.** La puerta no pedía dos manos: pedía las dos personas.

**Salida.** Una, compartida.

**Reglas verificadas.** R1, R5, R6, R7, R8, R12, R15, R16, R24.

**Riesgos.** Dos focos que compiten (división, §2 del lenguaje). Mitigación: sombra y fuente se presentan como pareja (un solo conjunto visual), y la idea única —atribución— los une.

### R5_08 — Orden de Reconocimiento

**Idea:** orden-de-reconocimiento. **Patrón:** PATTERN_HEIGHT. **Dificultad:** corta.

**Intención.** Cierre amable que ordena lo aprendido: observar primero, montar después, cruzar. Nada nuevo; todo en su sitio. Ritmo corto tras el clímax (R14).

**Punto focal.** Dintel con dos marcas y vano alto: la sala cita R5_01 y R5_02 a la vez, deliberadamente.

**Recorrido esperado.** El jugador observa (la sala lo agradece con READY), monta y cruza. Si monta sin observar, el cruce no completa: el orden importa, y ya lo sabe.

**Solución real.** OBSERVE → MOUNT → dúo en salida. La solución es comprender que reconocer precede a sostener.

**Posibles errores.** Montar directamente por prisa (falla legible, sin castigo).

**Momento ¡Ajá!.** Ya sabía hacer esto. Ahora sé por qué lo hago.

**Salida.** Una, en alto.

**Reglas verificadas.** R1, R2, R5, R9, R12, R14, R24.

**Riesgos.** Repetición con otra piel (A8). Mitigación: es cierre, no novedad — su función es ordenar, y el lenguaje lo permite (combinación sin idea nueva antes del examen).

---

## 7. Examen

### R5_EXAM — El Nombre del Dúo

**Idea declarada:** examen-torre. **Patrón:** PATTERN_TRANSFORM_TO_REACH (observable + transformable → ExamRuntime existente). **Dificultad:** media. **Sin ideas nuevas** (world plan §11).

**Intención.** Combinar los cuatro verbos con atribución de roles: UNO observa (suya es la mirada), DOS transforma (suyo es el nombre), el dúo monta (suyo es el sostén) y la salida ancha solo abre en TENSION (suya es la confianza). La misma maquinaria probada en R4_EXAM, con significado nuevo: no se añade nada, se reconoce todo.

**Recorrido esperado.** OBSERVE → TRANSFORM (DENIED si se altera el orden) → juntar → MOUNT → completar → separar a TENSION para abrir (COMPLETED pegajoso, como R4_EXAM). Cada paso pertenece a alguien; el examen verifica que el jugador sabe a quién pertenece cada paso.

**Solución real.** Secuencia completa con el dúo repartido en la salida ancha en TENSION.

**Posibles errores.** Los mismos de R4_EXAM, ahora legibles en clave de roles: transformar sin mirar (impaciencia de DOS), montar sin juntar (prisa), abrir en CONNECTED (miedo a la distancia).

**Momento ¡Ajá!.** Sé quién mira, quién nombra, quién sostiene. Sé quiénes somos.

**Salida.** Una, ancha, que exige TENSION por puerta lógica + geometría (validar juntas, como F26/F27).

**Reglas verificadas.** R5, R6, R9, R12, R15, R24.

**Riesgos.** Que el examen se lea como R4_EXAM repetido. Mitigación: la coreografía ordenada por roles y la lectura de la Torre lo distinguen; mecánicamente la repetición es legítima (el examen no debe inventar).

---

## 8. Riesgos

1. **Abstracción sin cuerpo.** La identidad es conceptual; si alguna habitación se entiende pero no se siente en el cuerpo (posiciones, montaje, distancia), es débil (§1 del lenguaje: la pregunta se verifica con el cuerpo). Criterio de corte: toda ficha debe poder resolverse describiendo solo dónde está cada uno.
2. **R5_02 / R5_08 vs R4_02.** Tres rooms HEIGHT en dos regiones. Diferenciación obligatoria en implementación: R4_02 = altura-planicie; R5_02 = atribución (el sostenido abre); R5_08 = orden (observar antes de montar). Si en playtest se resuelven igual, fusionar o cortar (A7).
3. **R5_04 vs R4_05.** Dos anchas TENSION. Diferencia: R4_05 = cruzar separado; R5_04 = llegar a la vez (simultaneidad). Ventana generosa siempre (A10).
4. **R5_EXAM vs R4_EXAM.** Misma maquinaria. Aceptado por canon (examen sin ideas nuevas); la distinción es de lectura, no de mecanismo. No añadir un segundo gate ni una condición extra para "diferenciarlo": sería complejidad sin claridad.
5. **Doble foco en R5_07.** Sombra + fuente compiten. Presentarlos como pareja visual única; si el playtest ciego muestra confusión, dividir es podar (una idea por sala, siempre).
6. **Puerta CONNECTED sin contraste.** Ninguna room R5 exige CONNECTED por gate: en salidas pequeñas CONNECTED ya lo exige la geometría y un gate sería redundante. No declararlo.
7. **Texto en lugar de espacio.** Si alguna habitación necesita explicación para entenderse, se rediseña en lugar de rotularse (R24).
8. **Atasco sin alternativa.** Al abrir R5, la regla R21 exige que el jugador atascado tenga adónde ir: la vuelta a R4 queda abierta (tránsito bidireccional F24/F28) hasta que el mundo justifique atajos (canon §13–§14).

---

## 9. Integración con R4_EXAM

La expansión ocurre en el extremo actual (canon §15): R5_01 declara enlace desde R4_EXAM y la cadena continúa R5_01–…–R5_08–R5_EXAM (fondo final).

Siguiendo el patrón F28 ya establecido y verificado:

- Los JSON existentes no se tocan: R4_EXAM seguirá declarando sus enlaces congelados en datos; la arista R4_EXAM→R5_01 vivirá en la capa de campaña (`EXTRA_LINKS`), como las tres aristas F28.
- Las rooms R5 vivirán en `data/r5_rooms/`, fuera de `data/blueprints/` (44 exactos, test_f11 intacto), como `link_rooms` y `r4_rooms`.
- El cargador de `main.py` ya itera varios directorios de planos: añadir el tercero es una línea en el mismo cuerpo de bucle.
- El gate LINK acepta nuevas puertas con +1 entrada en `REQUIREMENTS` si alguna room R5 la necesita (previsto: R5_04 y R5_EXAM en TENSION; validar geometría + gate juntas).
- `entry_for` ya es genérico: las entradas R5 se verifican con el mismo criterio F24 (fuera de salida, sin sólidos, d<210, determinista), incluidas las direcciones de vuelta.
- R4_EXAM pasa de fondo final a bisagra, igual que TAL_09 en F28: su solución y sus tests no cambian; solo el mapa de campaña añade su arista de salida.

---

## 10. Preparación para R6

R6 — ARCHIVO DE LO QUE NO FUE (world plan §10): confrontar versiones alternativas de patrones ya conocidos; región de reflexión y reinterpretación.

R5 deja el terreno preparado:

- **Extremo nuevo:** R5_EXAM será el fondo final y la bisagra de R6, igual que R4_EXAM lo es hoy de R5.
- **Material reinterpretable:** cada room R5 tiene una lectura alternativa natural (¿y si el que mira no sostiene? ¿y si el nombre era otro?), que es exactamente la materia de R6: variantes de patrones conocidos, no mecánicas nuevas.
- **Vínculo maduro:** tras R5, CONNECTED/TENSION/LIMIT han significado cercanía, confianza y ruptura; R6 puede usarlos como memoria (fragmentos, resonadores) sin redefinirlos.
- **Lo que R6 no debe hacer:** añadir verbos, reabrir regiones cerradas entre medias (canon §15), ni convertir el examen final (NÚCLEO) en otra cosa que combinación sin ideas nuevas.

*Fin del diseño R5 v1.0. Implementar fuera de este diseño es implementar fuera de DUALIS.*
