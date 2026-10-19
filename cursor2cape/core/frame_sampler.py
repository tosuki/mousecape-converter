"""
cursor2cape.core.frame_sampler
Amostragem e conformidade de taxas de quadros para restrições do macOS CoreGraphics.
"""

from typing import List, Tuple
from cursor2cape.domain.models import RawCursorFrame


class FrameSampler:
    """
    Controla o número de quadros de cursores animados.
    No macOS (Mousecape / CGSRegisterCursorWithImages), o limite rígido é 24 quadros.
    Animações com 60 quadros excedem o buffer do sistema e falham se não reamostradas.
    """

    MAX_MAC_FRAMES = 24

    @classmethod
    def sample(cls, frames: List[RawCursorFrame]) -> Tuple[List[RawCursorFrame], float]:
        """
        Retorna uma tupla contendo:
        1. A lista de quadros amostrados dentro do limite permitido (<= 24).
        2. A duração calculada por quadro em segundos (preservando o tempo do ciclo completo).
        """
        total = len(frames)
        if total <= 1:
            return frames, 1.0

        base_delay_ms = frames[0].delay_ms if frames[0].delay_ms > 0 else 50
        base_delay_s = base_delay_ms / 1000.0

        if total <= cls.MAX_MAC_FRAMES:
            return frames, base_delay_s

        # Para 60 quadros, saltar de 3 em 3 resulta em exatamente 20 quadros (suave e seguro)
        if total == 60:
            step = 3
        else:
            step = (total + cls.MAX_MAC_FRAMES - 1) // cls.MAX_MAC_FRAMES

        sampled = frames[::step]
        adjusted_duration = base_delay_s * step

        return sampled, adjusted_duration
