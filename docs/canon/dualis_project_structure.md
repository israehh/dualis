# DUALIS — Estructura del Proyecto

**Versión:** 1.0 — Organización definitiva
**Estado:** Norma de organización. No crea archivos. No define implementación.
**Obedece a:** `docs/canon/*` y `docs/work/dualis_engine_architecture.md`.
**Regla superior:** canon > work. Nada de lo aquí definido puede contradecir al canon.

---

## 1. Propósito

Definir dónde vive cada cosa en DUALIS, qué puede depender de qué y cómo evoluciona el proyecto sin improvisar.

Este documento no describe comportamiento ni implementación. Describe organización, propiedad y dependencias permitidas.

---

## 2. Principios de organización

1. El canon se lee; el trabajo se deriva. Nada en trabajo redefine visión, lenguaje ni habitaciones.
2. La simulación manda sobre la presentación también en carpetas: lo que decide nunca vive junto a lo que muestra.
3. La habitación es la unidad de datos: todo contenido jugable pertenece a una habitación o a una región como familia.
4. Cada ámbito tiene un dueño claro y una responsabilidad única.
5. Lo temporal y lo narrativo viven separados desde el primer día.
6. Validar es parte de la estructura, no un añadido posterior.

---

## 3. Mapa general

- docs/canon. Verdad oficial e inmutable sin revisión humana. Visión, lenguaje, habitaciones, slice y contratos.
- docs/work. Derivación técnica y de producción. Arquitectura, especificación de sistemas y este mapa. Nunca contradice al canon.
- data. Definiciones jugables versionables: habitaciones, regiones, affordances y memoria inicial. Una idea por habitación.
- validation. Comprobaciones derivadas del lenguaje: foco, doble salida, vínculo, affordance, restauración y grafo.
- presentation-reference. Guía sensible del diorama: foco, señales, tono por región. Solo referencia, nunca lógica.
- persistence-schema. Forma de la memoria: qué se recuerda, qué expira con la visita, cómo se versiona.
- tools-definition. Definición de herramientas futuras: visor, sábana de habitaciones y validador. Qué muestran, no cómo se programan.
- implementation-future. Espacio reservado para la futura implementación del motor. Hoy solo existe como hueco con fronteras, sin contenido.

Nada jugable vive fuera de data salvo la memoria. Nada normativo vive fuera de docs.

---

## 4. Responsabilidad por ámbito

**docs/canon.** Custodia el qué y el porqué. Nadie lo edita sin revisión humana explícita. Toda excepción se justifica por escrito.

**docs/work.** Custodia el cómo se organiza y cómo se comporta el motor como contrato. Puede crecer con nuevos contratos siempre que citen su base canónica.

**data.** Custodia el dónde y el qué hay. Cada habitación declara entidades, salidas, foco y región. Cada región declara vocabulario permitido y ruptura de regla.

**validation.** Custodia el está-bien. Traduce reglas del lenguaje en comprobaciones legibles por humanos antes que por máquinas.

**presentation-reference.** Custodia el se-ve-y-se-siente. Foco, affordance, tensión del vínculo, respiración de puertas, huella de memoria.

**persistence-schema.** Custodia el se-recuerda. Separa visita temporal de memoria narrativa versionada.

**tools-definition.** Custodia el se-revisa. Define qué debe mostrar cada herramienta para validar diseño sin jugar a ciegas.

**implementation-future.** Custodia el vacío ordenado. Reserva core, world, systems, presentation y persistence como ámbitos futuros con las fronteras de la arquitectura.

---

## 5. Dependencias permitidas

- work depende de canon. Nunca al revés.
- data depende de canon y de work como contratos. Nunca define comportamiento nuevo.
- validation depende de room_language y rooms_vestibulo. Nunca inventa reglas.
- presentation-reference depende de design_bible y room_language. Nunca decide jugabilidad.
- persistence-schema depende de system_spec. Nunca guarda instantes ni fotogramas.
- tools-definition depende de validation y engine_architecture. Nunca sustituye al playtest ciego.
- implementation-future dependerá, cuando exista, de engine_architecture y system_spec. Nunca de atajos fuera del contrato.

---

## 6. Dependencias prohibidas

- Ningún ámbito de trabajo modifica el canon por vía indirecta.
- Ninguna definición de datos invoca comportamiento fuera de los sistemas declarados.
- Ninguna referencia de presentación escribe en simulación ni en memoria.
- Ninguna herramienta decide diseño; solo lo muestra y lo comprueba.
- Ninguna memoria narrativa cierra puertas ni exige repetición.
- Ningún ámbito futuro nace con dependencias circulares: el orden del paso es acíclico y el correo de eventos no devuelve llamadas.
- Ningún contenido jugable vive suelto sin habitación ni región.

---

## 7. Ciclo de vida de un cambio

1. Nace como necesidad de diseño frente al canon.
2. Se formula como derivación en docs/work con cita explícita a su base.
3. Si toca datos, se expresa como habitación o región con una sola idea.
4. Si toca reglas, se expresa como comprobación en validation.
5. Si toca memoria o presentación, se expresa como esquema o referencia, nunca como lógica.
6. Se valida en prueba ciega: curiosidad sin indicación, resolución sin explicación, recuerdo al día siguiente.
7. Solo entonces se considera parte del proyecto.

Ningún cambio salta pasos. Ningún cambio entra por urgencia.

---

## 8. Reglas de convivencia

- Un concepto, un dueño. Si dos ámbitos lo definen, uno sobra.
- Nombres estables del canon: UNO, DOS, vínculo, Observar, Transformar, Marca, resonador como ritmo, fragmento como comprensión. Trabajo no renombra.
- Resonadores y fragmentos se tratan siempre como derivados, nunca como sistemas nuevos.
- La puerta con opinión y la doble salida son patrimonio del lenguaje; ninguna estructura los degrada a cerradura o pasillo.
- Todo lo excluido del Slice sigue excluido hasta que su propia habitación lo presente según el lenguaje.

---

## 9. Evolución permitida

Pueden crecer: nuevas habitaciones dentro de data, nuevas regiones como familia de sentido, nuevas comprobaciones derivadas, nuevas huellas cosméticas, nuevas herramientas de revisión.

No pueden crecer sin revisión humana: canon, poderes del dúo, estados globales, eventos del contrato, reglas de persistencia.

Cuando implementation-future se llene, heredará exactamente las fronteras de engine_architecture: núcleo que ordena, mundo que contiene, sistemas que razonan, presentación que observa, persistencia que recuerda.

*Fin de la estructura v1.0. Organizar fuera de este mapa es organizar fuera de DUALIS.*
