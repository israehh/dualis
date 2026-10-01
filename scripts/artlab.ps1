$dirs = @(
    "artlab",
    "artlab/registry",
    "artlab/assets",
    "artlab/assets/tiles",
    "artlab/assets/props",
    "artlab/assets/buildings",
    "artlab/assets/characters",
    "artlab/concepts",
    "artlab/references",
    "artlab/prompts",
    "artlab/exports"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

@"
# DUALIS STYLE

Projection: 2:1 Isometric

Tile Size: 64x32

Light Direction: Top Left

Style: Illustrated Isometric

Mood:
- Melancholic Wonder
- Ancient Knowledge
- Mystery

References:
- Head Over Heels
- Monument Valley
- Cocoon
"@ | Set-Content "artlab/STYLE.md"

@"
# DUALIS ARTLAB SPEC

Ver ARTLAB_SPEC v1.

Categorías:
- tile
- prop
- building
- character

Anchors:
- bottom_center
- front_bottom
- feet_center

Depth:
(row + col) * 100 + z
"@ | Set-Content "artlab/ARTLAB_SPEC.md"

@'
[
  {
    "id":"FLOOR_VESTIBULE_A",
    "category":"tile",
    "region":"vestibulo",
    "footprint":[1,1]
  },
  {
    "id":"WALL_VESTIBULE_A",
    "category":"tile",
    "region":"vestibulo",
    "footprint":[1,1]
  }
]
'@ | Set-Content "artlab/registry/tiles.json"

@'
[
  {
    "id":"BOOK_STACK_A",
    "category":"prop",
    "region":"biblioteca",
    "footprint":[1,1],
    "anchor":"bottom_center"
  }
]
'@ | Set-Content "artlab/registry/props.json"

@'
[
  {
    "id":"LIBRARY_MAIN",
    "category":"building",
    "region":"biblioteca",
    "footprint":[3,2],
    "height":4,
    "anchor":"front_bottom"
  }
]
'@ | Set-Content "artlab/registry/buildings.json"

@'
[
  {
    "id":"UNO",
    "category":"character",
    "anchor":"feet_center"
  },
  {
    "id":"DOS",
    "category":"character",
    "anchor":"feet_center"
  }
]
'@ | Set-Content "artlab/registry/characters.json"

Write-Host ""
Write-Host "================================="
Write-Host " DUALIS ARTLAB CREADO"
Write-Host "================================="
Write-Host ""