# DUALIS — Especificación de Sistemas (Contrato Diseño–Motor)

**Versión:** 1.0 — Contrato
**Estado:** Referencia obligatoria para programar el motor sin improvisar comportamiento.
**Obedece a:** canon (`dualis_concept`, history, design_bible, room_language, vertical_slice, technical_architecture como intención, no como implementación).
**Límites de este documento:** sin código, sin pseudocódigo, sin librerías, sin Python, sin Pygame. Solo comportamiento, estados, eventos, restricciones y relaciones.

---

## 1. Propósito

Este documento define qué hace cada sistema del juego desde el punto de vista del motor y cómo se relacionan entre sí.

No describe cómo se programa. Describe qué debe ocurrir, en qué orden, bajo qué condiciones y qué está prohibido que ocurra.

Si diseño y motor discrepan, este contrato decide. Si el contrato contradice al canon, el canon gana y el contrato se revisa con aprobación humana.

---

## 2. Principios inviolables

1. La unidad mínima de juego es el dúo, nunca el individuo.
2. Toda solución es cooperación dentro del vínculo; la alternancia por turnos no es solución válida.
3. El tiempo de simulación es discreto y determinista: a igual entrada y semilla, igual resultado.
4. La presentación nunca modifica la simulación; solo la observa.
5. Fallar informa y no destruye comprensión; ninguna muerte borra progreso de ideas.
6. Nada transformable aparece por sorpresa; todo poder limitado se gasta por decisión visible.
7. Ninguna puerta pide objeto, nivel ni contador; solo conducta o comprensión.
8. Reentrar restaura lo consumible de la visita sin castigo.

---

## 3. Modelo del mundo

El mundo se compone de habitaciones cerradas conectadas por salidas.

Cada habitación contiene:

- Dos agentes protagonistas: UNO y DOS.
- Un conjunto de entidades: bloques, plataformas, mecanismos rítmicos, puertas, objetos reinterpretables, marcas temporales y presencias.
- Una región de pertenencia que fija tono, affordances y un momento de ruptura de sus propias reglas.
- Dos salidas declaradas: una obvia y una menos evidente.
- Un foco único legible en los primeros segundos.

Cada entidad posee: posición en tres ejes, tamaño, postura, estado propio y affordance visible cuando es interactuable. Ninguna entidad posee puntos de vida ni poder de ataque.

---

## 4. Tiempo y ciclo de simulación

El motor avanza por pasos fijos de simulación. Cada paso ejecuta, en este orden:

1. Lectura de intención del jugador.
2. Actualización del vínculo y de los poderes del dúo.
3. Actualización de cada entidad según su comportamiento.
4. Resolución de movimiento, apoyo y arrastre.
5. Detección de eventos: activaciones, transformaciones, muertes suaves, cruces de salida.
6. Notificación a presentación y memoria de la estación.

Restricciones:

- La simulación nunca avanza ligada a la fluidez visual; si la presentación se retrasa, la simulación ejecuta pasos enteros pendientes con un tope, nunca pasos parciales.
- Observar detiene el mundo pero no la interfaz de lectura: el jugador puede mirar y planificar mientras el mundo está congelado.
- El azar, cuando exista, nace de una semilla por habitación y es reproducible.

---

## 5. Sistema dúo: UNO y DOS

### UNO

- Desplazamiento: salto preciso de arco controlable, caída predecible. No corre, no empuja cargas pesadas, no rompe.
- Papel: precisión, lectura y memoria. Espera y sostiene.
- Fragilidad: no resiste impactos como recurso; su fallo se trata como muerte suave, nunca como castigo.

### DOS

- Desplazamiento: carrera con aceleración e inercia, sin salto fino ni frenada en seco. Empuja bloques, activa por impacto y rompe solo tabiques designados.
- Papel: fuerza, oportunidad y reinterpretación. Mira antes de embestir.
- Imprecisión: no se le exige detenerse en marcas exactas como puerta de progreso.

### Control

