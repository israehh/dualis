# DUALIS — Biblia de Diseño

**Versión:** 1.0 — Documento fundacional
**Estado:** Canónico. Congela visión, identidad y reglas.
**Prioridad de fuentes:**
1. `docs/dualis_concept.txt` — prioridad absoluta. Define qué es DUALIS.
2. `docs/dualis__history.md` — prioridad absoluta. Define de dónde viene la gramática.
3. `references/HeadOverHeels_CPC` y `references/Head-Over-Heels` — solo referencia técnica y de diseño. Nunca fuente de lore, nombres, planetas, sprites ni código.

**Regla de oro:** DUALIS no es un clon, remake ni secuela de Head Over Heels. Es una reinterpretación del espíritu: dos mitades, una mente, un mundo que se entiende pensando.

---

## 1. Visión del juego

### 1.1 Frase fundacional

> DUALIS es un juego sobre entender.
> Entender el mundo. Entender a Uno y Dos. Entenderte a ti mismo.

No es un juego de habilidad. No es un juego de puzles en el sentido de catálogo de retos. No es un juego de exploración en el sentido de mapa por completar. Es un juego donde el progreso real ocurre en la cabeza del jugador, no en una barra de XP.

Cuando termina, el jugador no recuerda haber “resuelto puzles”. Recuerda haber pensado.

### 1.2 Premisa canónica

Dos entidades —una conciencia fragmentada— habitan el mismo cuerpo mecánico en una estación espacial abandonada llamada **El Nudo**.

El Nudo no es una estructura: es un organismo artificial construido dentro de un asteroide hueco, invadido por una plaga de parásitos conceptuales que devoran la coherencia del espacio. Las habitaciones cambian, los objetos se reinterpretan, las leyes físicas se pliegan sobre sí mismas.

El objetivo no es “salvar la estación”. Es **recomponer la mente**. Cada región de El Nudo representa un fragmento de memoria rota. Completar una región no te da una llave: te da una parte de ti mismo que habías olvidado.

### 1.3 Los tres pilares de experiencia

1. **Curiosidad constante:** ¿qué hay en la siguiente room?
2. **Orgullo intelectual:** lo he resuelto yo solo, sin tutorial.
3. **Afecto por dependencia:** Uno y Dos no tienen diálogo, pero los cuidas porque se necesitan.

A ellos se suma un cuarto, visual: **asombro de diorama**. Cada room es una ilustración viva que quieres mirar antes de resolver.

### 1.4 Qué promete y qué no promete

**Promete:**

- Un mundo enorme que se siente íntimo porque cada room es un puzle cerrado.
- Libertad real desde el inicio, con orden sugerido por comprensión, no impuesto por llaves.
- Muerte barata. Bloqueo mental como único castigo real.
- Final electivo, no victoria militar.

**No promete:**

- Poder creciente, builds, combate, loot, misiones marcadas, mapa automático, cinemáticas explicativas, multijugador.
- Reflejos como puerta de progreso. La ejecución importa, pero nunca bloquea la comprensión.

### 1.5 Referencia de tono

Melancólico pero no deprimente. Absurdo pero no cómico. Extrañamente cálido. Como recordar un sueño que no sabes si fue real.

Si una idea es muy oscura, se descarta. Si es muy chistosa, se descarta. Si da ternura inquietante, se queda.

---

## 2. Principios de diseño

Derivados directamente de `dualis_concept.txt §2, §5, §11` y `dualis__history.md Parte I §2, §5`.

### P1. Dos mitades, un cerebro

Ningún puzle importante se resuelve “cambiando de personaje para pasar”. Se resuelve con **diálogo mecánico**: lo que hace Uno solo Dos puede aprovechar, y viceversa. La alternancia es el fracaso del diseño; la cooperación es el diseño.

### P2. Comprensión > poder

No hay niveles, XP, puntos ni desbloqueos de fuerza. El jugador no se vuelve más fuerte. Se vuelve más listo. Las “habilidades nuevas” son en realidad comprensiones nuevas de lo que Uno y Dos siempre pudieron hacer.

Prohibido: puertas que piden nivel, enemigos que piden DPS, coleccionables que piden farmeo.

### P3. Nada se explica. Todo se encuentra

Cero tutoriales textuales. Cero pop-ups de “pulsa X para…”. Las mecánicas se aprenden por:

1. **Demostración pasiva** — ves al mundo hacer algo al entrar.
2. **Experimentación segura** — puedes probar sin morir de forma punitiva.
3. **Combinación forzada** — la salida solo existe si usas lo nuevo.

Si una mecánica necesita explicación escrita, el diseño ha fallado y debe rediseñarse la room.

### P4. Cada room debe ganarse su existencia

Toda room cumple al menos una función, sin excepción:

1. **Sorprender** — rompe una expectativa.
2. **Enseñar** — introduce mecánica sin tutorial.
3. **Desafiar** — exige solución no obvia.
4. **Recompensar** — da habilidad, acceso o conocimiento.
5. **Revelar** — muestra secreto o historia.

Prohibido: rooms de relleno, pasillos para “ir de A a B”, repetición de un puzle ya resuelto con otra skin.

### P5. Legibilidad en 3 segundos

Al entrar, el jugador debe entender qué tipo de espacio es, qué peligros contiene y qué posibilidades ofrece. Punto focal único, lógica visual coherente con su región, al menos dos salidas (una obvia, una secreta o no tanto).

La ambigüedad visual es un bug, no un misterio. El misterio está en la solución, no en no ver qué hay.

### P6. Libertad estructurada

Desde el principio se puede ir a cualquier región. Pero algunas son incomprensibles sin haber entendido otras. La llave es el conocimiento, no el objeto.

Esto exige: sin orden obligatorio, sin bloqueo por falta de poder, siempre una alternativa adonde ir si estás atascado. Si el jugador se bloquea globalmente, es fallo de grafo, no “dificultad”.

### P7. Muerte barata, memoria cara

Morir no quita progreso significativo. Lo que duele es no entender. Además, en DUALIS la muerte tiene consecuencia narrativa suave: **la estación recuerda** (cambios sutiles de iluminación, posición de objetos, frases visuales). No castiga; testimonia.

### P8. Memoria > mapa

Sin mapa automático. El jugador recuerda “la de las escaleras-perro”, “la del péndulo”, “la que gira”. Para lograrlo: formas únicas, mecanismos únicos, ritmo alternado, coherencia visual por región.

Los puntos de referencia visuales son sistema de navegación. Diseñarlos es diseñar el mapa invisible.

### P9. Materialidad y diorama

El isométrico no es limitación técnica retro. Es decisión artística contemporánea: mirar un diorama vivo pintado a mano, con paleta limitada por región, iluminación dramática y texturas que sugieren óxido, seda, hueso, cristal. Animación mínima pero expresiva.

### P10. La estación es un personaje

Las puertas tienen opiniones. Las máquinas recuerdan a sus operadores. Los pasillos respiran. El Nudo observa, juzga, a veces ayuda, a veces ignora. Nunca es solo decorado.

---

## 3. Identidad propia de DUALIS

Qué hace que DUALIS no sea Head Over Heels con otra skin. Esta sección es vinculante: cualquier propuesta que acerque DUALIS al clon debe rechazarse.

### 3.1 No es espacial heroico, es íntimo biológico-brutalista

Head Over Heels: cinco planetas dispares (Blacktooth, Penitentiary, Safari, Book World, Egyptus), imperio opresor, coronas que reunir, tono aventura imperial.

DUALIS: **un solo lugar** — El Nudo, asteroide hueco, mitad arquitectura brutalista, mitad biología alienígena. Fue construido por alguien y luego habitado por algo. No hay imperio que derrocar. Hay una mente que recomponer: la tuya y la de la Entidad Original.

No hay coronas. No hay imperio. No hay “salvar el mundo”.

### 3.2 No son Head y Heels renombrados, son Uno y Dos

Head salta y dispara; Heels corre y carga. Son dos cuerpos intercambiables con mochila.

Uno y Dos son **dos mitades de la misma mente que no pueden separarse** más de 10 unidades. Si se separan, la pantalla se oscurece y ambos sufren. No es alternancia táctica; es vínculo permanente. No hablan. Se miran, se esperan, se lanzan, se sostienen. Su lenguaje es corporal.

Habilidades canónicas (de `dualis_concept.txt §3`, no negociables sin revisión de biblia):

- **Uno:** salto largo y preciso + marca temporal en el aire (plataforma de 3 s) + Observar (congela el tiempo 2 s para planificar, no para combatir). Curioso, cauteloso, melancólico. No empuja, no rompe, no corre.
- **Dos:** carrera que genera energía cinética (embiste, empuja bloques, activa por impacto) + Transformar (reinterpreta un objeto una vez por room: silla→plataforma, enemigo→aliado temporal, puerta→pared). Impulsivo, alegre, temerario. No hace saltos finos, no para en seco, no observa.

