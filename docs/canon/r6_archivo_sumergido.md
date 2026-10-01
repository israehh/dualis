# R6 — ARCHIVO SUMERGIDO

**Continuidad de canon:** “Archivo Sumergido” es la identidad propuesta para R6, llamada “Archivo de lo que no fue” en el world plan y en el diseño R5. Es la misma región: su función canónica de confrontar variantes de patrones conocidos se expresa aquí como lectura de huellas y consecuencias espaciales.

**Versión:** 1.0 — Diseño canónico  
**Estado:** Diseño. No implementa código, rooms, tests ni datos.  
**Fuentes:** `docs/canon/dualis_world_plan.md` (§§7, 10–16), `docs/canon/dualis_room_language.md`, `docs/canon/r5_torre_nombres.md` y `docs/world_state_f35.md`.  
**Principio:** comprender > dificultad.

---

## 1. Visión general

R6 desarrolla **MEMORIA, RASTRO, PERSISTENCIA, ECO y HUELLA** como relaciones espaciales observables, nunca como información que el jugador recoja o consulte.

- R1 enseñó el vocabulario.
- R2 mostró sus variaciones.
- R3 sintetizó patrones.
- R4 invirtió la lectura del espacio.
- R5 invirtió la atribución: quién sostiene a quién.
- R6 pregunta qué cambia en la lectura de un lugar después de que algo haya ocurrido allí.

La respuesta no es una historia escondida. Es una forma visible en el espacio: una interrupción en el sedimento, un puente que conserva el aspecto que DOS le dio, una oscilación que vuelve a pasar por el mismo lugar. El jugador deduce el antes a partir del ahora y usa esa lectura para cooperar.

**Límite vinculante de “memoria”.** No se guarda el historial de acciones del jugador, no se transportan recuerdos entre habitaciones y no existe progreso persistente nuevo. Una transformación deja una diferencia legible durante la visita actual; al abandonar y volver a la room, el estado consumible se restaura como dicta la persistencia suave existente. Los rastros fijos del entorno son composición espacial, no registros de partidas anteriores.

R6 no incorpora verbos. Reutiliza exclusivamente OBSERVE, TRANSFORM, MOUNT y LINK, más los patrones ya existentes. No requiere documentos, diálogo, texto explicativo, inventario, llaves, poderes, IA, gravedad, world_z ni sistemas nuevos.

**Fantasía en una frase:** el agua no cuenta lo sucedido; deja el espacio dispuesto para que UNO y DOS lo comprendan.

## 2. Fantasía e identidad visual

El Archivo Sumergido no contiene estanterías ni documentos. Es una arquitectura inundada donde las superficies conservan diferencias de contacto: polvo desplazado, líneas de agua quietas, zonas protegidas, bordes lavados y pares de marcas. La inundación se expresa por materia y composición, no por una simulación de agua.

La sala debe leerse en pocos segundos. Cada rastro contrasta con una superficie cercana que no fue alterada. Las marcas nunca son escritura, símbolos que haya que traducir ni instrucciones: son consecuencias físicas legibles por su forma, dirección, repetición o ausencia.

**Materia y paleta propuestas:** piedra oscura saturada, cal apagada, depósitos verdes de agua quieta y pequeños reflejos fríos. El acento regional es sedimentario, no tecnológico. La silueta general conserva la arquitectura isométrica existente; la lógica permanece cartesiana y toda altura es exclusivamente visual.

La huella importante tiene una causa cercana y visible. No aparece de pronto ni exige pixel hunting. El fenómeno que se mueve repite un recorrido completo, con ritmo amable. La iluminación y el contraste ayudan a leer el rastro, pero no lo convierten en una interfaz ni en un marcador.

**Regla de salida de la región:** cada habitación ofrece una salida obvia que confirma la comprensión y una segunda ruta menos evidente, descubierta al leer una huella. La segunda no es necesaria para completar la campaña ni lleva a un hub, llave, coleccionable o estado externo. Ambas se mantienen dentro de la continuidad prevista y no añaden destinos fuera del grafo aprobado. El formato actual de blueprint modela una salida principal; antes de implementar la salida secundaria deberá verificarse una representación compatible con la arquitectura. No se debe fingir una segunda salida como un segundo destino si el tránsito actual no puede distinguirlas.

