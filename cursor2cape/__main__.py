"""
cursor2cape.__main__
Ponto de entrada de execução do pacote (python3 -m cursor2cape).
"""

import sys
from cursor2cape.ui.app import TUIApplication


def main():
    try:
        app = TUIApplication()
        app.run()
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário.")
        sys.exit(0)


if __name__ == '__main__':
    main()
