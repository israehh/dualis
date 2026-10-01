"""Campaña F28: grafo jugable completo como capa de integración. Sin mecánicas nuevas.

Los JSON de datos quedan congelados por los tests F24–F27: TAL_09 declara
solo TAL_08, R4_04 solo R4_03 y R4_08 solo R4_07 (fondos de saco temporales).
Esta capa añade, solo en memoria y solo para el juego real, las aristas F28/F33
que cierran la campaña sin reescribir historia:

- TAL_09 → R4_01 (bisagra R3→R4)
- R4_04 → R4_05 (continuidad interna de R4)
- R4_08 → R4_EXAM (cierre de región)
- R4_EXAM → R5_01 (bisagra R4→R5, F33)
- R5_08 → R5_EXAM (cierre de región R5, F33)
- R5_04 → R5_05 (continuidad interna de R5, F34)

Los tests antiguos siguen leyendo los JSON directos (mapa base intacto);
el juego y los tests F28 usan with_integration(). Sin render, sin sistemas,
sin patrones ni físicas nuevas: solo enlaces declarados.
"""

R4_ORDER = (
    "R4_01",
    "R4_02",
    "R4_03",
    "R4_04",
    "R4_05",
    "R4_06",
    "R4_07",
    "R4_08",
    "R4_EXAM",
)

R5_ORDER = (
    "R5_01",
    "R5_02",
    "R5_03",
    "R5_04",
    "R5_05",
    "R5_06",
    "R5_07",
    "R5_08",
    "R5_EXAM",
)

EXTRA_LINKS = {
    "TAL_09": ("TAL_08", "R4_01"),
    "R4_04": ("R4_03", "R4_05"),
    "R4_08": ("R4_07", "R4_EXAM"),
}

R5_EXTRA_LINKS = {
    "R4_EXAM": ("R4_08", "R5_01"),
    "R5_08": ("R5_07", "R5_EXAM"),
}

F34_EXTRA_LINKS = {
    "R5_04": ("R5_03", "R5_05"),
}


def with_integration(enlaces_map):
    """Mapa de campaña: copia del base + las aristas F28/F33/F34.

    No muta la entrada. Las rooms no listadas en los overlays conservan
    sus enlaces tal cual; R5_EXAM es el nuevo fondo de saco final y R4_EXAM queda como bisagra.
    """
    merged = {rid: tuple(links) for rid, links in enlaces_map.items()}
    overlays = (EXTRA_LINKS, R5_EXTRA_LINKS, F34_EXTRA_LINKS)
    for overlay in overlays:
        for rid, links in overlay.items():
            if rid in merged:
                merged[rid] = tuple(links)
    return merged