## 3. Qué aporta respecto a R5

R5 preguntaba **quién hace qué**. R6 pregunta **qué evidencia deja esa relación en el espacio**.

R6 no convierte la identidad de R5 en recuerdos narrativos ni en objetos. La “memoria” es lectura física presente. Un personaje observa; el otro transforma; el cambio queda visible durante la visita. Un eco ambiental repite su propia conducta, no copia una acción del jugador. El montaje y el vínculo siguen siendo los mismos de R1–R5.

El avance conceptual es:

1. Reconocer una huella preexistente.
2. Leer por contraste qué parte del espacio fue protegida o recorrida.
3. Transformar algo y notar que su nueva forma persiste durante la visita.
4. Distinguir una repetición ambiental de una marca fija.
5. Cooperar usando a la vez el rastro, su eco y la posición del dúo.
6. Completar una síntesis en la que las acciones se entienden por sus consecuencias, no por una explicación.

La región no promete persistencia entre rooms. Si el jugador sale, el runtime y los actores locales siguen el reset previsto. La memoria que queda es comprensión del jugador; no un dato guardado por el juego.

## 4. Uso de OBSERVE / TRANSFORM / MOUNT / LINK

**OBSERVE — detener para comparar.** UNO congela un fenómeno existente y permite leer una relación que el movimiento ocultaba: alineación, dirección, separación o fase. Observar no revela un archivo ni activa información remota. La duración y el cooldown siguen siendo los existentes; ninguna solución exige precisión de reloj real.

**TRANSFORM — dejar una forma.** DOS transforma una sola vez un objeto que anuncia su affordance. El puente, step o plataforma resultante cambia la lectura y el recorrido de la habitación. Esa forma permanece durante la visita actual y puede servir como referencia espacial. No se conserva al salir ni se lleva a otra room.

**MOUNT — sostener la lectura con el cuerpo.** El gesto no cambia: UNO se monta sobre DOS. La composición de los dos cuerpos contrasta con las marcas del suelo, permite alcanzar la salida existente y hace visible una relación de escala o apoyo. No se usa como salto, elevación lógica ni transporte separado.

**LINK — confirmar confianza espacial.** CONNECTED sigue significando cercanía; TENSION, confianza a distancia; LIMIT no abre salidas. Una o dos rooms pueden contrastar una lectura compartida con el dúo repartido en una salida ancha, mediante el gate LINK ya existente. Una implementación futura solo podrá añadir requisitos declarativos compatibles con `link_gate`; no necesita un estado nuevo. No se hace de LIMIT una mecánica de memoria.

## 5. Progresión pedagógica completa

| Room | Idea única | Patrón existente | Dificultad |
|---|---|---|---|
| R6_01 | La huella orienta | PATTERN_OBSERVE_TO_CROSS | corta |
| R6_02 | La ausencia mide | PATTERN_HEIGHT | corta |
| R6_03 | La transformación deja forma | PATTERN_TRANSFORM_TO_REACH | media |
| R6_04 | El eco repite, no recuerda | PATTERN_TIMED_WINDOW | corta |
| R6_05 | El rastro necesita un testigo | PATTERN_SHARED_PASSAGE | media |
| R6_06 | El apoyo conserva una relación | PATTERN_HEIGHT | corta |
| R6_07 | La marca se reconoce a distancia | PATTERN_TRANSFORM_TO_REACH + LINK TENSION | media |
| R6_08 | El lugar se lee por lo que falta | PATTERN_OBSERVE_TO_CROSS | corta |
| R6_EXAM | Las cuatro acciones dejan una lectura común | PATTERN_TRANSFORM_TO_REACH + observable (ExamRuntime) | media |

El ritmo de las ocho rooms es **corta, corta, media, corta, media, corta, media, corta**. Cada patrón ya existe. Repetir un patrón no autoriza repetir su solución: cada ficha cambia qué relación espacial se observa y qué entiende el jugador.

