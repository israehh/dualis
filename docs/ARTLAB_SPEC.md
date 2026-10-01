# DUALIS ARTLAB SPEC v1.0

Estado: Draft
Propósito: Definir las reglas visuales, estructurales y de producción de assets para DUALIS.

---

# 1. Filosofía

DUALIS utiliza una dirección artística única y consistente.

Todo asset debe parecer pertenecer al mismo mundo.

Se prioriza:

- Legibilidad
- Coherencia
- Composición
- Reutilización

Se evita:

- Realismo fotográfico
- Mezcla de estilos
- Assets ambiguos
- Objetos sin escala definida

---

# 2. Referencias

Inspiración principal:

- Head Over Heels
- Monument Valley
- Cocoon

Inspiración secundaria:

- Fez
- The Witness
- Tunic

---

# 3. Proyección

Projection:

2:1 Isometric

Tile Width:

64 px

Tile Height:

32 px

Transformación oficial:

screen_x = (col - row) * 32

screen_y = (col + row) * 16

Todas las herramientas y assets deben respetar esta proyección.

---

# 4. Iluminación

Dirección:

Top Left

Ángulo:

45°

Reglas:

- Nunca cambiar la dirección de luz.
- Todas las sombras siguen la misma orientación.
- Todas las regiones utilizan la misma lógica de iluminación.

---

# 5. Estilo Visual

Tipo:

Illustrated Isometric

No utilizar:

- Pixel Art puro
- Realismo
- Fotografía
- Cel Shading extremo

Objetivo:

Crear un mundo atemporal, elegante y misterioso.

---

# 6. Paleta General

Materiales principales:

- Piedra
- Alabastro
- Cobre
- Bronce
- Madera oscura

Colores dominantes:

- Gris cálido
- Azul profundo
- Marfil
- Verde apagado
- Cobre oxidado

Cada región podrá añadir colores propios sin romper la coherencia global.

---

# 7. Categorías de Assets

## TILE

Elementos base del escenario.

Ejemplos:

- Floor
- Wall
- Ramp
- Platform

---

## PROP

Objetos decorativos o interactivos.

Ejemplos:

- Books
- Lever
- Gear
- Statue

---

## BUILDING

Estructuras grandes.

Ejemplos:

- Library
- Tower
- Workshop

---

## CHARACTER

Entidades vivas.

Ejemplos:

- UNO
- DOS
- Guardian
- Archivist

---

# 8. Convención de Nombres

Formato:

CATEGORY_REGION_NAME_VARIANT

Ejemplos:

FLOOR_VESTIBULE_A

COLUMN_VESTIBULE_A

BOOKSHELF_LIBRARY_A

GEAR_WORKSHOP_A

PEDESTAL_TOWER_A

UNO_IDLE

DOS_IDLE

---

# 9. Reglas para Props

Cada imagen contiene:

UN SOLO OBJETO

Correcto:

BOOK_STACK_A

Incorrecto:

BOOKS_TABLE_CANDLE_STACK

Los props deben:

- Fondo transparente
- Escala consistente
- Anchor definido

---

# 10. Reglas para Buildings

Todo building debe definir:

- Footprint
- Height
- Anchor

Ejemplo:

```json
{
  "id": "LIBRARY_MAIN",
  "footprint": [3,2],
  "height": 4,
  "anchor": "front_bottom"
}
```

---

# 11. Anchors

## Prop

bottom_center

## Building

front_bottom

## Character

feet_center

Los anchors son obligatorios.

---

# 12. Footprints

Todo asset con volumen debe declarar footprint.

Ejemplos:

Columna:

1x1

Estantería:

2x1

Máquina:

2x2

Biblioteca:

3x2

Torre:

4x4

---

# 13. Depth Sorting

Regla oficial:

depth = row + col

Extensión para altura:

depth = (row + col) * 100 + z

Nunca ordenar por screen_y directamente.

---

# 14. Asset Package

Cada asset tendrá su carpeta:

assets/

    props/

        BOOK_STACK_A/

            spec.json
            concept.png
            final.png

---

# 15. Asset Specification

Ejemplo:

```json
{
  "id": "BOOK_STACK_A",
  "category": "prop",
  "region": "library",

  "footprint": [1,1],

  "height": 1,

  "anchor": "bottom_center",

  "style": "dualis_v1"
}
```

---

# 16. Regiones Iniciales

R1 - Vestíbulo

Materiales:

- Piedra
- Alabastro

Assets iniciales:

- Floor
- Wall
- Column
- Arch
- Pedestal

---

R2 - Biblioteca

Materiales:

- Madera
- Piedra

Assets iniciales:

- Bookshelf
- Desk
- Scroll
- Lamp

---

R3 - Taller

Materiales:

- Cobre
- Bronce

Assets iniciales:

- Gear
- Pipe
- Workbench

---

R4 - Torre

Materiales:

- Piedra blanca
- Oro antiguo

Assets iniciales:

- Pillar
- Rune Pedestal
- Observatory

---

# 17. Pipeline ArtLab

STYLE.md
↓
Asset Spec
↓
Concept
↓
Generation
↓
Cleanup
↓
Validation
↓
Import

No se generan assets sin especificación previa.

---

# 18. Regla de Oro

Antes de aprobar cualquier asset:

¿Parece pertenecer al mismo mundo que UNO y DOS?

Si la respuesta es NO:

El asset se rechaza.