- Un único dispositivo controla al agente activo; el cambio de activo es conveniencia, no jerarquía.
- Existe una acción conjunta contextual que, según proximidad y postura, propone montar, lanzar o sostener. Nunca exige combinaciones ocultas.
- El lenguaje corporal es comportamiento observable: espera, mirada, giro ante el sufrimiento del otro.

---

## 6. Vínculo permanente

Definición: distancia máxima permitida entre UNO y DOS. Superarla degrada la situación sin matar.

Comportamiento:

- Estado normal dentro del límite.
- Estado de tensión al superar el límite: oscurecimiento progresivo, ralentización de ambos y drenaje de estabilidad.
- Histéresis obligatoria: se entra en tensión a una distancia y se sale a una distancia menor, para evitar parpadeo en el borde.
- Excepción única de diseño: una sola puerta del Vestíbulo exige aceptar la tensión para comprenderla. No se repite como truco.

Eventos: entrada en tensión, salida de tensión, permanencia en tensión.

Restricciones: ninguna habitación exige romper el vínculo como solución habitual; toda solución cabe con ambos cerca.

---

## 7. Poderes cognitivos

### Observar (UNO)

- Efecto: congela el mundo durante una duración breve y fija para leer ritmos, sombras y patrones.
- No reposiciona agentes gratuitamente; permite mover la mirada y planificar.
- Uso limitado por visita a la habitación; se recarga al reentrar.
- Restricción: nunca es arma ni huida; es lupa temporal.

### Transformar (DOS)

- Efecto: reinterpreta un objeto elegible una vez por habitación (paso, apoyo, aliado temporal, bloqueo).
- La elegibilidad se comunica antes de necesitarse mediante forma, brillo o conducta.
- Irreversible dentro de la visita; reversible al reentrar.
- Restricción: gasto siempre deliberado, nunca accidental; sin confirmaciones textuales, solo colocación y gesto claro.

### Marca temporal (UNO)

- Efecto: deja un apoyo breve en el punto alto del salto, aprovechable por el dúo dentro de su ventana.
- Duración generosa, pensada para sincronía y no para reflejos.
- Restricción: no es plataforma permanente ni atajo universal; es oportunidad creada.

---

## 8. Cooperación

### Montar

DOS actúa como plataforma móvil; UNO hereda su movimiento más su propio salto. Relación espacial sostenida, no teletransporte. Si DOS se mueve, UNO acompaña.

### Lanzar

DOS imparte impulso a UNO; UNO vuela en arco, puede rebotar y debe aterrizar en apoyo válido. El fallo devuelve al punto de intento sin pérdida. En el Slice vertical el lanzamiento largo queda fuera; aquí se define el comportamiento para producción posterior.

### Puente y sostén conjunto

Ambos adoptan postura y generan un paso transitable durante una duración breve y visible. Exige simultaneidad y cercanía. Al expirar, el paso deja de existir sin daño colateral.

Restricción común: montar, lanzar y sostener se invocan por geometría y postura, nunca por interruptor textual ni menú.

---

## 9. Locomoción, apoyo y arrastre

- Todo cuerpo cae salvo que tenga apoyo bajo sus pies.
- El apoyo válido es la altura máxima transitable bajo el cuerpo; si no hay, cae.
- Ser transportado es heredar el desplazamiento del soporte: plataformas móviles, DOS como plataforma, marcas en movimiento aparente.
- Los choques con techo, pared y esquina se resuelven por eje mínimo sin teletransportes correctivos.
- La energía de la carrera es recurso para empujar y activar, no puntuación.

---

## 10. Habitaciones: ciclo de vida

Estados de una habitación:

- Entrada: se componen suelo, muros y entidades; se presenta el foco; el dúo aparece en accesos declarados.
- Juego: rige la gramática observar, entender, cooperar, transformar, avanzar.
- Salida obvia: confirma la comprensión y lleva al siguiente espacio.
- Salida menos evidente: premia comprensión excedente con atajo o recontextualización.
- Reentrada: restaura poderes consumibles y objetos reinterpretados; conserva comprensión y memoria de visitas.

Eventos: entrar, salir por vía obvia, salir por vía menos evidente, reentrar, agotar transformación, restaurar visita.