La progresión es demostración pasiva → experimentación segura → combinación forzada. Las marcas y los fenómenos no castigan un intento equivocado: permiten reconstruir por qué la lectura no encajó. La salida secundaria recompensa una comprensión excedente, nunca bloquea la salida principal.

## 6. Diseño de habitaciones

Convención común: cada ficha declara una salida principal de avance y una ruta secundaria de comprensión. La secundaria no exige acción nueva ni progreso global. Si no puede representarse como ruta espacial distinta hacia una transición ya permitida, no se implementará hasta resolver esa limitación de representación; no se sustituirá por una llave, selector o teletransporte.

### R6_01 — La Orilla Conservada

**Idea:** la huella orienta. **Patrón:** PATTERN_OBSERVE_TO_CROSS. **Dificultad:** corta.

**Intención.** Enseñar a distinguir una marca fija de un fenómeno que pasa sobre ella. La habitación no explica quién dejó el rastro; solo permite ver hacia dónde conduce.

**Punto focal.** Una línea clara interrumpida por depósitos oscuros. Un fenómeno móvil recorre lentamente la misma franja, como una oscilación que deja visible el contraste al detenerla.

**Recorrido esperado.** El jugador intenta cruzar siguiendo el movimiento y ve que cambia de lado. UNO observa; al congelarse el fenómeno, la relación entre la línea fija y el paso queda clara. El dúo ocupa la salida.

**Solución real.** OBSERVE para congelar la referencia móvil y cruzar juntos guiándose por la huella fija.

**Posibles errores.** Confundir el movimiento con el rastro; intentar salir antes de observar; cruzar con un solo personaje.

**Momento ¡Ajá!.** La marca no se movía; era el agua la que pasaba sobre ella.

**Salidas.** Principal: vano alineado con la continuación de la huella. Secundaria: paso bajo una cornisa, insinuado por el mismo depósito, que vuelve a la continuidad sin abrir otra región.

**Reglas verificadas.** R1, R2, R5, R6, R7, R8, R12, R19, R22, R24.

**Riesgos.** Que la marca parezca una flecha o texto. Debe leerse como materia y contraste, no como iconografía de instrucciones.

### R6_02 — La Medida Ausente

**Idea:** una ausencia permite medir lo que estuvo protegido. **Patrón:** PATTERN_HEIGHT. **Dificultad:** corta.

**Intención.** Introducir la memoria como comparación espacial, no como objeto: una superficie limpia bajo un saliente contrasta con el sedimento alrededor.

**Punto focal.** Un step bajo una franja limpia de pared; el resto conserva un borde de depósito visible. El desnivel sigue siendo visual, y la salida existente solo se completa con UNO montado sobre DOS.

**Recorrido esperado.** El dúo prueba la salida a pie y no la alcanza. Lee el borde limpio como continuación de la altura del apoyo. UNO monta sobre DOS; juntos llegan a la salida.

**Solución real.** MOUNT y desplazamiento conjunto hasta la salida. La marca sirve para anticipar la relación de altura; no se transforma ni se recoge.

**Posibles errores.** Leer la zona limpia como decoración; separar el dúo antes de alcanzar la salida.

**Momento ¡Ajá!.** La pared guarda la altura sin guardar nada.

**Salidas.** Principal: vano a la misma altura visual que la franja limpia. Secundaria: un paso lateral visible desde la posición elevada que conduce al mismo enlace de campaña.

**Reglas verificadas.** R1, R2, R5, R6, R7, R9, R12, R15, R22, R24.

**Riesgos.** Parecer otro HEIGHT genérico. La diferencia con R5_02 es que la altura no atribuye quién abre: la evidencia del espacio permite leer cuánto falta antes de montar.

### R6_03 — El Umbral que Permanece

**Idea:** transformar deja una forma visible durante la visita. **Patrón:** PATTERN_TRANSFORM_TO_REACH. **Dificultad:** media.

**Intención.** Primera experiencia directa de persistencia local. La transformación no es un destello que se olvida: el objeto queda en una disposición distinta mientras el dúo termina de cruzar.

**Punto focal.** Un puente incompleto con una cara seca y otra cubierta de sedimento. La affordance de TRANSFORM se comunica por forma y contraste antes de necesitarla.

