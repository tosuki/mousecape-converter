"""
cursor2cape.parsers.xcursor_parser
Parser de baixo nível para arquivos binários no formato Xcursor (X11 / Linux).
"""

import struct
from typing import Dict, List, Optional
from cursor2cape.domain.models import RawCursorFrame


class XCursorParser:
    """
    Responsável por analisar e extrair imagens de arquivos no formato Xcursor.
    Especificação: https://www.x.org/releases/current/doc/man/man3/Xcursor.3.xhtml
    """

    MAGIC_HEADER = b'Xcur'
    IMAGE_TYPE_CHUNK = 0xfffd0002

    @classmethod
    def parse_file(cls, file_path: str) -> Optional[Dict[int, List[RawCursorFrame]]]:
        """Abre e extrai os quadros de um arquivo binário Xcursor."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            return cls.parse_bytes(data)
        except Exception:
            return None

    @classmethod
    def parse_bytes(cls, data: bytes) -> Optional[Dict[int, List[RawCursorFrame]]]:
        """Processa um buffer de bytes contendo dados Xcursor."""
        if len(data) < 16 or data[:4] != cls.MAGIC_HEADER:
            return None

        try:
            header_size, version, ntoc = struct.unpack('<III', data[4:16])
            frames_by_size: Dict[int, List[RawCursorFrame]] = {}

            for i in range(ntoc):
                offset_toc = 16 + i * 12
                ctype, subtype, pos = struct.unpack('<III', data[offset_toc : offset_toc + 12])

                if ctype == cls.IMAGE_TYPE_CHUNK:
                    head, itype, isubtype, iversion, w, h, xhot, yhot, delay = struct.unpack(
                        '<IIIIIIIII', data[pos : pos + 36]
                    )
                    expected_length = w * h * 4
                    pixel_bytes = data[pos + 36 : pos + 36 + expected_length]

                    if len(pixel_bytes) == expected_length:
                        frame = RawCursorFrame(
                            width=w,
                            height=h,
                            xhot=xhot,
                            yhot=yhot,
                            delay_ms=delay,
                            raw_bytes=pixel_bytes
                        )
                        frames_by_size.setdefault(subtype, []).append(frame)

            return frames_by_size if frames_by_size else None
        except Exception:
            return None
