# DUALIS — Plan de Implementación

**Versión:** 1.0 — Plan operativo
**Estado:** Orden de construcción vinculante. Sin código, sin librerías, sin clases, sin algoritmos.
**Obedece a:** canon (`dualis_concept`, `dualis__history`, `dualis_design_bible`, `dualis_room_language`, `dualis_vertical_slice`, `dualis_rooms_vestibulo`, `dualis_system_spec`) y `docs/work/dualis_engine_architecture.md`.
**Define únicamente:** orden de construcción, dependencias entre fases, criterios de aceptación y entregables verificables.

---

## 1. Filosofía de implementación

**Construir de abajo hacia arriba.** Primero el latido y el mundo vacío; después los habitantes; después el significado. Nunca contenido antes que simulación.

**Cada fase genera un ejecutable verificable.** Ninguna fase termina en documentos ni en piezas sueltas. Toda fase se juega, se observa y se valida en prueba ciega cuando corresponde.

**Ninguna fase depende de sistemas futuros.** Cada fase usa solo lo ya construido y verificado. Lo futuro se menciona como hueco reservado, nunca como requisito.

**El Vertical Slice es el primer objetivo real.** Todo lo anterior existe para sostenerlo. Todo lo posterior existe porque el Slice demostró que el ADN se entiende jugando.

---

## 2. Estrategia global

F0 Fundación → F1 Simulación básica → F2 Habitaciones → F3 Entidades → F4 Cooperación → F5 Poderes → F6 Interacciones → F7 Vertical Slice → F8 Persistencia → F9 Pulido.

Este orden minimiza riesgo porque estabiliza lo invisible antes que lo visible: primero tiempo determinista y eventos, después lugares que se entran y se salen, después cuerpos que ocupan espacio, después el vínculo que los une, después los poderes que reinterpretan, después las puertas que opinan, y solo entonces las seis habitaciones que deben emocionar. Persistencia y pulido llegan cuando ya hay algo que merezca recordarse y sentirse.

Ninguna fase introduce dos ideas de diseño a la vez, en coherencia con una habitación igual a una idea.

---

## 3. F0 Fundación

Entregables: estructura del proyecto según mapa vigente; configuración versionada de paso fijo, semilla por habitación y estados globales; validación inicial derivada del lenguaje (foco declarado, doble salida, una idea); ejecución mínima que abre, late y cierra sin contenido.

Criterios de aceptación: el ejecutable arranca y termina limpio; el paso fijo avanza con tope y sin medios pasos; la validación rechaza una habitación mal declarada; canon mayor que trabajo ante cualquier duda.

Riesgos: fundar con contenido prematuro. Mitigación: prohibido cargar habitaciones del Vestíbulo en F0.

---

## 4. F1 Simulación básica

Objetivo: habitación vacía ejecutable.

Incluye: latido por pasos fijos; tiempo discreto y reproducible; correo de eventos con orden dentro del paso; gestión de escena vacía y de estados globales (juego, entrada, salida).

No incluye: puzles, poderes, narrativa, vínculo, puertas ni memoria.

Criterios de aceptación: la escena vacía late de forma estable; los eventos emitidos llegan completos antes del paso siguiente; el cambio de modo solo ocurre por transición concedida.

---

## 5. F2 Habitaciones

Objetivo: entrar y salir de habitaciones.

Incluye: definición de habitación como datos (entidades, salidas, foco, región); enlaces por salidas declaradas; carga como composición del lugar; reinicio de visita con restauración de consumibles.

Pruebas obligatorias: entrar compone foco y accesos; salir por vía obvia y por vía menos evidente llevan a destinos distintos y correctos; reentrar restaura sin castigo; una habitación con dos ideas se rechaza en validación; ninguna habitación conoce a otra salvo por salidas.

---

## 6. F3 Entidades

Objetivo: UNO y DOS existen como cuerpos diferenciados.

Incluye: desplazamiento asimétrico (salto preciso frente a carrera con inercia); ocupación espacial con apoyo, techo y arrastre por soporte; presencia corporal legible (espera, orientación).

No incluye: vínculo, poderes, cooperación ni puertas. La cercanía aún no condiciona.

Criterios de aceptación: UNO no empuja cargas pesadas ni corre; DOS no resuelve saltos finos; ser transportado hereda desplazamiento sin teletransportes; caer sin apoyo es legible e inmediato.

---

## 7. F4 Cooperación

Objetivo: vínculo completo y cooperación espacial mínima.

Incluye: medición de distancia con histéresis; tensión con oscurecimiento y ralentización sin muerte; montaje como plataforma móvil con herencia de movimiento.

Pruebas obligatorias: superar el límite entra en tensión y volver a cercanía segura la restaura sin parpadeo en el borde; toda solución de prueba cabe dentro del vínculo; montar permite alcanzar altura imposible en solitario y se comprende sin texto en prueba ciega.

---

## 8. F5 Poderes

Observar: congela el mundo con mirada libre durante duración breve y fija, un uso por visita, recargable al reentrar. Verificable: leer un ritmo visible y cruzarlo solo después de leer; nunca reposiciona gratis.

