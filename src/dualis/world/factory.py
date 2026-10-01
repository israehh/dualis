"""Factoría F9: instanciar piezas desde configuración. Sin lógica específica."""
import json
from pathlib import Path

try:
    from dualis.world.entity import Entity
    from dualis.world.observables import (
        MovingPhenomenon,
        OscillatingPhenomenon,
        TimedPhenomenon,
    )
    from dualis.world.phenomenon import TestPhenomenon
    from dualis.world.test_transformable import TestTransformable
    from dualis.world.transformables import (
        BridgeTransformable,
        PlatformTransformable,
        StepTransformable,
    )
except ImportError:
    from src.dualis.world.entity import Entity
    from src.dualis.world.observables import (
        MovingPhenomenon,
        OscillatingPhenomenon,
        TimedPhenomenon,
    )
    from src.dualis.world.phenomenon import TestPhenomenon
    from src.dualis.world.test_transformable import TestTransformable
    from src.dualis.world.transformables import (
        BridgeTransformable,
        PlatformTransformable,
        StepTransformable,
    )


def _uno(**params):
    return Entity("UNO", radius=14, color=(210, 180, 120), shape="circle", **params)


def _dos(**params):
    return Entity("DOS", radius=14, color=(90, 180, 170), shape="square", **params)


KINDS = {
    "uno": _uno,
    "dos": _dos,
    "phenomenon": TestPhenomenon,
    "moving": MovingPhenomenon,
    "oscillating": OscillatingPhenomenon,
    "timed": TimedPhenomenon,
    "testbox": TestTransformable,
    "step": StepTransformable,
    "bridge": BridgeTransformable,
    "platform": PlatformTransformable,
}


def create(spec):
    kind = spec.get("kind")
    if kind not in KINDS:
        raise KeyError("pieza desconocida: %s" % kind)
    params = dict(spec.get("params", {}))
    return KINDS[kind](**params)


def load_setup(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [create(spec) for spec in raw.get("actors", [])]
