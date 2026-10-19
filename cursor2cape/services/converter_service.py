"""
cursor2cape.services.converter_service
Fachada de orquestração do processo de conversão de temas para Mousecape.
"""

import os
import subprocess
from typing import Callable, Dict, Optional
from cursor2cape.domain.models import (
    ThemeInfo,
    ConversionConfig,
    ConversionResult,
    CapeCursor
)
from cursor2cape.parsers.xcursor_parser import XCursorParser
from cursor2cape.core.mappings import CursorMappingRegistry
from cursor2cape.core.resampler import (
    ResamplingStrategy,
    LanczosAdaptiveResampler,
    ExactMatchResampler
)
from cursor2cape.core.cape_builder import CapeCursorBuilder, CapeDocumentBuilder


class ThemeToCapeService:
    """
    Fachada que orquestra a leitura de cursores, aplicação de estratégias
    de resolução de tamanhos, montagem de spritesheets e exportação final.
    """

    def __init__(self, resampling_strategy: Optional[ResamplingStrategy] = None):
        self._strategy = resampling_strategy or LanczosAdaptiveResampler()

    def convert(
        self,
        theme: ThemeInfo,
        config: ConversionConfig,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> ConversionResult:
        """Executa a conversão completa do tema conforme os parâmetros informados."""
        resampler = (
            LanczosAdaptiveResampler()
            if config.allow_resampling
            else ExactMatchResampler()
        )

        cape_cursors: Dict[str, CapeCursor] = {}
        parsed_cache: Dict[str, Dict] = {}

        identifiers = CursorMappingRegistry.get_all_identifiers()
        total_steps = len(identifiers)

        for step_idx, identifier in enumerate(identifiers, start=1):
            if progress_callback:
                progress_callback(step_idx, total_steps, identifier)

            # 1. Trata cursores vazios/transparentes
            if CursorMappingRegistry.is_empty_cursor(identifier):
                cape_cursors[identifier] = CapeCursorBuilder.build_empty(
                    identifier=identifier,
                    target_size=config.target_size,
                    include_retina=config.include_retina
                )
                continue

            # 2. Busca o primeiro candidato de arquivo existente
            candidates = CursorMappingRegistry.get_candidates(identifier)
            src_filename: Optional[str] = None

            for candidate in candidates:
                cand_path = os.path.join(theme.cursors_dir, candidate)
                if os.path.isfile(cand_path):
                    src_filename = candidate
                    break

            if not src_filename:
                continue

            # 3. Lê o arquivo binário Xcursor (com cache em memória)
            if src_filename not in parsed_cache:
                parsed = XCursorParser.parse_file(os.path.join(theme.cursors_dir, src_filename))
                if parsed:
                    parsed_cache[src_filename] = parsed

            cursor_data = parsed_cache.get(src_filename)
            if not cursor_data:
                continue

            # 4. Resolve quadros 1x
            frames_1x = resampler.resolve_frames(cursor_data, config.target_size)
            if not frames_1x:
                continue

            # 5. Resolve quadros 2x Retina (se solicitado)
            frames_2x = None
            if config.include_retina:
                frames_2x = resampler.resolve_frames(cursor_data, config.target_size * 2)

            # 6. Constrói a entidade CapeCursor
            cape_cursor = CapeCursorBuilder.build_from_frames(
                identifier=identifier,
                frames_1x=frames_1x,
                frames_2x=frames_2x,
                target_size=config.target_size
            )
            cape_cursors[identifier] = cape_cursor

        if not cape_cursors:
            return ConversionResult(
                success=False,
                output_path=config.output_path,
                cursor_count=0,
                file_size_bytes=0,
                is_valid_plist=False,
                error_message="Nenhum cursor correspondente pôde ser extraído deste tema."
            )

        try:
            # 7. Salva o documento .cape
            CapeDocumentBuilder.save_to_file(config, cape_cursors)
            file_size = os.path.getsize(config.output_path)

            # 8. Valida sintaxe no macOS via plutil
            is_valid = True
            try:
                lint_proc = subprocess.run(
                    ["plutil", "-lint", config.output_path],
                    capture_output=True,
                    text=True,
                    check=False
                )
                is_valid = (lint_proc.returncode == 0)
            except Exception:
                pass

            return ConversionResult(
                success=True,
                output_path=config.output_path,
                cursor_count=len(cape_cursors),
                file_size_bytes=file_size,
                is_valid_plist=is_valid
            )
        except Exception as exc:
            return ConversionResult(
                success=False,
                output_path=config.output_path,
                cursor_count=0,
                file_size_bytes=0,
                is_valid_plist=False,
                error_message=str(exc)
            )
