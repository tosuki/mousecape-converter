"""
cursor2cape.parsers.theme_parser
Parser de metadados de temas de cursor FreeDesktop/X11 e serviço de descoberta de diretórios.
"""

import os
from typing import List, Optional
from cursor2cape.domain.models import ThemeInfo
from cursor2cape.parsers.xcursor_parser import XCursorParser


class ThemeParser:
    """Responsável por localizar temas no sistema de arquivos e ler suas definições."""

    @classmethod
    def inspect_directory(cls, theme_dir: str) -> Optional[ThemeInfo]:
        """Inspeciona um diretório para validar se é um tema de cursores válido."""
        real_path = os.path.realpath(os.path.expanduser(theme_dir))
        cursors_dir = os.path.join(real_path, 'cursors')

        if not os.path.isdir(cursors_dir):
            return None

        theme_name = os.path.basename(real_path)
        author = "Desconhecido"

        # Leitura dos arquivos de metadados padrão do FreeDesktop
        for meta_filename in ['index.theme', 'cursor.theme']:
            meta_path = os.path.join(real_path, meta_filename)
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('Name=') and theme_name == os.path.basename(real_path):
                                theme_name = line.split('=', 1)[1].strip()
                            elif line.startswith('Comment='):
                                author = line.split('=', 1)[1].strip()
                except Exception:
                    pass

        # Coleta os tamanhos nominais disponíveis no tema inspecionando arquivos válidos
        available_sizes = set()
        try:
            candidates = [
                f for f in os.listdir(cursors_dir)
                if not f.endswith(('.cur', '.ani', '.png', '.inf', '.bak', '.tmp'))
            ][:20]

            for filename in candidates:
                cursor_file = os.path.join(cursors_dir, filename)
                if os.path.isfile(cursor_file):
                    parsed = XCursorParser.parse_file(cursor_file)
                    if parsed:
                        available_sizes.update(parsed.keys())
        except Exception:
            pass

        return ThemeInfo(
            name=theme_name,
            path=real_path,
            cursors_dir=cursors_dir,
            author=author,
            available_sizes=sorted(list(available_sizes))
        )

    @classmethod
    def discover_themes(cls, search_directories: List[str]) -> List[ThemeInfo]:
        """Varre múltiplos diretórios em busca de temas de cursor válidos."""
        discovered: List[ThemeInfo] = []
        visited_paths = set()

        for base_dir in search_directories:
            expanded = os.path.realpath(os.path.expanduser(base_dir))
            if not os.path.isdir(expanded):
                continue

            # Verifica se o próprio diretório é um tema
            self_theme = cls.inspect_directory(expanded)
            if self_theme and self_theme.path not in visited_paths:
                discovered.append(self_theme)
                visited_paths.add(self_theme.path)
                continue

            # Verifica subpastas imediatas
            try:
                for entry in sorted(os.listdir(expanded)):
                    sub_path = os.path.join(expanded, entry)
                    if os.path.isdir(sub_path) and sub_path not in visited_paths:
                        theme = cls.inspect_directory(sub_path)
                        if theme:
                            discovered.append(theme)
                            visited_paths.add(theme.path)
            except Exception:
                continue

        return discovered