Ninguno dispara. El disparo de Head se descarta explícitamente (ver §8).

### 3.3 No hay inventario extractivo, hay reinterpretación

En Head Over Heels la economía es llevar objetos en bolsa con agujeros, interruptores remotos, teletransportadores.

En DUALIS no se acumula. Se **reinterpreta**. Dos transforma, Uno congela y marca. Los secretos no son “objetos útiles para después” en sentido de llave inglesa; son formas nuevas de usar a Uno y Dos, atajos que solo existen si exploraste, o rooms puramente narrativas que cambian tu comprensión del final.

### 3.4 La plaga es conceptual, no militar

Los “enemigos” de DUALIS no son patrullas que matar. Son **desafíos, no enemigos** (concepto §7):

- Ecos, Bibliotecarios, Puertas con Opiniones, Nominadores, la Entidad Original.

No se matan. Se aprende a moverse con ellos, a nombrarlos, a no mirarlos, a sincronizarse. La violencia como solución es ajena a DUALIS.

### 3.5 El final es ético, no triunfal

Head Over Heels termina reuniendo coronas y liberando planetas. DUALIS termina con una **elección**: qué hacer con la Entidad Original rota, y si Uno y Dos deben separarse para siempre o fusionarse en uno solo. Hay una versión opcional de la estación donde nunca se separaron (Archivo de lo que no fue) que cambia el final si entras. El objetivo es aceptación, no victoria.

### 3.6 Firma visual y sonora propia

- Isométrico 2:1 pintado a mano, no voxel 3D, no pixel-art nostálgico 1:1.
- Paleta limitada por región (ver §5), luz dramática, grano material.
- Sonido como información potencial (rooms donde el sonido es el mapa), no chiptune beeper/AY. La referencia sonora de 1987 se estudia por estructura (loops, prioridades), no se imita.

Si alguien mira una captura y dice “es Head Over Heels HD”, hemos fallado. Debe decir “me recuerda a lo que sentía con Head Over Heels, pero es otra cosa”.

---

## 4. Relación entre UNO y DOS

Esta es la mecánica, la narrativa y la emoción. Todo lo demás orbita aquí.

### 4.1 Ontología

Uno y Dos no son hermanos, ni amigos, ni piloto y robot. Son **una conciencia fragmentada en el mismo cuerpo mecánico**. El jugador es el tercer vértice: el cerebro que los opera a ambos. Por eso el juego dice “DUALIS no es sobre Uno y Dos. Es sobre ti”.

No tienen voz. Tienen cuerpo:

- Uno espera a Dos antes de saltar.
- Dos mira a Uno antes de embestir.
- Si uno sufre por separación, el otro se gira.

El lenguaje corporal es especificación de animación, no flavor.

### 4.2 Regla de vínculo (inamovible)

- Distancia máxima: **10 unidades** (unidad = celda lógica del mundo).
- Si se supera: viñeta oscura progresiva, temblor leve, drenaje de estabilidad, ambos se ralentizan. No muerte instantánea.
- Excepción diseñada: **una sola puerta en El Vestíbulo** que solo se abre si aceptas separarte y sufrir. Es la primera lección moral y mecánica: la separación es posible, pero dolorosa. No se repite como truco barato.

Esta regla obliga a que toda room sea resoluble con ambos cerca, y convierte cada room en puzle de relaciones, no de recorrido.

### 4.3 Gramática cooperativa canónica

Combinaciones que el diseño debe usar y variar, no agotar en una room:

1. **Montar:** Uno salta sobre Dos para alcanzar cornisas. Dos es plataforma móvil.
2. **Lanzar:** Dos lanza a Uno contra objetos lejanos / interruptores / enemigos-recurso. Uno rebota y debe aterrizar.
3. **Congelar para cruzar:** Uno congela 2 s para que Dos atraviese zona peligrosa o sincronice máquinas.
4. **Transformar para usar:** Dos reinterpreta objeto → Uno lo usa como plataforma / puente / sombra.
5. **Puente humano:** ambos forman puente con sus cuerpos 3 s para que algo pase por encima.
6. **Marca temporal:** Uno deja plataforma aérea 3 s → Dos debe correr y alcanzarlo antes de que se desvanezca (variante: eco de salto que se repite 5 s después).

