# DUALIS — Arquitectura del Motor

**Versión:** 1.0 — Puente entre canon e implementación
**Estado:** Diseño de arquitectura. Sin código, sin librerías, sin algoritmos.
**Obedece a:** `docs/canon/dualis_concept.md`, `dualis__history.md`, `dualis_design_bible.md`, `dualis_room_language.md`, `dualis_vertical_slice.md`, `dualis_rooms_vestibulo.md`, `docs/work/dualis_system_spec.md`.
**Límites:** solo responsabilidades, relaciones y flujo de datos.

---

## 1. Filosofía de arquitectura

**Simulación primero.** El mundo existe y avanza por sí mismo en pasos fijos. Lo que se ve y se oye es consecuencia, nunca causa. Ninguna decisión de presentación altera el estado simulado.

**Presentación desacoplada.** La capa que muestra dioramas, luz, sonido y señales solo observa. Puede quedarse atrás, repetirse o interpolarse sin romper la verdad del mundo. La simulación nunca espera a la presentación.

**Determinismo.** A igual intención del jugador y misma semilla de habitación, el resultado es idéntico y reproducible. El azar aparente nace de semilla local, no de momento de ejecución. Esto permite probar, repetir y validar diseño sin ambigüedad.

**Habitaciones como unidad.** La habitación cerrada es la unidad de carga, de significado y de validación. Todo lo que ocurre pertenece a una visita a una habitación. Nada relevante vive flotando entre habitaciones salvo la memoria narrativa.

**Sistemas pequeños y especializados.** Cada sistema sabe una sola cosa y la sabe bien: vínculo, observación, transformación, cooperación, interacción, habitación, memoria. Ningún sistema hace el trabajo de otro. La cooperación entre sistemas ocurre por eventos, no por invasión.

---

## 2. Capas del motor

**Core — latido y orden.** Responsable del paso fijo de simulación, del estado global, del bus de eventos y de la escena activa. No conoce habitaciones concretas, ni regiones, ni emociones. Solo sabe qué debe ejecutarse, en qué orden y en qué estado global estamos.

**World — verdad del lugar.** Responsable de la habitación activa, sus entidades, sus affordances y su región. Es la única capa que sabe dónde está cada cosa y qué significa cada relación espacial. No decide comportamiento; lo contiene.

**Systems — comportamiento.** Responsable de aplicar las reglas del canon sobre el mundo: medir el vínculo, congelar para leer, reinterpretar una vez por visita, montar y sostener, leer conducta de puertas, abrir y cerrar visitas, recordar. Cada sistema lee el mundo y propone cambios; ninguno toca presentación directamente.

**Presentation — lectura sensible.** Responsable de convertir estado en diorama legible: foco, affordance, ritmo, tensión del vínculo, respiración de puertas, huella de memoria. Solo escucha eventos y observa estado. Nunca escribe en el mundo.

**Persistence — memoria y continuidad.** Responsable de separar lo temporal de lo narrativo. Guarda comprensión, visitas y huellas; nunca guarda fotogramas ni posiciones intermedias como verdad. Restaura visitas sin castigo.

Relación entre capas: Core ordena, Systems razonan sobre World, Presentation observa, Persistence recuerda. El flujo de datos va de la intención del jugador hacia World a través de Systems, y de World hacia Presentation y Persistence mediante eventos.

---

## 3. Núcleo (Core)

**Game Loop — el latido.** Responsabilidad exacta: avanzar la simulación en pasos enteros y fijos, con tope por ciclo visible. Si la presentación se retrasa, se ejecutan pasos pendientes completos o se descartan con degradación suave, nunca medios pasos. No sabe qué es UNO ni qué es una puerta; solo sabe pulsar el siguiente paso.

**State Manager — el modo.** Responsabilidad exacta: custodiar el estado global (juego, observación, entrada, salida, muerte suave, elección futura) y sus transiciones permitidas. Ningún sistema cambia de modo por su cuenta; solicita transición y el gestor la concede o la niega según la tabla de estados. Es el único que puede congelar el mundo para lectura sin detener la mirada.

**Event Bus — el correo.** Responsabilidad exacta: transportar hechos ya ocurridos desde quien los emite hacia quien los escucha, sin devolver llamadas. Garantiza orden dentro del paso y entrega completa antes del siguiente paso. No interpreta, no filtra por conveniencia, no ejecuta comportamiento.

**Scene Manager — la estancia.** Responsabilidad exacta: activar, suspender y retirar habitaciones como unidades. Prepara la entrada (composición del lugar y colocación del dúo), declara la salida (vía obvia o menos evidente) y restaura la visita al reentrar. No conoce ideas de diseño; conoce visitas con principio y fin.

---

## 4. Mundo (World)

**Room — la estancia.** Conoce sus entidades, sus dos salidas declaradas, su foco y su región. No conoce otras habitaciones salvo por el nombre de sus salidas. No sabe qué valida ni qué enseña; eso pertenece a diseño, no al motor.

**Entity — lo que hay.** Conoce su posición en tres ejes, su tamaño, su postura y su estado propio. No conoce el estado global, ni la memoria narrativa, ni la intención del jugador. Su comportamiento lo decide su sistema, no ella misma.