Transformar: reinterpreta un objeto elegible una vez por visita con affordance previa. Verificable: gasto deliberado por colocación clara, irreversible en la visita, restaurado al reentrar, con salida alternativa exigente para quien no quiera gastarlo.

Marca: apoyo breve creado en el salto y aprovechable en ventana generosa. Verificable: sincronía holgada sin reflejos; expira sin daño colateral.

Ningún poder es arma, llave ni botón global.

---

## 9. F6 Interacciones

Basado en el canon. Bloques como peso y apoyo que se empujan sin viajar lejos; plataformas fijas, temporales y formadas por el dúo; interruptores solo diegéticos y locales por presencia, impacto o ritmo; puertas con opinión que muestran su humor antes de exigir conducta y nunca piden objeto.

Criterios de aceptación: cada interacción se anuncia antes de necesitarse; cada activación es local y visible; cada puerta se niega con suavidad ante prisa y acepta ante calma conjunta; resonadores piden sincronía y fragmentos premian comprensión, ambos como derivados sin sistemas nuevos.

---

## 10. F7 Vertical Slice

Implementar únicamente `docs/canon/dualis_rooms_vestibulo.md`. Nada más. Nada de lanzamiento largo, puente sostenido, ecos, gravedad direccional, nominación, relojes regionales, archivo ni final ético.

Checklist exacta: Despertar contiguo enseña dúo y vínculo; El hombro ajeno enseña montar; La duda quieta enseña observar para leer; Lo que no era silla enseña transformar deliberada; La respiración del vano enseña marca y sincronía; La puerta que duda cierra con conducta conjunta como primer gran momento memorable. Cada una con foco, doble salida, momento de comprensión y reglas verificadas según su ficha. Duración total de quince a veinticinco minutos en jugador nuevo.

---

## 11. F8 Persistencia

Guardar: habitación actual y acceso, comprensión registrada por habitación y región, conteo de visitas y muertes suaves para huella, consumibles de la visita activa, variante narrativa visitada cuando exista. Todo versionado y migrable, con borrado total disponible.

No guardar: posiciones intermedias, estados de presentación, intenciones a medio gesto ni duraciones restantes como verdad. Al cargar, la visita se recompone desde su inicio declarado.

Criterios de aceptación: salir y volver conserva comprensión sin bloquear; la huella modula luz y ecos sin cerrar caminos; reentrar restaura sin exigir repetición vacía.

---

## 12. F9 Pulido

Audio como información y tono, nunca como requisito exclusivo: toda pista sonora tiene redundancia visible. Retroalimentación sensible del vínculo, poderes, puertas y huellas sin texto obligatorio. Accesibilidad de lectura: foco, ritmo y affordance perceptibles por más de un canal. Telemetría mínima de playtest ciego: comprensión del vínculo, uso espontáneo de cooperación espacial, recuerdo al día siguiente y relato como idea.

Criterios de aceptación: el Slice se completa sin instrucciones con afecto declarado por el dúo; ningún pulido introduce poder, puerta-objeto ni bloqueo nuevos.

---

## 13. Dependencias

| Fase | Depende de | Bloquea a |
|---|---|---|
| F0 Fundación | Canon | F1 |
| F1 Simulación básica | F0 | F2 |
| F2 Habitaciones | F1 | F3, F8 |
| F3 Entidades | F2 | F4 |
| F4 Cooperación | F3 | F5, F6 |
| F5 Poderes | F4 | F6, F7 |
| F6 Interacciones | F4, F5 | F7 |
| F7 Vertical Slice | F2–F6 | F8, F9 |
| F8 Persistencia | F2, F7 | F9 |
| F9 Pulido | F7, F8 | Expansión |

Ninguna fase salta a su bloqueadora. F7 no empieza sin F2 a F6 verificadas.

---

## 14. Riesgos

Riesgo técnico: paso no determinista o eventos fuera de orden. Mitigación: F1 con tope de pasos, semilla por habitación y validación de orden antes de contenido.

Riesgo de diseño: vínculo percibido como castigo o cooperación degradada a alternancia. Mitigación: F4 y F7 en prueba ciega con corrección por iniciativa propia como criterio; rediseñar habitación en lugar de añadir texto.

Riesgo de contenido: dos ideas por habitación o relleno para alargar. Mitigación: validación una-idea y poda obligatoria; si sobra tiempo se recorta, si falta no se añade ruido.

---

## 15. Definition of Done

Motor funcional: late en pasos fijos, ordena modos por transición, transporta eventos completos, compone y restaura visitas, mide el vínculo con histéresis y anuncia todo con señal perceptible.

Vertical Slice funcional: las seis habitaciones del Vestíbulo se juegan de principio a fin sin instrucciones, con doble salida, momento memorable en la puerta que duda y recuerdo al día siguiente.

Base para expansión: Biblioteca y Taller pueden definirse como datos con su vocabulario y ruptura sin tocar el motor; validación, memoria y herramientas de revisión crecen sin reescribir fases.

*Fin del plan v1.0. Ejecutar fuera de este orden es improvisar.*