Ninguna room tardía puede exigir solo 1–2. El clímax (Núcleo) las combina todas.

### 4.4 Progresión de la relación (arco emocional)

- **Inicio (confusión):** ¿qué hago? ¿adónde voy? Torpeza de control dual. Afecto por torpeza compartida.
- **Mitad (comprensión):** ya sé cómo funcionan. Anticipo al otro. Placer de sincronía.
- **Final (aceptación):** entiendo qué soy. La elección final duele porque quiero a ambos.

El juego nunca explica esto con texto. Lo produce el diseño de rooms.

### 4.5 Lo prohibido en la relación

- No pueden fusionarse a voluntad salvo rooms rituales específicas (momento 13/25). La fusión es evento, no botón.
- No pueden hablar ni recibir órdenes por voz.
- No puede uno morir permanentemente sin el otro. La muerte es siempre conjunta en consecuencia narrativa.
- No hay personaje “principal” y “secundario”. El modo activo es conveniencia de input, no jerarquía.

---

## 5. Mundo y narrativa

### 5.1 El Nudo — definición

Estación espacial construida dentro de un asteroide hueco. Mitad brutalismo (mármol agrietado, techos altísimos, prensas, cintas), mitad organismo (pasillos que respiran, puertas con opiniones, máquinas que recuerdan). Fue construida por alguien, habitada por algo, rota por una plaga de parásitos conceptuales que devoran coherencia.

Narrativa ambiental, sin diálogos ni misiones. Se cuenta con arquitectura, comportamiento de criaturas y secretos.

### 5.2 Las siete regiones (canónicas)

Cada región = fragmento de memoria rota + identidad mecánica y visual consistente + al menos un momento que rompe sus propias reglas. Orden sugerido, nunca obligatorio.

**R1 — El Vestíbulo (tutorial orgánico)**
Función: moverse, saltar, correr, descubrir vínculo. Mármol agrietado, luces parpadeantes, puertas cerradas pero no bloqueadas. Secreto: puerta que exige separación dolorosa. Paleta: gris cálido + ámbar.

**R2 — La Biblioteca Húmeda (observación y memoria)**
Biblioteca inundada, libros flotantes, estanterías-islas, agua que sube/baja con el tiempo en región. Civilización: Bibliotecarios (papel, reorganizan pasillos al parpadear). Secreto: libro que cuenta historia de Uno y Dos → desbloquea comprensión (habilidad). Paleta: verde tinta + papel.

**R3 — El Taller de los Ecos (físico y temporal)**
Martillo eterno, cintas en bucle, prensa. Civilización: Ecos (residuos de operarios, obstáculos con memoria, no enemigos). Secreto: sincronizar todas las máquinas al mismo ritmo abre puerta. Paleta: óxido + grasa + chispa.

**R4 — El Jardín Invertido (espacial y gravedad)**
Plantas crecen hacia abajo, cielo es suelo, gravedad cambia según dirección de mirada. Civilización: Jardineros ciegos que riegan plantas inexistentes. Secreto: flor que solo florece si nunca la miras directamente. Paleta: negro fértil + clorofila pálida + hueso.

**R5 — La Torre de los Nombres (cooperativo e identidad)**
Torre infinita, cada piso un nombre que cambia si lo pronuncias. Civilización: Nominadores (existen mientras los nombras; si los nombras, te nombran y cambias). Secreto: nombres verdaderos de Uno y Dos → habilidad combinada. Paleta: azul archivo + tiza.

**R6 — El Archivo de lo que no fue (ambiental y narrativo)**
Versiones alternativas de la estación según decisiones no tomadas. Sin civilización, solo ecos de decisiones. Secreto: versión donde Uno y Dos nunca se separaron — entrar es opcional pero cambia el final. Paleta: blanco roto + gris espejo.

**R7 — El Núcleo (clímax)**
Corazón imposible, geometría no euclidiana, tiempo no lineal. Civilización: Entidad Original rota que quiere ayuda sin saber pedirla. Secreto: el final no es ganar, es elegir qué hacer con ella. Paleta: todas las anteriores contaminadas + luz imposible.

### 5.3 Civilizaciones (no facciones enemigas)

