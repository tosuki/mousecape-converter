"""
cursor2cape.ui.app
Controlador do fluxo interativo de terminal (TUI).
"""

import os
import sys
import subprocess
from typing import List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
import questionary
from questionary import Choice

from cursor2cape.domain.models import ThemeInfo, ConversionConfig
from cursor2cape.parsers.theme_parser import ThemeParser
from cursor2cape.services.converter_service import ThemeToCapeService
from cursor2cape.ui.views import ConsoleViews


class TUIApplication:
    """Controlador da interface de usuário interativa no terminal."""

    def __init__(self):
        self._console = Console()
        self._views = ConsoleViews(self._console)
        self._service = ThemeToCapeService()

    def run(self) -> None:
        """Ponto de entrada do loop da aplicação interativa."""
        self._views.render_welcome_banner()

        # 1. Seleção do Tema
        theme = self._prompt_theme_selection()
        if not theme:
            self._console.print("\n[yellow]Operação cancelada pelo usuário.[/yellow]")
            return

        self._views.render_theme_summary(theme)

        # 2. Definição do Tamanho Alvo
        target_size = self._prompt_target_size()

        # 3. Confirmação de Redimensionamento (Lanczos)
        allow_rescale = self._resolve_resampling_preference(theme, target_size)

        # 4. Inclusão da camada Retina 2x
        include_retina = questionary.confirm(
            f"Deseja incluir representação HiDPI 2x ({target_size * 2}px) para monitores Retina?",
            default=True
        ).ask()
        if include_retina is None:
            return

        # 5. Metadados do Cape
        config = self._prompt_metadata_and_config(theme, target_size, allow_rescale, include_retina)
        if not config:
            return

        # 6. Resumo e Confirmação de Início
        self._views.render_config_table(theme, config)
        if not questionary.confirm("Iniciar conversão agora?", default=True).ask():
            self._console.print("\n[yellow]Operação abortada.[/yellow]")
            return

        # 7. Execução com Barra de Progresso
        result = self._execute_conversion_with_progress(theme, config)

        # 8. Exibição de Resultados e Ações Finais
        self._views.render_result_panel(result)

        if result.success:
            self._prompt_post_conversion_actions(result.output_path)

    def _prompt_theme_selection(self) -> Optional[ThemeInfo]:
        """Varre os diretórios padrão e oferece seleção ao usuário."""
        search_paths = [
            os.getcwd(),
            os.path.expanduser("~/.icons"),
            os.path.expanduser("~/.local/share/icons"),
            "/usr/share/icons"
        ]
        discovered = ThemeParser.discover_themes(search_paths)

        choices: List[Choice] = []
        for t in discovered:
            sizes_str = ", ".join(map(str, t.available_sizes)) if t.available_sizes else "desconhecidos"
            label = f"{t.name} [dim]({t.path}) - Tamanhos: [{sizes_str}][/dim]"
            choices.append(Choice(title=label, value=t))

        choices.append(Choice(title="📂 Inserir caminho de outro diretório manualmente...", value="MANUAL"))

        selected = questionary.select(
            "Selecione o tema de cursor a converter:",
            choices=choices,
            use_indicator=True,
        ).ask()

        if selected is None:
            return None

        if selected == "MANUAL":
            while True:
                path = questionary.path("Digite ou cole o caminho do diretório do tema:").ask()
                if not path:
                    return None
                theme = ThemeParser.inspect_directory(path)
                if theme:
                    return theme
                self._console.print(
                    "[red]Erro:[/red] Não foi encontrada uma pasta 'cursors/' válida com arquivos Xcursor nesse caminho."
                )

        return selected

    def _prompt_target_size(self) -> int:
        """Solicita ao usuário a dimensão básica desejada."""
        choice = questionary.select(
            "Qual tamanho base de cursor você deseja para a capa?",
            choices=[
                Choice("24 pt (Padrão macOS / Mais comum)", value=24),
                Choice("32 pt (Médio)", value=32),
                Choice("48 pt (Grande)", value=48),
                Choice("Outro tamanho personalizado...", value="CUSTOM")
            ],
            default=24
        ).ask()

        if choice is None:
            sys.exit(0)

        if choice == "CUSTOM":
            raw = questionary.text("Digite o tamanho em pixels (ex: 28, 64):").ask()
            try:
                return max(16, int(raw.strip()))
            except Exception:
                return 24

        return int(choice)

    def _resolve_resampling_preference(self, theme: ThemeInfo, target_size: int) -> bool:
        """
        Determina se o redimensionamento inteligente será ativado,
        perguntando explicitamente ao usuário caso o tamanho não seja nativo.
        """
        has_native_target = target_size in theme.available_sizes
        has_native_retina = (target_size * 2) in theme.available_sizes

        if not has_native_target:
            self._views.render_resampling_notice(theme, target_size)
            allow = questionary.confirm(
                f"Deseja ativar o redimensionamento inteligente (Lanczos) para gerar o tamanho {target_size} a partir do mais próximo?",
                default=True
            ).ask()

            if not allow:
                self._console.print("[yellow]Redimensionamento desativado.[/yellow]")
                if theme.available_sizes:
                    native_choice = questionary.select(
                        "Selecione um dos tamanhos nativos disponíveis neste tema:",
                        choices=[Choice(f"{s} pt", value=s) for s in theme.available_sizes]
                    ).ask()
                    target_size = int(native_choice)
                return False
            return True

        if not has_native_retina:
            return questionary.confirm(
                f"O tamanho {target_size} é nativo, mas a camada Retina 2x ({target_size * 2}) não está presente. Deseja permitir redimensionamento inteligente para a camada Retina?",
                default=True
            ).ask() or False

        return True

    def _prompt_metadata_and_config(
        self,
        theme: ThemeInfo,
        target_size: int,
        allow_rescale: bool,
        include_retina: bool
    ) -> Optional[ConversionConfig]:
        """Solicita os metadados finais de empacotamento da capa."""
        self._console.print()
        cape_name = questionary.text(
            "Nome da Capa (Cape Name):",
            default=theme.name
        ).ask()
        if cape_name is None:
            return None

        author = questionary.text(
            "Autor / Créditos:",
            default=theme.author
        ).ask()
        if author is None:
            return None

        default_output = os.path.join(os.getcwd(), f"{cape_name}.cape")
        output_path = questionary.text(
            "Caminho do arquivo final .cape:",
            default=default_output
        ).ask()
        if output_path is None:
            return None

        return ConversionConfig(
            target_size=target_size,
            include_retina=include_retina,
            allow_resampling=allow_rescale,
            cape_name=cape_name,
            author=author,
            output_path=os.path.abspath(output_path)
        )

    def _execute_conversion_with_progress(
        self,
        theme: ThemeInfo,
        config: ConversionConfig
    ):
        """Executa a conversão conectando o serviço à barra de progresso Rich."""
        self._console.print()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self._console
        ) as progress:
            task = progress.add_task("[cyan]Convertendo cursores...", total=51)

            def on_progress(current, total, ident):
                name = ident.split('.')[-1]
                progress.update(task, completed=current, total=total, description=f"[cyan]Processando:[/] [bold]{name}[/]")

            return self._service.convert(
                theme=theme,
                config=config,
                progress_callback=on_progress
            )

    def _prompt_post_conversion_actions(self, output_path: str) -> None:
        """Ações complementares após a conclusão da conversão."""
        action = questionary.select(
            "O que deseja fazer agora?",
            choices=[
                Choice("🚀 Abrir e Importar no Mousecape agora", value="OPEN"),
                Choice("📁 Revelar arquivo no Finder", value="FINDER"),
                Choice("Sair", value="EXIT")
            ]
        ).ask()

        if action == "OPEN":
            self._console.print("[cyan]Abrindo no Mousecape...[/cyan]")
            subprocess.run(["open", output_path], check=False)
        elif action == "FINDER":
            subprocess.run(["open", "-R", output_path], check=False)

        self._console.print("\n[bold green]Concluído com sucesso![/bold green]\n")
