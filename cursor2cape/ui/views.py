"""
cursor2cape.ui.views
Componentes de renderização visual no terminal baseados na biblioteca Rich.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from cursor2cape.domain.models import ThemeInfo, ConversionConfig, ConversionResult


class ConsoleViews:
    """Gerenciador de visualizações e painéis do console."""

    def __init__(self, console: Console):
        self._console = console

    def render_welcome_banner(self) -> None:
        """Exibe o cabeçalho principal da aplicação."""
        self._console.clear()
        self._console.print(
            Panel.fit(
                "[bold cyan]Mousecape Cape Generator[/bold cyan] [green]v2.0[/green]\n"
                "[dim]Conversor Arquitetural de Temas Xcursor para Mousecape (macOS)[/dim]",
                border_style="cyan",
                padding=(1, 2)
            )
        )

    def render_theme_summary(self, theme: ThemeInfo) -> None:
        """Exibe os dados do tema selecionado."""
        sizes_str = ", ".join(map(str, theme.available_sizes)) if theme.available_sizes else "Nenhum detectado"
        self._console.print(f"\n[green]✔[/green] Tema Selecionado: [bold]{theme.name}[/bold]")
        self._console.print(f"[dim]Autor/Origem:[/dim] {theme.author}")
        self._console.print(f"[dim]Tamanhos Nativos Encontrados:[/dim] [cyan]{sizes_str}[/cyan]\n")

    def render_resampling_notice(self, theme: ThemeInfo, target_size: int) -> None:
        """Exibe aviso de que o tamanho solicitado não é nativo no tema."""
        sizes_str = ", ".join(map(str, theme.available_sizes))
        self._console.print(
            f"\n[bold yellow]Aviso de Redimensionamento:[/bold yellow] O tema [bold]{theme.name}[/bold] "
            f"não possui nativamente o tamanho [bold cyan]{target_size}[/bold cyan] (disponíveis: {sizes_str})."
        )

    def render_config_table(self, theme: ThemeInfo, config: ConversionConfig) -> None:
        """Renderiza a tabela de confirmação dos parâmetros antes da execução."""
        table = Table(title="Configurações da Conversão", show_header=True, header_style="bold magenta")
        table.add_column("Parâmetro", style="cyan", width=26)
        table.add_column("Valor Definido", style="white")

        table.add_row("Tema de Origem", theme.name)
        table.add_row("Diretório do Tema", theme.path)
        table.add_row("Tamanho Base", f"{config.target_size} pt ({config.target_size}x{config.target_size} px)")
        table.add_row("Camada Retina 2x", f"{'Sim (' + str(config.target_size * 2) + 'px)' if config.include_retina else 'Não'}")
        table.add_row(
            "Redimensionamento Lanczos",
            "[green]Ativado[/green]" if config.allow_resampling else "[dim]Desativado[/dim]"
        )
        table.add_row("Nome da Capa", config.cape_name)
        table.add_row("Autor", config.author)
        table.add_row("Arquivo de Destino", config.output_path)

        self._console.print()
        self._console.print(table)
        self._console.print()

    def render_result_panel(self, result: ConversionResult) -> None:
        """Exibe o painel com as estatísticas de sucesso ou falha."""
        if result.success:
            file_kb = result.file_size_bytes / 1024.0
            lint_text = "[bold green]Válido (OK)[/]" if result.is_valid_plist else "[bold yellow]Não verificado[/]"

            self._console.print(
                Panel(
                    f"[bold green]✔ Conversão Concluída com Sucesso![/bold green]\n\n"
                    f"• [bold]Arquivo gerado:[/] [cyan]{result.output_path}[/cyan]\n"
                    f"• [bold]Cursores mapeados:[/] [yellow]{result.cursor_count}[/yellow] estados do macOS\n"
                    f"• [bold]Tamanho do arquivo:[/] [yellow]{file_kb:.1f} KB[/yellow]\n"
                    f"• [bold]Validação plutil macOS:[/] {lint_text}",
                    border_style="green",
                    padding=(1, 2)
                )
            )
        else:
            self._console.print(
                Panel(
                    f"[bold red]✖ Falha na Conversão do Tema[/bold red]\n\n"
                    f"• [bold]Erro ocorrido:[/] {result.error_message or 'Erro desconhecido'}",
                    border_style="red",
                    padding=(1, 2)
                )
            )