- **Bibliotecarios, Ecos, Jardineros, Nominadores:** obstáculos con memoria, lógica propia, nunca farmeables. No tienen HP. Tienen comportamiento legible y manipulable.
- **Entidad Original:** presencia, no boss. Observa, juzga, ayuda o ignora. El “encuentro” es oferta de trato, no combate.

### 5.4 Cómo se cuenta sin contar

- Sin mapa, sin quest log, sin Codex que explique.
- Secretos narrativos: rooms sin puzle, solo historia, que recontextualizan todo.
- La estación recuerda muertes y visitas (iluminación, objetos desplazados). Es continuidad emocional, no sistema punitivo.
- Los nombres verdaderos y el Archivo son los únicos giros explicativos, y llegan tarde, cuando el jugador ya intuye.

### 5.5 Finales (conceptuales, no implementados aún)

- **Fusión:** Uno y Dos se vuelven uno. Comprensión total, pérdida de dualidad.
- **Separación:** viven como dos. Libertad, pérdida de vínculo.
- **Variante Archivo:** si entraste donde nunca se separaron, se desbloquea tercera lectura (no tercer final “bueno”, sino comprensión distinta).

Ningún final es “verdadero”. Todos son aceptación.

---

## 6. Mecánicas principales

### 6.1 Locomoción dual

- **Uno:** salto preciso de arco controlable, sin carrera. Caída predecible. No empuja > umbral ligero. Marca temporal: al saltar puede dejar plataforma de 3 s en el ápice (cooldown por room, no por tiempo global, para forzar diseño local).
- **Dos:** aceleración con inercia, sin salto fino, sin frenada en seco. Carga que empuja bloques, rompe tabiques designados y activa mecanismos por impacto. La velocidad es recurso (energía cinética), no solo desplazamiento.

Input mapea a ejes de mundo, no de pantalla (herencia Filmation II): arriba aleja de cámara, etc. Tutorializado por demostración, no por texto.

### 6.2 Poderes cognitivos (una vez por contexto)

- **Observar (Uno):** congela el mundo 2 s. El jugador puede mover cámara / planificar, no reposicionarse gratis. Sirve para cruces, sincronías y lectura de sombras/patrones. No es bullet-time de combate.
- **Transformar (Dos):** una vez por room, reinterpreta un objeto elegible (silla→plataforma, enemigo→aliado temporal, puerta→pared). Irreversible en esa visita; al reentrar se restaura. Obliga a decisión, no a spam. Todo objeto transformable debe comunicar affordance visualmente (brillo, forma, comportamiento), nunca con icono UI.

### 6.3 Sistemas de room

- Gravedad direccional / invertida (Jardín), salas que giran, péndulos, ecos que repiten acciones a +5 s, cuentas atrás 10/60 s, agua que sube, relojes que avanzan si te mueves, plataformas que solo existen si las miras, puertas que se abren si las ignoras / si no corres / si no miras.
- Todos los sistemas son locales a room o región, con gramática global: entrar → leer en 3 s → experimentar seguro → ¡ajá! → dos salidas.

### 6.4 Sin sistemas proscritos por defecto

No hay: combate con HP, inventario cuantitativo, crafting, tienda, stamina que bloquee, sigilo con cono de visión punitivo, plataformas que exijan frame-perfect encadenado como norma. Si aparecen, son variaciones de una room, no sistema global.

---

## 7. Inspiraciones tomadas de Head Over Heels

Solo lo estructural y filosófico. Nada de contenido trasplantado.

### 7.1 Lo que se adopta