**Recorrido esperado.** DOS transforma el puente. La nueva forma continúa visible mientras ambos se desplazan a la salida. El jugador puede mirar atrás y usar el contraste para reconstruir qué cambió.

**Solución real.** TRANSFORM con DOS; después, llevar a UNO y DOS juntos a la salida. El estado transformado dura en esa visita, no entre entradas a la room.

**Posibles errores.** Esperar que el puente se active por observar; intentar transformar varias veces; creer que el juego guardó la forma globalmente.

**Momento ¡Ajá!.** Lo que hice sigue aquí; no tengo que llevarlo conmigo.

**Salidas.** Principal: paso sobre el puente transformado. Secundaria: una franja antes oculta por la silueta del puente revela un recorrido alternativo hacia el mismo destino.

**Reglas verificadas.** R1, R2, R4, R5, R6, R7, R10, R11, R12, R19, R22, R24.

**Riesgos.** Confundir permanencia durante la visita con persistencia de save. La sala debe dejar clara la primera; la reentrada restaura el estado local como en el resto del juego.

### R6_04 — El Eco de la Columna

**Idea:** un eco ambiental repite su propio recorrido; no reproduce acciones del jugador. **Patrón:** PATTERN_TIMED_WINDOW. **Dificultad:** corta.

**Intención.** Separar repetición de memoria. El fenómeno retorna al mismo lugar con un ritmo visible; la pista está en el intervalo que vuelve, no en una acción pasada del jugador.

**Punto focal.** Una columna marcada por depósitos a dos alturas y un observable temporizado que reaparece en el mismo arco. No hay agua dinámica ni cuenta atrás oculta.

**Recorrido esperado.** El jugador observa una repetición completa, solicita OBSERVE y congela el fenómeno en una fase legible. El dúo cruza a la salida durante esa observación.

**Solución real.** Leer el ciclo sin prisa, congelarlo con OBSERVE y llevar a ambos a la salida mientras el fenómeno está congelado.

**Posibles errores.** Tratar el primer paso como evento único; correr antes de reconocer el retorno; esperar que el fenómeno recuerde el movimiento de UNO o DOS.

**Momento ¡Ajá!.** No volvió por nosotros; siempre volvía.

**Salidas.** Principal: vano al final del arco visible. Secundaria: una hendidura alineada con la segunda marca, accesible tras entender la repetición y conectada con el mismo avance.

**Reglas verificadas.** R1, R2, R5, R6, R7, R8, R12, R14, R19, R22, R24.

**Riesgos.** Exigir sincronía exacta. El ciclo debe ser generoso y la solución se basa en congelar un estado visible, no en acertar un instante de reloj.

### R6_05 — La Cámara del Testigo

**Idea:** una huella se vuelve significativa cuando se compara con un fenómeno observado. **Patrón:** PATTERN_SHARED_PASSAGE. **Dificultad:** media.

**Intención.** Combinar OBSERVE y TRANSFORM ya aprendidos sin añadir un verbo. El jugador no reconstruye el pasado: alinea una evidencia presente con una forma que DOS puede transformar.

**Punto focal.** Una sombra móvil cruza una marca sedimentada y un puente corto permanece incompleto en el mismo eje. Se perciben como una sola relación, no dos objetivos.

**Recorrido esperado.** Intentar transformar antes de observar produce ROOM_DENIED, consecuencia local y comprensible. UNO congela el fenómeno; DOS transforma el puente; el dúo ocupa la salida común.

**Solución real.** OBSERVE → TRANSFORM → ambos cruzan por el paso compartido.

**Posibles errores.** Transformar primero; usar la marca fija como si fuera el fenómeno; cruzar con un solo personaje.

**Momento ¡Ajá!.** La marca no decía qué hacer; me dejó comprobar cuándo hacerlo.

**Salidas.** Principal: vano atravesando el puente común. Secundaria: borde seco que solo se reconoce al quedar congelada la sombra y que devuelve al mismo destino.

**Reglas verificadas.** R1, R2, R5, R6, R7, R8, R10, R12, R15, R16, R22, R24.