**Affordance — lo que se intuye.** Conoce la relación entre una entidad y el dúo: si es usable, por quién y bajo qué condición de cercanía, postura o ritmo. No ejecuta el uso; solo lo anuncia de forma perceptible. No conoce poderes futuros ni visitas pasadas.

**Region — el tono.** Conoce el vocabulario de affordances permitido, la paleta de conductas y el momento de ruptura de sus propias reglas. No contiene habitaciones como datos técnicos; las agrupa como familia de sentido.

Relaciones: Region agrupa Rooms. Room contiene Entities. Cada Entity interactuable expone Affordance. Affordance es leída por Interaction System y presentada por Presentation. Ningún elemento del mundo emite eventos por sí mismo; los sistemas los emiten al interpretar el mundo.

Lo que NO conoce cada elemento: Room no conoce al jugador. Entity no conoce a otra Entity directamente. Affordance no conoce persistencia. Region no conoce estados globales.

---

## 5. Sistemas

**Link System — el vínculo.**
Entradas: posiciones de UNO y DOS, estado global. Salidas: nivel de tensión, señales de degradación. Eventos: tensión iniciada, tensión sostenida, vínculo restaurado. Dependencias: solo lectura de World y del estado global; ningún otro sistema.

**Observation System — la lectura.**
Entradas: solicitud de UNO, disponibilidad de uso en la visita, estado global. Salidas: congelación del mundo con mirada libre. Eventos: observación iniciada y finalizada. Dependencias: State Manager para el modo, Room System para la disponibilidad por visita. No mueve agentes.

**Transformation System — la reinterpretación.**
Entradas: cercanía de DOS a objeto elegible, affordance confirmada, disponibilidad por visita. Salidas: cambio de sentido del objeto dentro de la visita. Eventos: transformación gastada, visita restaurada al reentrar. Dependencias: World para elegibilidad, Room System para el límite por visita. Decisión siempre deliberada.

**Cooperation System — la relación.**
Entradas: proximidad, posturas, apoyo y ritmo de ambos agentes. Salidas: montaje sostenido, impulso con aterrizaje, paso conjunto temporal. Eventos: montaje iniciado y finalizado, lanzamiento y aterrizaje, puente formado y disuelto. Dependencias: Link System como condición, World como geometría. Nunca actúa por interruptor textual.

**Interaction System — la conducta.**
Entradas: affordances, presencia, impacto y ritmo sobre mecanismos visibles y puertas. Salidas: activaciones locales y respuestas de puertas. Eventos: puerta que acepta, puerta que se niega, mecanismo activado. Dependencias: World para affordance, Cooperation System cuando la conducta exige al dúo. Prohibida la activación ciega a distancia.

**Room System — la visita.**
Entradas: peticiones de entrada, salida y reentrada desde Scene Manager. Salidas: habitación activa compuesta, salidas declaradas, restauración de consumibles. Eventos: entrada, salida obvia, salida menos evidente, reentrada. Dependencias: World como contenido, Persistence como memoria de visitas. Garantiza una idea por habitación por construcción de datos, no por vigilancia.

**Memory System — el recuerdo.**
Entradas: eventos de visita, muerte suave y salidas. Salidas: huellas cosméticas y registro de comprensión. Eventos: huella depositada, comprensión registrada. Dependencias: escucha al Bus, escribe solo en Persistence. Nunca bloquea ni castiga; solo testimonia.

---

## 6. Entidades

**Protagonistas.** UNO y DOS. Diferencia: son los únicos con intención del jugador, vínculo y poderes. Todo lo demás existe en relación con ellos. Nunca son plataforma genérica ni enemigo.

**Geometría.** Suelos, cornisas, bloques, vanos. Diferencia: definen dónde se puede estar y a qué altura. No deciden nada; sostienen. Su verdad es apoyo y tamaño.

**Interactivos.** Objetos reinterpretables, mecanismos visibles, puertas con opinión. Diferencia: exponen affordance y responden a conducta. No piden inventario; piden presencia, ritmo o calma.

**Temporales.** Marcas, ventanas de ritmo, puentes conjuntos. Diferencia: existen con duración visible y expiran sin daño colateral. Preguntan oportunidad y sincronía, no velocidad.

**Narrativos.** Fragmentos, huellas, presencias como la Entidad. Diferencia: no se usan, se comprenden. Recontextualizan lo vivido y alimentan la memoria. Nunca bloquean el avance.

---

## 7. Flujo de una habitación

De la entrada a la salida, en orden exacto de sistemas implicados:

1. Scene Manager solicita entrada; Room System compone la visita desde World y declara foco y salidas.
2. State Manager entra en modo entrada; Presentation muestra el diorama y la affordance inicial.
3. State Manager pasa a juego; Game Loop inicia pasos fijos.
4. Cada paso: Link System mide el vínculo; Observation, Transformation y Cooperation actualizan según intención; Interaction System lee conductas; World resuelve apoyo y arrastre.
5. Los hechos viajan por Event Bus hacia Presentation (señales) y Memory System (huellas).
6. Ante cruce de salida, Room System declara vía obvia o menos evidente; Scene Manager ejecuta la transición.
7. Ante muerte suave, el modo correspondiente disuelve, pausa la amenaza y reaparece al dúo en el acceso con el vínculo restaurado.
8. Ante reentrada futura, Room System restaura consumibles de la visita y conserva comprensión.