1. **Dos personajes, un cerebro como núcleo, no como gimmick.** De HoH se toma la idea de que la solución requiere que ambos actúen en conjunto (montar, lanzar, usar como plataforma). En DUALIS se radicaliza con vínculo de distancia.
2. **Mundo coherente disfrazado de disparate.** De los cinco planetas se toma la lección: cada zona identidad mecánica+visual consistente. En DUALIS son siete regiones de una sola estación, no planetas.
3. **Puzles sin tutorial, muerte barata.** Se adopta literal: nunca explicar, nunca castigar experimentación. El castigo es bloqueo mental.
4. **Libertad real con orden sugerido.** Se adopta: ir a casi cualquier sitio desde el inicio; la dificultad y habilidades requeridas sugieren orden.
5. **Gramática de room:** legible en 3 s, al menos dos salidas, punto focal, memorizable por forma, ritmo alternado, economía de objetos entre rooms, regla de separación. Todo de `dualis__history.md Parte I §2`.
6. **Tipología de rooms (8 tipos):** transición, observación, precisión, recompensa, riesgo, descubrimiento, combinación, puzle puro. DUALIS las usa todas, con peso mayor en combinación y descubrimiento, menor en precisión arcade.
7. **Patrones reutilizables como lenguaje:** plataforma elevada aparentemente inalcanzable, objeto brillante como guía sin tutorial, patrullas legibles, puzle en dos fases (observar→ejecutar), secreto visual por ángulo. Se adoptan como vocabulario, no como copia.
8. **Técnica isométrica:** proyección 2:1 dimetric, orden pintor atrás→adelante, colisión objeto-vs-objeto sin tilemap, habitaciones como unidades cerradas, 50 Hz lógica fija. Ver documento técnico. De los repos se toma el *cómo funciona*, no el *qué contiene*.
9. **Sensación ¡ajá! como métrica de calidad.** Si una room no produce comprensión inevitable-una-vez-vista, se corta.

### 7.2 Cómo se traslada a moderno (decisiones DUALIS)

- Sin mapa auto, pero con landmarks que el jugador recuerda.
- Sin misiones, pero con objetivos emergentes autoimpuestos.
- Sin diálogos, pero con lenguaje corporal.
- Sin castigo por muerte, pero con consecuencia narrativa (la estación recuerda).
- Sin bolsas con agujeros como impuesto, sino Transformar una-vez-por-room como decisión.

---

## 8. Elementos descartados

Explícitamente no van a DUALIS, aunque estén en Head Over Heels o en borradores de `HEAD OVER HEELS 2026`. Esta lista es filtro de revisión: si una propuesta los reintroduce, debe justificarse contra la biblia.

1. **Disparo / combate letal.** Head disparaba. Uno no dispara. No hay proyectiles ofensivos, ni HP de enemigos, ni farmeo.
2. **Vidas BCD y game over por conteo.** Descartado. Muerte barata + recuerdo de estación. Game over solo como renuncia narrativa, no por contador.
3. **Coronas / coleccionables de poder / puntuación.** Descartado. Progresión = comprensión. Secretos = habilidades-comprensión, atajos, historia. Nada acumulable por puntos.
4. **Bolsa con agujeros como impuesto de inventario.** Descartado como sistema global. Sustituido por Transformar 1×/room.
5. **Teletransportadores como atajos arbitrarios.** Descartado. Los atajos en DUALIS son espaciales y conceptuales (sincronizar máquinas, puerta que se abre al ignorarla), ganados por comprensión, no cabinas.
6. **Interruptor remoto genérico “activa puerta en otra room”.** Descartado como patrón abusado. Solo permitido si la conexión es legible diegéticamente (máquinas visibles, ecos, sonido) y no obliga a backtracking ciego.
7. **Tutoriales, mapas auto, quest markers, Codex explicativo.** Descartados por principio P3/P8.
8. **Rooms de relleno / transición vacía.** En HoH las transiciones pausan ritmo. En DUALIS incluso la transición debe enseñar, sorprender o revelar. Si solo conecta, se fusiona o se corta.
9. **Puzles de reflejos puros / frame-perfect encadenado.** Precisión existe (saltos milimétricos) pero nunca como puerta principal de región. Siempre hay vía de comprensión alternativa o margen generoso.
10. **Backtracking por olvido.** Si hay que volver, es porque el mundo cambió (agua, sincronía, noche/día conceptual), no porque faltó llave. Prohibido “vuelve con objeto X”.
11. **Fusión / intercambio de habilidades como botón spameable.** Momentos 5/13/31 de listas de 25/50 son eventos rituales de room, no toggle global. Si se vuelve botón, destruye identidad.
12. **Secretos que exigen grind externo** (morir 10/100 veces, hora real del día, día real). La lista de 25 secretos de history contiene ideas brillantes pero varias son anti-DUALIS por exigir metajuego punitivo o reloj real. Se conservan como inspiración filtrada: valen los que requieren observación, experimentación y paciencia diegética; se descartan los que piden repetición ciega o calendario.
13. **Nombres Cabeza/Tacón, planetas, El Que Fue como lore importado.** La Parte II de history usa esos nombres como placeholder de estudio. En DUALIS son Uno, Dos, El Nudo, Entidad Original. No se importan planetas ni bestiario nominal de HoH.
14. **Estética “HD remake con clash”.** Se estudia paleta por room de HoH como lección (tinta base + highlights), pero DUALIS es pintado a mano contemporáneo, no emulación Spectrum.

