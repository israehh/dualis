"""Montar F8.5: fachada compatible sobre MountAction. Sin cambios de conducta."""
try:
    from dualis.systems.cooperation import MountAction
except ImportError:
    from src.dualis.systems.cooperation import MountAction


class MountSystem(MountAction):
    """Compatibilidad F8.5: idéntica conducta, nuevo hogar en CooperationSystem."""