**Riesgos.** Que sombra y puente se conviertan en dos focos. Se componen como una pareja única: sombra sobre la huella y puente en la continuación de esa misma línea.

### R6_06 — El Apoyo Bajo el Sedimento

**Idea:** sostener también conserva una relación que el espacio permite leer. **Patrón:** PATTERN_HEIGHT. **Dificultad:** corta.

**Intención.** Releer MOUNT tras la transformación y el testigo: DOS no carga un recuerdo, sostiene a UNO en relación con una marca que solo se ve desde arriba.

**Punto focal.** Dos marcas paralelas en una cornisa visual; desde abajo parecen una sola mancha. La salida queda en altura visual y se alcanza con el dúo montado.

**Recorrido esperado.** A pie, la composición no se entiende completa. El jugador monta a UNO; desde la posición elevada, las marcas se distinguen como una pareja. El dúo sigue montado hasta la salida.

**Solución real.** MOUNT y atravesar juntos la salida. No hay segundo salto ni cambio de altura lógica.

**Posibles errores.** Buscar un objeto que recoja la marca; desmontar antes de que ambos entren en la salida.

**Momento ¡Ajá!.** DOS no me llevó a la memoria: me sostuvo para poder verla.

**Salidas.** Principal: salida elevada visualmente junto a las dos marcas. Secundaria: borde de la cornisa que ofrece un acceso más discreto al mismo enlace.

**Reglas verificadas.** R1, R2, R5, R6, R7, R9, R12, R15, R22, R24.

**Riesgos.** Repetición con R6_02 o R5_02. Aquí el foco no es medir una altura ni decidir quién abre; es que la relación de dos marcas solo resulta legible desde la posición cooperativa del montaje.

### R6_07 — El Vínculo en la Marca

**Idea:** dos posiciones distantes pueden pertenecer a una misma huella si el vínculo se mantiene. **Patrón:** PATTERN_TRANSFORM_TO_REACH + LINK TENSION. **Dificultad:** media.

**Intención.** Clímax previo al cierre amable. El jugador ya sabe leer marcas y estados transformados; ahora reconoce que una forma compartida no exige que UNO y DOS ocupen el mismo punto.

**Punto focal.** Un puente ancho con un depósito continuo y dos interrupciones simétricas, una en cada extremo. La salida permite que ambos estén dentro separados en TENSION. El elemento transformable anuncia que su forma completa la línea.

**Recorrido esperado.** DOS transforma el puente. El dúo ocupa extremos distintos de la salida y prueba la distancia. CONNECTED confirma el runtime pero no abre el gate; al separarse hasta TENSION, la línea y las marcas se leen de una vez.

**Solución real.** TRANSFORM, completar el runtime con ambos presentes y abrir la salida en TENSION mediante el gate LINK existente. LIMIT nunca sirve.

**Posibles errores.** Confundir distancia con ruptura; permanecer CONNECTED; transformar y dejar fuera a uno de los dos.

**Momento ¡Ajá!.** La huella sigue entera aunque nosotros no estemos juntos en el mismo extremo.

**Salidas.** Principal: vano ancho entre las dos marcas. Secundaria: paso lateral que revela la continuidad del sedimento al alcanzar la separación legible; retorna a la misma progresión.

**Reglas verificadas.** R1, R2, R5, R6, R7, R12, R15, R18, R19, R22, R24.

**Riesgos.** Gate geométricamente imposible o duplicación de R4_05/R5_04. La sala debe comprobar TENSION y posiciones alcanzables conjuntamente; su diferencia es usar una forma transformada como línea común, no cruzar o llegar simultáneamente a una puerta ancha.

### R6_08 — El Lugar que Falta

**Idea:** una ausencia también deja una huella legible. **Patrón:** PATTERN_OBSERVE_TO_CROSS. **Dificultad:** corta.

**Intención.** Cierre sereno: no todo recuerdo es una marca añadida. A veces lo significativo es el espacio que permanece limpio alrededor de una forma.

**Punto focal.** Un fenómeno móvil recorre un muro y nunca cubre un rectángulo seco de tamaño suficiente para reconocer una forma ausente. Al observar, el contraste queda quieto; no se revela texto ni imagen oculta.

