# DUALIS WORLD PLAN
Versión 1.0

Estado de referencia arquitectónica del mundo DUALIS.

Este documento define la estructura global del mundo, la progresión prevista y las reglas de crecimiento futuras.

No describe implementación concreta.

No sustituye DUALIS_CONTEXT.md.

---

# 1. OBJETIVO

DUALIS es un juego de exploración, observación y resolución de patrones.

Su estructura general toma inspiración de la organización espacial de Head Over Heels, pero mantiene un lenguaje propio basado en:

- OBSERVE
- TRANSFORM
- MOUNT
- LINK

El objetivo es construir un mundo coherente, legible y ampliable sin romper la progresión existente.

---

# 2. PRINCIPIOS FUNDAMENTALES

## 2.1 Una idea por sala

Cada habitación debe enseñar, practicar o evaluar una única idea principal.

No se crearán habitaciones de relleno.

---

## 2.2 El fallo informa

La frustración no es una mecánica.

El error debe ayudar al jugador a comprender mejor el sistema.

---

## 2.3 El lenguaje es el progreso

La progresión se basa en comprender patrones.

No existen:

- llaves
- inventarios complejos
- farmeo
- mejoras numéricas

---

## 2.4 Cooperación permanente

UNO y DOS forman un sistema único.

El vínculo es permanente.

No existen campañas separadas.

No existe intercambio de personaje principal.

---

## 2.5 Lógica cartesiana

Toda la lógica del juego ocurre en coordenadas cartesianas.

La proyección isométrica es únicamente representación visual.

---

## 2.6 Sin world_z jugable

No existen:

- saltos
- escaleras
- plataformas físicas
- gravedad simulada

La elevación es exclusivamente visual.

---

# 3. ESTRUCTURA GENERAL

El mundo se organiza como una columna vertebral principal.

La progresión inicial es lineal.

Las ramificaciones aparecerán únicamente cuando el lenguaje esté consolidado.

---

# 4. ESTADO ACTUAL

Actualmente existen:

ROOM_SLICE
↓
R1 VESTÍBULO
↓
R2 BIBLIOTECA
↓
R3 TALLER

---

# 5. REGIONES

## R1 — EL VESTÍBULO

Propósito:

Introducción al lenguaje.

Conceptos:

- movimiento
- observación
- transformación
- montaje

Función:

Construir el vocabulario básico.

Estado:

Implementado.

---

## R2 — LA BIBLIOTECA

Propósito:

Variaciones funcionales.

Conceptos:

- reinterpretación
- combinación simple
- ROOM_DENIED como aprendizaje

Función:

Demostrar que el mismo lenguaje produce soluciones distintas.

Estado:

Implementado.

---

## R3 — EL TALLER DE LOS ECOS

Propósito:

Síntesis.

Conceptos:

- orden de acciones
- distancia
- decisiones
- rutas alternativas

Función:

Combinar todo lo aprendido anteriormente.

Estado:

Implementado.

---

# 6. BISAGRA PRINCIPAL

TAL_09 constituye actualmente la única bisagra natural del mundo.

No debe modificarse hasta que exista una región nueva validada.

Toda expansión futura partirá desde TAL_09.

---

# 7. ESTRUCTURA FUTURA

La estructura prevista es:

ROOM_SLICE
↓
R1 VESTÍBULO
↓
R2 BIBLIOTECA
↓
R3 TALLER
↓
R4 JARDÍN INVERTIDO
↓
R5 TORRE DE LOS NOMBRES
↓
R6 ARCHIVO DE LO QUE NO FUE
↓
NÚCLEO

---

# 8. R4 — JARDÍN INVERTIDO

Estado:

Diseño conceptual.

Objetivo:

Explorar percepción espacial.

Importante:

No introduce gravedad real.

No introduce world_z.

No introduce nuevas capacidades físicas.

La inversión es conceptual y visual.

---

# 9. R5 — TORRE DE LOS NOMBRES

Estado:

Diseño conceptual.

Objetivo:

Explorar identidad, equivalencia y relación entre entidades.

El jugador ya conoce el lenguaje.

La región profundiza en su significado.

---

# 10. R6 — ARCHIVO DE LO QUE NO FUE

Estado:

Diseño conceptual.

Objetivo:

Confrontar versiones alternativas de patrones ya conocidos.

Región de reflexión y reinterpretación.

---

# 11. NÚCLEO

Estado:

No implementado.

Objetivo:

Examen final.

No introduce ideas nuevas.

Solo combina:

- OBSERVE
- TRANSFORM
- MOUNT
- LINK

en configuraciones avanzadas.

---

# 12. EL VÍNCULO

El vínculo entre UNO y DOS es un pilar estructural.

Estados conocidos:

- CONNECTED
- TENSION
- LIMIT

Las regiones futuras podrán utilizar el vínculo como condición de resolución.

El vínculo sustituye el papel que otras aventuras otorgan a:

- llaves
- habilidades
- inventario

---

# 13. HUBS Y TRÁNSITOS

No existe hub global actualmente.

No debe implementarse hasta que existan suficientes regiones para justificarlo.

Regla:

Primero regiones.

Después atajos.

Nunca al revés.

---

# 14. DOOR TO BEFORE

Principio heredado de la estructura clásica de exploración.

Tras un hito importante:

- debe existir retorno rápido
- debe evitarse backtracking excesivo

La implementación concreta queda pendiente.

---

# 15. CRECIMIENTO FUTURO

Toda nueva región deberá:

- añadir una idea principal
- respetar el lenguaje existente
- evitar verbos redundantes
- mantener compatibilidad con regiones previas

Nunca se insertarán regiones entre regiones ya existentes.

La expansión siempre ocurrirá en los extremos previstos.

---

# 16. RESTRICCIONES ARQUITECTÓNICAS

Prohibido introducir:

- sistemas de vidas
- daño arbitrario
- llaves tradicionales
- inventario complejo
- farmeo
- IA avanzada
- pathfinding obligatorio
- saltos
- plataformas físicas
- world_z jugable

---

# 17. REFERENCIAS

Referencias estructurales:

- OpenHoH (Open Head Over Heels)
- Head Over Heels (RetroRemakes)

Estas referencias se utilizan únicamente para estudiar:

- organización del mundo
- progresión
- estructura de regiones
- conexiones

No para copiar mecánicas, contenido o diseño concreto.

---

# 18. ESTADO DE APROBACIÓN

Versión:

WORLD_ARCHITECTURE_V1

Estado:

Aprobado como guía de crecimiento del proyecto.

Las futuras regiones deberán respetar este documento salvo revisión explícita.