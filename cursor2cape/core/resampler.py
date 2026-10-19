"""
cursor2cape.core.resampler
Padrão Strategy para obtenção ou redimensionamento de quadros de cursores.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from PIL import Image

from cursor2cape.domain.models import RawCursorFrame
from cursor2cape.core.image_processor import ImageProcessor


class ResamplingStrategy(ABC):
    """Interface abstrata para estratégia de resolução de tamanhos de cursor."""

    @abstractmethod
    def resolve_frames(
        self,
        frames_by_size: Dict[int, List[RawCursorFrame]],
        target_size: int
    ) -> Optional[List[RawCursorFrame]]:
        """Resolve a lista de quadros para o tamanho desejado."""
        pass


class ExactMatchResampler(ResamplingStrategy):
    """Estratégia estrita: apenas retorna frames se o tamanho nativo exato existir."""

    def resolve_frames(
        self,
        frames_by_size: Dict[int, List[RawCursorFrame]],
        target_size: int
    ) -> Optional[List[RawCursorFrame]]:
        return frames_by_size.get(target_size)


class LanczosAdaptiveResampler(ResamplingStrategy):
    """
    Estratégia adaptativa: utiliza o tamanho nativo se existir;
    caso contrário, reamostra a partir do tamanho mais próximo com filtro Lanczos
    e calcula os novos hotspots proporcionalmente.
    """

    def resolve_frames(
        self,
        frames_by_size: Dict[int, List[RawCursorFrame]],
        target_size: int
    ) -> Optional[List[RawCursorFrame]]:
        if target_size in frames_by_size:
            return frames_by_size[target_size]

        if not frames_by_size:
            return None

        # Localiza o tamanho de origem mais próximo
        closest_size = min(frames_by_size.keys(), key=lambda s: abs(s - target_size))
        source_frames = frames_by_size[closest_size]
        scale_factor = float(target_size) / float(closest_size)

        rescaled_frames: List[RawCursorFrame] = []

        for frame in source_frames:
            # Desfaz o alpha se necessário
            orig_im = frame.pre_rendered_image or ImageProcessor.unpremultiply_argb(
                frame.width, frame.height, frame.raw_bytes
            )

            new_w = max(1, int(round(frame.width * scale_factor)))
            new_h = max(1, int(round(frame.height * scale_factor)))

            rescaled_im = orig_im.resize((new_w, new_h), Image.Resampling.LANCZOS)

            new_xhot = min(new_w - 1, max(0, int(round(frame.xhot * scale_factor))))
            new_yhot = min(new_h - 1, max(0, int(round(frame.yhot * scale_factor))))

            # Recria bytes brutos para consistência de modelo
            r, g, b, a = rescaled_im.split()
            r_b, g_b, b_b, a_b = r.tobytes(), g.tobytes(), b.tobytes(), a.tobytes()
            raw_bgra = bytearray(new_w * new_h * 4)

            for i in range(new_w * new_h):
                raw_bgra[i * 4] = b_b[i]
                raw_bgra[i * 4 + 1] = g_b[i]
                raw_bgra[i * 4 + 2] = r_b[i]
                raw_bgra[i * 4 + 3] = a_b[i]

            rescaled_frames.append(
                RawCursorFrame(
                    width=new_w,
                    height=new_h,
                    xhot=new_xhot,
                    yhot=new_yhot,
                    delay_ms=frame.delay_ms,
                    raw_bytes=bytes(raw_bgra),
                    pre_rendered_image=rescaled_im
                )
            )

        return rescaled_frames