**Recorrido esperado.** El jugador sigue el movimiento y cree que la mancha es uniforme. UNO observa; la zona protegida y su relación con el vano se vuelven claras. Ambos avanzan sin transformar ni recoger nada.

**Solución real.** OBSERVE y cruzar juntos leyendo el límite entre superficie alterada y superficie preservada.

**Posibles errores.** Buscar un secreto por inspección de píxel; activar TRANSFORM sin affordance; separar al dúo.

**Momento ¡Ajá!.** Lo que falta también ocupa un lugar.

**Salidas.** Principal: vano en el espacio negativo que dibuja la zona protegida. Secundaria: un acceso visible desde el lado opuesto de esa forma, alternativa que conduce al mismo tramo siguiente.

**Reglas verificadas.** R1, R2, R5, R6, R7, R8, R12, R14, R19, R22, R23, R24.

**Riesgos.** Convertir la ausencia en acertijo abstracto. El contorno tiene que leerse en segundos y su relación con la salida debe ser inmediata al congelar el fenómeno.

## 7. Examen R6_EXAM — La Sala que Conserva

**Idea:** síntesis de las cuatro acciones existentes; ninguna idea nueva. **Patrón:** PATTERN_TRANSFORM_TO_REACH con observable + transformable → ExamRuntime existente. **Dificultad:** media.

**Intención.** El examen no pregunta qué objeto guardó el jugador. Comprueba si puede leer una evidencia, cambiar una forma, sostener al otro y confiar en el vínculo sin confundir huella con inventario.

**Punto focal.** Un fenómeno móvil recorre una franja de sedimento; un puente transformable ocupa su continuación; dos marcas en el vano permiten leer la llegada conjunta. La salida final es ancha y exige TENSION mediante el gate LINK existente.

**Recorrido esperado.** OBSERVE congela el fenómeno. TRANSFORM, permitido después de observar, cambia el puente. UNO y DOS se juntan para MOUNT y completan el runtime montados. Después se separan dentro del vano hasta TENSION. COMPLETED permanece pegajoso durante ese último ajuste, como en los exámenes previos.

**Solución real.** OBSERVE → TRANSFORM → juntar → MOUNT → completar → separar a TENSION en la salida.

**Posibles errores.** Transformar antes de observar (ROOM_DENIED); intentar completar sin montar; creer que la transformación se conservó antes de entrar; quedarse CONNECTED o llegar a LIMIT al abrir.

**Momento ¡Ajá!.** No tuve que guardar lo que hicimos. Bastó con entender lo que dejó.

**Salidas.** Principal: salida final que continúa hacia el extremo previsto de campaña. Secundaria: un paso discreto trazado por la forma transformada, comprensión excedente que desemboca en esa misma continuidad; no crea un hub ni una región intermedia.

**Reglas verificadas.** R1, R5, R6, R7, R9, R12, R15, R18, R19, R22, R24; world plan §11 (examen sin ideas nuevas).

**Riesgos.** Parecer R4_EXAM o R5_EXAM con otra piel. La diferencia debe ser de lectura y atribución —resultado que permanece, no identidad o rol— mientras la maquinaria continúa siendo la existente. No añadir un gate, paso o estado para diferenciarlo.

## 8. Riesgos