---

## 9. Filosofía de puzzles

### 9.1 Definición operativa

Un puzle DUALIS es una **relación malentendida** entre Uno, Dos y la room, que al comprenderse se vuelve inevitable. No es un obstáculo de ejecución ni un candado de inventario.

Estructura ideal (4 beats):

1. **Entrada legible (3 s):** ves punto focal, entiendes qué hay.
2. **Experimentación segura:** pruebas combinaciones sin miedo. El mundo responde con feedback legible.
3. **¡Ajá!:** ves la relación (el péndulo bloquea si lo fijas; el espejo miente salvo reflejo; el eco repite en 5 s y puedes usarlo).
4. **Salida doble:** una obvia, una secreta. La secreta recompensa haber entendido de más.

### 9.2 Familias canónicas (de concept §6, vinculantes como repertorio inicial)

- **Físicos:** plataforma que no existe (bloque temporal 5 s + salto + carrera), péndulo roto (fijar vs dejar oscilar bloquea otra ruta).
- **Espaciales:** sala que gira (techo como acceso), espejo roto (reflejo indica salida, romper abre).
- **Temporales:** eco (+5 s repetición usable), cuenta atrás (10/60 s con reparto dentro/fuera).
- **Cooperativos:** puente humano (3 s), lanzamiento con rebote y recogida.
- **Observación:** sombra equivocada (congelar para ver origen), patrón oculto (mirar a otro lado, Dos guía).
- **Ambientales:** gravedad cambiante cada 20 s, aire que falta con burbuja para uno (turnarse).

Cada familia debe tener al menos 3 variaciones no obvias antes de considerarse “cubierta”. Variar no es cambiar skin; es invertir la relación (ej.: eco que ayuda → eco que bloquea si no lo gestionas).

### 9.3 Reglas de buen puzle

- Resoluble con lo que el jugador ya puede comprender (nunca exige poder futuro).
- Nunca exige una habilidad que no tenga; solo comprensión que aún no tiene.
- Dos fases: observar, luego ejecutar. Nunca todo de golpe.
- Si fallas, entiendes por qué. Sin “muerte injusta que enseña”.
- Si lo resuelves por accidente, debes poder reconstruir por qué funcionó (legibilidad retrospectiva).
- Un puzle = una idea. Si necesita dos ideas nuevas a la vez, son dos rooms.

### 9.4 Dificultad sin números

La dificultad es **distancia conceptual**, no daño ni tiempo:

- Corta: combinación vista recientemente en otro contexto.
- Media: inversión de patrón conocido (puerta que se abre si la ignoras).
- Alta: requiere usar eco/transformación/gravedad de forma no literal + cooperación estrecha.

Siempre hay otra región adonde ir. El bloqueo local nunca es bloqueo global.

### 9.5 Los 25 momentos (canon de referencia)

De concept §9, asumidos como banco de momentos memorables a prototipar, no como checklist obligatorio. Todo momento debe pasar filtro P4+P5+§8:

Paredes que se mueven al saltar, biblioteca que se reorganiza al parpadear, torre que gira, péndulo-lanzadera, intercambio temporal Uno↔Dos, espejo con solución ya resuelta, tiempo detenido si ambos quietos, plantas que crecen adonde miras, enemigos = acciones pasadas, ascensor de pisos diferentes, lava segura si no la miras, reloj regional, fusión temporal, laberinto que se resuelve dejándolo, objetos con opiniones, vacío sin gravedad, sonido-como-mapa, archivo de decisiones, separación con comunicación por acciones, espejo de vidas sin encuentro, salida detrás de ti, fallar deliberadamente, tiempo al revés, trato de la Entidad, elección final fusión/separación.

El novato error sería implementarlos los 25. La biblia exige: prototipar 8–10, quedarse con 4–5 que produzcan ¡ajá! real en playtest ciego sin explicación.

---

## 10. Roadmap conceptual

Sin código, sin fechas cerradas. Fases de pensamiento y validación. El roadmap técnico va en `dualis_technical_architecture.md`.

### Fase 0 — Fundación (este documento + arquitectura)