Restricciones: una idea nueva como máximo por habitación; si pide dos, debe dividirse. Sin habitaciones de paso vacío.

---

## 11. Obstáculos e interacciones

- Bloques: peso y posición. Se empujan y se usan como apoyo o contrapeso. Nunca se transportan lejos como llaves.
- Interruptores: solo diegéticos y locales. Presencia, impacto o ritmo sobre mecanismos visibles. Prohibida la activación ciega a distancia.
- Plataformas: fijas, temporales, dejadas como marca o formadas por el dúo. Preguntan permanencia y oportunidad.
- Puertas con opinión: responden a conducta (calma, lentitud, no mirar, ignorar, sincronizarse). Muestran su humor antes de exigirlo. Nunca piden objeto.
- Resonadores: lectura rítmica de relojes, péndulos, ecos y máquinas en bucle. Piden sincronía, no pulsación. Concepto derivado del canon, no sistema nuevo.
- Fragmentos: secretos que son comprensión, atajo o recontextualización. No son coleccionables ni inventario. Concepto derivado del canon, no sistema nuevo.
- Objetos futuros: todo lo reinterpretable anuncia su papel con antelación perceptible.

---

## 12. Muerte suave y memoria de la estación

La muerte no es game over ni pérdida de ideas.

Comportamiento:

- Disolución breve de los agentes implicados, pausa de la amenaza, reaparición en el acceso de la habitación con el vínculo restaurado.
- Sin contadores de vidas, sin retroceso lejano, sin lección por humillación.
- La estación recuerda: las visitas y muertes suaves dejan huella cosmética y narrativa (luz, posición de polvo, ecos visuales). Testimonia, no castiga ni bloquea.
- El borrado total de memoria está siempre disponible como respeto al jugador.

---

## 13. Estados globales y eventos del motor

Estados globales:

- Juego: simulación plena.
- Observación: mundo congelado, lectura activa.
- Entrada a habitación: composición y presentación del foco.
- Salida de habitación: transición con disolvencia.
- Muerte suave: secuencia breve y reaparición.
- Elección final (producción posterior): el mundo espera decisión ética, no ejecuta victoria.

Eventos principales que diseño puede usar:

- Vínculo en tensión y vínculo restaurado.
- Observación iniciada y finalizada.
- Transformación gastada y visita restaurada.
- Marca creada y marca expirada.
- Montaje iniciado y finalizado; lanzamiento y aterrizaje; puente formado y disuelto.
- Puerta que acepta y puerta que se niega.
- Salida obvia cruzada y salida menos evidente cruzada.
- Muerte suave y reaparición.

Restricción: ningún evento exige texto para comprenderse; todos tienen señal perceptible en el mundo.

---

## 14. Relaciones entre sistemas

- El vínculo condiciona todo: locomoción, cooperación, poderes y salidas deben funcionar dentro de él.
- Observar alimenta cooperación: leer bien permite colocar y sincronizar.
- Transformar alimenta geometría: reinterpretar crea el apoyo que UNO aprovecha.
- La marca alimenta sincronía: crear oportunidad pide alcance del otro.
- Las puertas leen conducta del dúo, no inventario: observan calma, ritmo y cercanía.
- Los resonadores leen tiempo compartido: piden a ambos en fase.
- Los fragmentos leen historia de juego: premian observación y experimentación, nunca repetición ciega.
- La memoria de la estación lee eventos: visitas y muertes suaves modulan presentación, jamás bloquean.

---

## 15. Criterios de aceptación del motor

El motor cumple este contrato si, en prueba ciega:

- El vínculo se comprende sin nombrarlo y se corrige por iniciativa propia.
- Montar, observar-leer y transformar-decidir ocurren sin instrucciones.
- Fallar informa y reintentar es inmediato y cercano.
- Reentrar restaura sin castigo y sin exigir repetición vacía.
- Cada habitación se recuerda por forma o conducta al día siguiente.
- Lo aprendido se relata como idea, no como botón.

Todo comportamiento fuera de este contrato es defecto, aunque funcione sin errores técnicos.

*Fin de la especificación v1.0. Programar fuera de este contrato es programar fuera de DUALIS.*
