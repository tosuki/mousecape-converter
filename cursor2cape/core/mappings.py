"""
cursor2cape.core.mappings
Tabela de mapeamento e resolução de identificadores entre FreeDesktop e Mousecape (macOS).
"""

from typing import Dict, List, Optional


class CursorMappingRegistry:
    """
    Registro canônico de cursores do macOS / Mousecape associados às listas de
    nomes de arquivo candidatos do padrão X11/FreeDesktop em ordem de prioridade.
    """

    MAPPINGS: Dict[str, List[str]] = {
        # CoreGraphics Principais
        'com.apple.coregraphics.Arrow': ['left_ptr', 'arrow', 'default'],
        'com.apple.coregraphics.ArrowS': ['left_ptr', 'arrow', 'default'],
        'com.apple.coregraphics.IBeam': ['xterm', 'text'],
        'com.apple.coregraphics.IBeamS': ['xterm', 'text'],
        'com.apple.coregraphics.IBeamXOR': ['vertical-text', 'xterm'],
        'com.apple.coregraphics.Alias': ['alias', 'dnd-link', 'link'],
        'com.apple.coregraphics.Copy': ['copy', 'dnd-copy'],
        'com.apple.coregraphics.Move': ['move', 'dnd-move'],
        'com.apple.coregraphics.ArrowCtx': ['context-menu'],
        'com.apple.coregraphics.Wait': ['wait', 'watch'],
        'com.apple.coregraphics.Empty': ['__EMPTY__'],

        # CoreCursor / Indicadores Numéricos do Sistema
        'com.apple.cursor.2': ['pointer', 'hand2', 'link'],              # Link (mão apontando)
        'com.apple.cursor.3': ['not-allowed', 'crossed_circle', 'circle', 'no-drop'], # Proibido
        'com.apple.cursor.4': ['progress', 'left_ptr_watch', 'wait'],     # Ocupado / Spinner
        'com.apple.cursor.5': ['dnd-copy', 'copy'],                       # Copiar arrasto
        'com.apple.cursor.7': ['crosshair', 'cross'],                     # Mira / Precisão
        'com.apple.cursor.8': ['cross', 'tcross', 'crosshair'],           # Cruz 2
        'com.apple.cursor.9': ['target', 'crosshair'],                    # Câmera 2
        'com.apple.cursor.10': ['target', 'crosshair'],                   # Câmera
        'com.apple.cursor.11': ['grabbing'],                              # Mão fechada
        'com.apple.cursor.12': ['grab'],                                  # Mão aberta
        'com.apple.cursor.13': ['pointer', 'hand2', 'hand1'],             # Mão apontando (sistema)
        'com.apple.cursor.14': ['progress', 'left_ptr_watch'],            # Contagem crescente
        'com.apple.cursor.15': ['progress', 'left_ptr_watch'],            # Contagem decrescente
        'com.apple.cursor.16': ['progress', 'left_ptr_watch'],            # Contagem mista
        'com.apple.cursor.17': ['w-resize', 'left_side'],                 # Redimensionar Oeste (Esquerda)
        'com.apple.cursor.18': ['e-resize', 'right_side'],                # Redimensionar Leste (Direita)
        'com.apple.cursor.19': ['ew-resize', 'col-resize', 'size_hor', 'h_double_arrow'], # Redimensionar L-O
        'com.apple.cursor.20': ['cell'],                                  # Célula XOR
        'com.apple.cursor.21': ['n-resize', 'top_side'],                  # Redimensionar Norte (Cima)
        'com.apple.cursor.22': ['s-resize', 'bottom_side'],               # Redimensionar Sul (Baixo)
        'com.apple.cursor.23': ['ns-resize', 'row-resize', 'size_ver', 'v_double_arrow'], # Redimensionar N-S
        'com.apple.cursor.24': ['context-menu'],                          # Menu de contexto
        'com.apple.cursor.26': ['vertical-text'],                         # Texto vertical
        'com.apple.cursor.27': ['e-resize', 'right_side'],                # Janela L
        'com.apple.cursor.28': ['ew-resize', 'col-resize', 'size_hor'],   # Janela L-O
        'com.apple.cursor.29': ['ne-resize', 'top_right_corner', 'ur_angle'], # Janela NE
        'com.apple.cursor.30': ['nesw-resize', 'size_bdiag', 'fd_double_arrow'], # Janela NE-SO
        'com.apple.cursor.31': ['n-resize', 'top_side'],                  # Janela N
        'com.apple.cursor.32': ['ns-resize', 'row-resize', 'size_ver'],   # Janela N-S
        'com.apple.cursor.33': ['nw-resize', 'top_left_corner', 'ul_angle'], # Janela NO
        'com.apple.cursor.34': ['nwse-resize', 'size_fdiag', 'bd_double_arrow'], # Janela NO-SE
        'com.apple.cursor.35': ['se-resize', 'bottom_right_corner', 'lr_angle'], # Janela SE
        'com.apple.cursor.36': ['s-resize', 'bottom_side'],               # Janela S
        'com.apple.cursor.37': ['sw-resize', 'bottom_left_corner', 'll_angle'], # Janela SO
        'com.apple.cursor.38': ['w-resize', 'left_side'],                 # Janela O
        'com.apple.cursor.39': ['all-scroll', 'size_all', 'fleur'],       # Redimensionar em todas as direções
        'com.apple.cursor.40': ['help', 'question_arrow', 'left_ptr_help'], # Ajuda
        'com.apple.cursor.41': ['cell', 'plus'],                          # Célula / Mais
        'com.apple.cursor.42': ['zoom-in'],                               # Zoom In
        'com.apple.cursor.43': ['zoom-out'],                              # Zoom Out
    }

    @classmethod
    def get_all_identifiers(cls) -> List[str]:
        """Retorna todos os identificadores conhecidos."""
        return list(cls.MAPPINGS.keys())

    @classmethod
    def get_candidates(cls, identifier: str) -> List[str]:
        """Retorna os nomes de arquivo candidatos para um dado identificador."""
        return cls.MAPPINGS.get(identifier, [])

    @classmethod
    def is_empty_cursor(cls, identifier: str) -> bool:
        """Verifica se o identificador requer geração de textura transparente."""
        return cls.MAPPINGS.get(identifier) == ['__EMPTY__']
