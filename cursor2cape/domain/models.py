"""
cursor2cape.domain.models
Entidades e Value Objects do domínio de conversão de cursores.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from PIL import Image


@dataclass(frozen=True)
class RawCursorFrame:
    """Representa um quadro bruto extraído de um arquivo binário Xcursor."""
    width: int
    height: int
    xhot: int
    yhot: int
    delay_ms: int
    raw_bytes: bytes
    pre_rendered_image: Optional[Image.Image] = field(default=None, repr=False)


@dataclass(frozen=True)
class ThemeInfo:
    """Metadados de um tema de cursores descoberto no sistema de arquivos."""
    name: str
    path: str
    cursors_dir: str
    author: str
    available_sizes: List[int]


@dataclass(frozen=True)
class ConversionConfig:
    """Parâmetros e opções de configuração para a geração do arquivo .cape."""
    target_size: int
    include_retina: bool
    allow_resampling: bool
    cape_name: str
    author: str
    output_path: str


@dataclass
class CapeCursor:
    """Estrutura de dados de um cursor no formato de dicionário do Mousecape."""
    identifier: str
    frame_count: int
    frame_duration: float
    hotspot_x: float
    hotspot_y: float
    points_wide: float
    points_high: float
    representations: List[bytes]

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para o dicionário compatível com o plist do Mousecape."""
        return {
            'FrameCount': self.frame_count,
            'FrameDuration': float(self.frame_duration),
            'HotSpotX': float(self.hotspot_x),
            'HotSpotY': float(self.hotspot_y),
            'PointsWide': float(self.points_wide),
            'PointsHigh': float(self.points_high),
            'Representations': self.representations
        }


@dataclass(frozen=True)
class ConversionResult:
    """Resultado da execução do serviço de conversão."""
    success: bool
    output_path: str
    cursor_count: int
    file_size_bytes: int
    is_valid_plist: bool
    error_message: Optional[str] = None