Ningún paso salta a otro. Ningún sistema actúa fuera de su turno dentro del paso.

---

## 8. Eventos globales

Catálogo inicial. Quien emite solo anuncia hechos; quien escucha decide su respuesta sin devolver llamadas.

- LINK_TENSION. Emite Link System al superar el límite con histéresis. Escuchan Presentation (oscurecimiento y ralentización sensible) y Memory System (huella leve).
- LINK_RESTORED. Emite Link System al volver a cercanía segura. Escuchan Presentation y Cooperation System (reanudación plena).
- OBSERVE_BEGIN y OBSERVE_END. Emite Observation System. Escuchan State Manager (modo), Presentation (mirada libre) y Memory System.
- TRANSFORM_USED. Emite Transformation System al reinterpretar. Escuchan Presentation (cambio de sentido), Room System (agotamiento por visita) y Memory System.
- MARK_CREATED y MARK_EXPIRED. Emite Cooperation System o el responsable de la marca según System Spec. Escuchan Presentation y Cooperation System.
- MOUNT_BEGIN, MOUNT_END, BRIDGE_FORMED, BRIDGE_RELEASED. Emite Cooperation System. Escucha Presentation; World refleja el apoyo resultante.
- DOOR_ACCEPTS y DOOR_REFUSES. Emite Interaction System al leer conducta. Escuchan Presentation, Room System y Memory System.
- ROOM_ENTER, ROOM_EXIT, ROOM_REENTER. Emite Room System vía Scene Manager. Escuchan todos: Presentation recompone, Memory registra, poderes restauran.
- SOFT_DEATH y REAPPEAR. Emite el responsable de muerte suave. Escuchan State Manager, Presentation y Memory System.
- VISIT_RESTORED. Emite Room System al reentrar. Escuchan Transformation System y Presentation.

---

## 9. Persistencia

Qué se guarda: habitación actual y acceso de aparición, comprensión registrada por habitación y región, visitas y muertes suaves como conteo para huella, usos consumidos dentro de la visita activa, variante narrativa visitada cuando exista. Todo versionado y migrable.

Qué no se guarda: posiciones intermedias dentro del paso, estados de presentación, fotogramas, intenciones a medio gesto, duraciones restantes de marcas y puentes como verdad. Al cargar, la visita se recompone desde su inicio declarado, nunca desde un instante congelado.

Separación: el estado temporal pertenece a la visita y muere con la salida; la memoria narrativa pertenece a la estación y sobrevive. La memoria modula luz, polvo y ecos; jamás cierra puertas ni exige repetición. El borrado total está siempre disponible.

---

## 10. Restricciones arquitectónicas

- Sin dependencia circular entre sistemas; el orden del paso es acíclico y el Bus no devuelve llamadas.
- Sin lógica de comportamiento en presentación; solo observación y señal.
- Sin comportamiento oculto en entidades; toda conducta vive en su sistema y se anuncia por affordance.
- Sin acceso directo entre sistemas; toda coordinación pasa por World como lectura y por el Bus como hechos.
- Sin estado global manipulado fuera del gestor; los modos solo cambian por transición concedida.
- Sin habitación que conozca a otra salvo por salidas declaradas; sin atajos fuera del grafo.
- Sin poder gastado por accidente; todo consumo limitado nace de gesto deliberado y affordance previa.
- Sin persistencia de instante; solo visitas restaurables y memoria narrativa.
- Sin texto como requisito de comprensión; todo evento tiene señal perceptible en el mundo.
- Sin crecimiento silencioso: un sistema nuevo exige evento, dependencia declarada y lugar en el paso.

---

## 11. Árbol de proyecto recomendado

Solo nombres de carpetas y su responsabilidad. Sin archivos concretos.

- core. Latido, modos, correo de eventos y estancias. Nada de diseño concreto.
- world. Habitación activa, entidades, affordances y regiones como verdad del lugar.
- systems. Un subámbito por sistema: vínculo, observación, transformación, cooperación, interacción, habitación y memoria. Cada uno con entradas, salidas y eventos declarados.
- presentation. Lectura sensible del estado: diorama, foco, señales de vínculo y puertas, huellas. Solo observa.
- persistence. Memoria narrativa y continuidad de visitas. Separa lo temporal de lo recordado.
- data. Definiciones de habitaciones y regiones como datos versionables, una idea por habitación.
- validation. Comprobaciones de diseño derivadas del lenguaje: foco, doble salida, vínculo, affordance y restauración.
- docs. Canon y trabajo: este documento como puente, sin duplicar comportamiento.

*Fin de la arquitectura v1.0. Implementar fuera de estas responsabilidades es implementar fuera de DUALIS.*
