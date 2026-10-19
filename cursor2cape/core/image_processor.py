"""
cursor2cape.core.image_processor
Processamento e conversão de buffers de pixels, desfeita de canal alpha e spritesheets.
"""

import io
from typing import List
from PIL import Image


class ImageProcessor:
    """Manipulação e conversão de imagens de cursores."""

    @staticmethod
    def unpremultiply_argb(width: int, height: int, raw_bytes: bytes) -> Image.Image:
        """
        Converte bytes ARGB com alpha pré-multiplicado (padrão Xcursor)
        para uma imagem PIL no formato RGBA desfeita (straight alpha).
        """
        total_pixels = width * height
        out = bytearray(total_pixels * 4)

        for i in range(0, total_pixels * 4, 4):
            b = raw_bytes[i]
            g = raw_bytes[i + 1]
            r = raw_bytes[i + 2]
            a = raw_bytes[i + 3]

            if a == 0:
                out[i] = 0
                out[i + 1] = 0
                out[i + 2] = 0
                out[i + 3] = 0
            elif a == 255:
                out[i] = r
                out[i + 1] = g
                out[i + 2] = b
                out[i + 3] = 255
            else:
                inv_a = 255.0 / a
                out[i] = min(255, int(round(r * inv_a)))
                out[i + 1] = min(255, int(round(g * inv_a)))
                out[i + 2] = min(255, int(round(b * inv_a)))
                out[i + 3] = a

        return Image.frombytes('RGBA', (width, height), bytes(out))

    @staticmethod
    def to_png_bytes(image: Image.Image) -> bytes:
        """Serializa uma imagem PIL para o formato binário PNG."""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()

    @staticmethod
    def create_transparent_png(width: int, height: int) -> bytes:
        """Gera um PNG 100% transparente com as dimensões especificadas."""
        im = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        return ImageProcessor.to_png_bytes(im)

    @staticmethod
    def compose_vertical_spritesheet(
        frames: List[Image.Image],
        frame_width: int,
        frame_height: int
    ) -> bytes:
        """
        Gera uma folha de sprites vertical exigida pelo Mousecape:
        largura = frame_width, altura = frame_height * total_frames.
        """
        count = len(frames)
        sheet = Image.new('RGBA', (frame_width, frame_height * count))

        for idx, frame in enumerate(frames):
            sheet.paste(frame, (0, idx * frame_height))

        return ImageProcessor.to_png_bytes(sheet)