1. **Confundir huella con persistencia global.** El documento limita toda transformación recordable a la visita actual. No se serializa el progreso ni se guarda la acción del jugador.
2. **Convertir el eco en replay.** Los fenómenos solo repiten su propia conducta existente. Ningún sistema registra ni reproduce inputs.
3. **Agua como mecánica nueva.** La inundación es materia visual fija; no sube, empuja, ahoga, cambia gravedad ni altera colisiones.
4. **Lectura demasiado abstracta.** Cada evidencia debe tener una causa espacial visible, un contraste claro y una consecuencia comprobable. Si necesita texto, se rediseña.
5. **Focos múltiples.** En R6_05 sombra, marca y puente deben formar un único eje visual; de lo contrario, dividir la idea antes de implementar.
6. **Repetición de patrones.** Las rooms con el mismo patrón cambian la relación aprendida; playtests deben comprobar que la solución y el recuerdo verbal no sean intercambiables.
7. **TENSION imposible por geometría.** R6_07 y R6_EXAM requieren salida ancha que admita el estado y el gate a la vez. Validar distancias, salida y requisito LINK conjuntamente.
8. **Dos salidas frente al modelo actual.** El canon exige una salida obvia y otra menos evidente, pero los blueprints actuales exponen una sola `exit_rect`. La forma de representar una segunda ruta debe revisarse en una fase técnica separada; no añadir un selector, teletransporte, estado o mecánica para sortear esa limitación.
9. **Retorno y atajos pendientes.** El retorno desde R5_EXAM no está resuelto y DOOR TO BEFORE sigue pendiente. La integración R6 no debe asumir que el backtracking desde el examen anterior está solucionado ni insertar R6 como atajo entre regiones.
10. **Ritmo.** Mantener exactamente corta, corta, media, corta, media, corta, media, corta y un examen medio; ningún par de clímax consecutivos.

## 9. Integración con la campaña actual

La campaña aprobada termina en R5_EXAM. Según la regla de crecimiento del world plan §15, R6 solo puede añadirse en el extremo: nunca entre R1–R5.

La futura integración debe seguir F28/F33/F34:

- Mantener congelados los JSON existentes.
- Alojar el contenido R6 fuera de `data/blueprints/`, que permanece con 44 entradas congeladas.
- Añadir las rooms al cargador mediante el patrón de directorios ya establecido, en una fase de implementación explícita.
- Añadir las aristas de continuidad únicamente en `campaign.py`.
- Declarar, si se aprueba, los requisitos TENSION de R6 en la tabla de requisitos existente de `link_gate.py`; no crear un sistema de puertas.
- Verificar ida y vuelta, entradas seguras y llegada al nuevo terminal. El retorno específico desde R5_EXAM requiere decisión propia y no se arregla implícitamente en esta propuesta.
- Resolver la representación de la salida secundaria conforme al riesgo 8 sin modificar transit, runtimes o sistemas por sorpresa.

Este documento no aprueba ni implementa datos, gates, directorios ni cambios de cargador.

## 10. Preparación conceptual del NÚCLEO

R6 deja al jugador preparado para un examen final sin abrir un vocabulario nuevo:

- De R1 conserva el significado de OBSERVE, TRANSFORM, MOUNT y LINK.
- De R2 conserva la reinterpretación de patrones.
- De R3 conserva el orden y la síntesis.
- De R4 conserva una lectura espacial no literal.
- De R5 conserva la atribución entre UNO y DOS.
- De R6 conserva la capacidad de leer evidencia presente sin convertirla en objeto o dato persistente.

El NÚCLEO puede combinar esas comprensiones y ofrecer una elección ética o una salida doble, como establece el world plan, pero no necesita vidas, inventario, puntuación ni ideas nuevas. La elección debe ser comprensible por la disposición del mundo y no por diálogo.

La diferencia esencial: el jugador no llega al Núcleo con una colección de recuerdos. Llega sabiendo mirar lo que cambió, quién lo hizo, quién lo sostuvo y qué sigue siendo cierto cuando el dúo se separa.

---

## Resumen ejecutivo

- **Idea principal:** la memoria es una huella espacial legible; no un archivo de datos ni un registro de acciones.
- **Qué aprende el jugador:** observar la diferencia entre rastro y eco, transformar sin borrar la forma anterior de su lectura, cooperar usando evidencia presente y confiar en LINK sin necesitar estar siempre juntos.
- **Cómo prepara el Núcleo:** R6 completa la lectura del mundo como consecuencia física de acciones y consolida los cuatro verbos para una síntesis final sin ideas nuevas.
- **Riesgos de implementación:** evitar persistencia entre rooms o replay de inputs no existentes; mantener fenómenos y transformaciones dentro de runtimes actuales; validar TENSION con geometría; y resolver explícitamente la doble salida canónica frente al blueprint actual de una salida, sin introducir mecánicas ni alterar sistemas fuera de una fase aprobada.
