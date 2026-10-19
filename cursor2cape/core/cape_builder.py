"""
cursor2cape.core.cape_builder
Builder para construção de CapeCursor e documentos .cape (Property List).
"""

import re
import plistlib
from typing import Dict, List, Optional
from PIL import Image

from cursor2cape.domain.models import CapeCursor, RawCursorFrame, ConversionConfig
from cursor2cape.core.image_processor import ImageProcessor
from cursor2cape.core.frame_sampler import FrameSampler


class CapeCursorBuilder:
    """Constrói instâncias de CapeCursor a partir de listas de quadros (1x e opcionalmente 2x)."""

    @classmethod
    def build_empty(cls, identifier: str, target_size: int, include_retina: bool) -> CapeCursor:
        """Cria um cursor transparente (ex: com.apple.coregraphics.Empty)."""
        reps = [ImageProcessor.create_transparent_png(target_size, target_size)]
        if include_retina:
            reps.append(ImageProcessor.create_transparent_png(target_size * 2, target_size * 2))

        return CapeCursor(
            identifier=identifier,
            frame_count=1,
            frame_duration=1.0,
            hotspot_x=0.0,
            hotspot_y=0.0,
            points_wide=float(target_size),
            points_high=float(target_size),
            representations=reps
        )

    @classmethod
    def build_from_frames(
        cls,
        identifier: str,
        frames_1x: List[RawCursorFrame],
        frames_2x: Optional[List[RawCursorFrame]],
        target_size: int
    ) -> CapeCursor:
        """Processa os quadros para 1x e 2x, gerando spritesheets e definindo hotspots."""
        sampled_1x, duration = FrameSampler.sample(frames_1x)
        frame_count = len(sampled_1x)

        # Hotspot lógico (em pontos de tamanho alvo)
        hot_x = float(sampled_1x[0].xhot)
        hot_y = float(sampled_1x[0].yhot)

        # Montagem das imagens PIL para 1x
        pil_images_1x: List[Image.Image] = []
        for f in sampled_1x:
            im = f.pre_rendered_image or ImageProcessor.unpremultiply_argb(f.width, f.height, f.raw_bytes)
            pil_images_1x.append(im)

        rep1x = ImageProcessor.compose_vertical_spritesheet(pil_images_1x, target_size, target_size)
        representations = [rep1x]

        # Montagem para 2x Retina se disponível
        if frames_2x:
            sampled_2x, _ = FrameSampler.sample(frames_2x)
            if len(sampled_2x) == frame_count:
                pil_images_2x: List[Image.Image] = []
                for f in sampled_2x:
                    im = f.pre_rendered_image or ImageProcessor.unpremultiply_argb(f.width, f.height, f.raw_bytes)
                    pil_images_2x.append(im)

                rep2x = ImageProcessor.compose_vertical_spritesheet(
                    pil_images_2x, target_size * 2, target_size * 2
                )
                representations.append(rep2x)

        return CapeCursor(
            identifier=identifier,
            frame_count=frame_count,
            frame_duration=duration,
            hotspot_x=hot_x,
            hotspot_y=hot_y,
            points_wide=float(target_size),
            points_high=float(target_size),
            representations=representations
        )


class CapeDocumentBuilder:
    """Monta o documento Property List (.cape) completo e o salva em disco."""

    @staticmethod
    def build_document_dict(
        config: ConversionConfig,
        cursors: Dict[str, CapeCursor]
    ) -> Dict:
        """Estrutura o dicionário de nível superior exigido pelo Mousecape."""
        safe_slug = re.sub(r'[^a-zA-Z0-9_\-]', '', config.cape_name.lower().replace(' ', '-'))

        return {
            'Author': config.author,
            'CapeName': config.cape_name,
            'CapeVersion': 1.0,
            'Cloud': False,
            'HiDPI': bool(config.include_retina),
            'Identifier': f'com.custom.{safe_slug}',
            'MinimumVersion': 2.0,
            'Version': 2.0,
            'Cursors': {ident: cursor.to_dict() for ident, cursor in cursors.items()}
        }

    @classmethod
    def save_to_file(
        cls,
        config: ConversionConfig,
        cursors: Dict[str, CapeCursor]
    ) -> None:
        """Serializa o dicionário em formato XML Property List."""
        doc = cls.build_document_dict(config, cursors)
        with open(config.output_path, 'wb') as f:
            plistlib.dump(doc, f, fmt=plistlib.FMT_XML)