- Congelar biblia v1.0 y arquitectura v1.0. Criterio de salida: cualquier lector puede explicar en 2 minutos qué es DUALIS sin decir “como Head Over Heels pero…”.
- Definir glosario cerrado: Uno, Dos, El Nudo, Entidad Original, Ecos, Bibliotecarios, Jardineros, Nominadores, Observar, Transformar, Marca temporal, Vínculo 10u.

### Fase 1 — Gramática mínima (papel + maqueta)

- 5 rooms en papel que cubran: montar, lanzar, congelar-para-cruzar, transformar-para-usar, eco.
- Cada room en ficha: entrada 3 s (dibujo), desarrollo, ¡ajá!, dos salidas, qué enseña, qué prohíbe.
- Playtest mental: ¿se puede leer sin texto? ¿tiene dos salidas? Si no, se corta.

### Fase 2 — Vertical slice conceptual (una región)

- El Vestíbulo completo en diseño (no código): 8–12 rooms, incluyendo puerta de separación dolorosa.
- Debe enseñar moverse/saltar/correr/vínculo sin una sola palabra.
- Métrica: jugador ciego entiende vínculo 10u sin que se lo digan.

### Fase 3 — Expansión por regiones

- Biblioteca Húmeda y Taller de los Ecos diseñados. Cada una con identidad mecánica propia + momento rompe-reglas.
- Validar que libertad real no rompe comprensión: grafo de dependencias por conocimiento, no por llaves. Si una región exige otra, debe ser por “no entenderás”, nunca por “no tienes objeto”.

### Fase 4 — Jardín + Torre (riesgo alto)

- Gravedad direccional y nominación son los sistemas más frágiles. Prototipo conceptual + pruebas de legibilidad. Si confunden, se simplifican antes de código.
- Definir rituales de fusión/intercambio como eventos únicos, con reglas de no repetición.

### Fase 5 — Archivo + Núcleo (cierre)

- Archivo de lo que no fue: definir qué decisiones rastrea (sin sistema de karma numérico) y cómo altera final por comprensión.
- Núcleo: combinar todas las familias sin introducir mecánica nueva. El clímax no enseña; examina.
- Cierre de finales: escribir elecciones sin “final bueno/malo”.

### Fase 6 — Poda

- Aplicar §8 y P4 a todo. Cortar al menos 20% de rooms/puzles. Si todo sobrevive, no se podó bien.
- Consolidar paletas, bestiario comportamental y secretos que merezcan la pena (observación, experimentación, paciencia diegética).

### Criterios de avance entre fases

1. ¿Un jugador nuevo siente curiosidad sin que le digan adónde ir?
2. ¿Resuelve sin que le expliquen?
3. ¿Recuerda cada room por su forma al día siguiente?
4. ¿Quiere a Uno y Dos sin que hablen?
5. ¿Puede describir lo aprendido como comprensión, no como “conseguí X”?

Si alguna respuesta es no, no se avanza.

---

## Apéndice A — Trazabilidad a fuentes

- Visión, premisa, tono, diorama, 7 regiones, personajes y poderes, 25 momentos, familias de puzles, anti-patrones (tutorial, mapa, misiones, puntuación, castigo): `dualis_concept.txt` §§1–12.
- Reglas invisibles ×10, 8 tipos de room, patrones, errores evitados ×10, memorable, sin-tutorial ×3 estrategias, recompensa ×4, sorpresa ×3, enganche ×5: `dualis__history.md` Parte I.
- Parte II de history (HoH2026 con Cabeza/Tacón, 50 rooms, 50 puzles, 25 secretos, 25 mecánicas) se usa como banco de ideas filtrado por §8, no como canon nominal.
- Repos HoH: solo lecciones estructurales (§7) y base técnica (proyección, painter, objeto-vs-objeto, 50 Hz, dispatch). Nada de lore, planetas, sprites o texto se importa.

## Apéndice B — Glosario canónico

- **Uno / Dos:** mitades de una mente. No “personajes elegibles”.
- **El Nudo:** estación-organismo en asteroide hueco.
- **Entidad Original:** mente rota que habita el Nudo.
- **Vínculo:** límite 10u, sufrimiento por separación.
- **Observar / Transformar / Marca temporal:** poderes cognitivos, no armas.
- **Room:** unidad cerrada de diseño. Siempre con función y dos salidas.
- **¡Ajá!:** métrica de calidad. Sin ¡ajá!, no hay room.

*Fin de la biblia v1.0. Lo que no esté aquí, no existe todavía.*
