# cursor2cape 🖱️✨

> **Conversor arquitetural de temas de cursor Linux (Xcursor / FreeDesktop) para o formato nativo do Mousecape (`.cape`) no macOS.**

O **cursor2cape** foi desenvolvido com foco em separação de responsabilidades (SOLID), padrões de projeto (GoF) e experiência de terminal interativa (TUI) moderna com **Rich** e **Questionary**.

---

## 🏗️ Padrões de Projeto & Arquitetura

O projeto foi inteiramente fragmentado em módulos com responsabilidade única:

```
cursor2cape/
├── __init__.py
├── __main__.py               # Ponto de entrada CLI (python3 -m cursor2cape)
├── domain/                   # Camada de Domínio (Entidades e Value Objects puros)
│   ├── __init__.py
│   └── models.py             # RawCursorFrame, ThemeInfo, CapeCursor, ConversionConfig
├── parsers/                  # Camada de Leitura e Parsing
│   ├── __init__.py
│   ├── xcursor_parser.py     # Parser binário de structs do formato X11 Xcursor
│   └── theme_parser.py       # Leitor de metadados index.theme e descoberta de temas
├── core/                     # Regras de Negócio e Transformação Gráfica
│   ├── __init__.py
│   ├── mappings.py           # Registry Pattern: mapeamento canônico macOS <-> X11
│   ├── image_processor.py    # Desfeita de alpha pré-multiplicado, PNG e spritesheets
│   ├── frame_sampler.py      # Controle de taxa de quadros e restrições do macOS
│   ├── resampler.py          # Strategy Pattern: resolução nativa vs Lanczos inteligente
│   └── cape_builder.py       # Builder Pattern: construção de cursores e Property Lists
├── services/                 # Camada de Aplicação / Orquestração
│   ├── __init__.py
│   └── converter_service.py  # Facade Pattern: orquestrador desacoplado de qualquer UI
└── ui/                       # Camada de Apresentação (TUI)
    ├── __init__.py
    ├── views.py              # Componentes visuais com Rich (tabelas, painéis, status)
    └── app.py                # Controlador de fluxo interativo com Questionary
```

### Padrões Aplicados
- **Facade (`ThemeToCapeService`)**: Isola completamente a lógica de conversão da interface gráfica de terminal. O serviço pode ser importado em scripts automatizados sem depender da TUI.
- **Strategy (`ResamplingStrategy`)**: Permite alternar entre amostragem estrita (`ExactMatchResampler`) e redimensionamento adaptativo com reamostragem de alta qualidade (`LanczosAdaptiveResampler`).
- **Registry (`CursorMappingRegistry`)**: Centraliza o mapeamento de 51 identificadores de cursor do macOS com cadeias de fallback de arquivos X11.
- **Builder (`CapeCursorBuilder` & `CapeDocumentBuilder`)**: Monta representações 1x e 2x em spritesheets verticais e serializa documentos `.cape` XML compatíveis com a API do CoreGraphics.

---

## 🚀 Instalação

### 1. Pré-requisitos
- **macOS** (testado em versões modernas do sistema).
- **Python 3.9+** com suporte a pip.
- **Mousecape** instalado para aplicar os temas gerados.

### 2. Instalar Dependências do Python
No diretório deste repositório, instale as dependências:

```bash
pip3 install -r requirements.txt
```

*(Opcional recomendado)* Instale o pacote no modo editável para que fique disponível globalmente no Python:
```bash
pip3 install --user -e .
```

### 3. Instalar o Executável no `bin` do Sistema

O projeto inclui o wrapper executável `bin/cursor2cape`. Copie-o para qualquer pasta presente no seu `$PATH` (como `/usr/local/bin` ou `~/.local/bin`):

#### Opção A: No sistema global (`/usr/local/bin`)
```bash
sudo cp bin/cursor2cape /usr/local/bin/
sudo chmod +x /usr/local/bin/cursor2cape
```

#### Opção B: No diretório de usuário (`~/.local/bin`)
```bash
mkdir -p ~/.local/bin
cp bin/cursor2cape ~/.local/bin/
chmod +x ~/.local/bin/cursor2cape
```
*(Certifique-se de que `~/.local/bin` esteja no seu `$PATH` no seu `~/.zshrc` ou `~/.bash_profile`).*

---

## 🎮 Como Usar

Com o script copiado para a pasta `bin`, você não precisa mais digitar `python3`. Basta rodar diretamente em qualquer terminal:

```bash
cursor2cape
```

### Passo a Passo no Terminal Interativo (TUI):

1. **Seleção de Tema**:
   - O aplicativo localiza temas de cursor automaticamente na pasta atual, em `~/.icons`, `~/.local/share/icons` e `/usr/share/icons`.
   - Você também pode escolher a opção de colar qualquer pasta manualmente.
2. **Definição de Tamanho**:
   - Escolha o tamanho base desejado (ex: `24 pt`, `32 pt`, `48 pt` ou personalizado).
3. **Pergunta sobre Redimensionamento Inteligente (Lanczos)**:
   - Se o tema não tiver o tamanho escolhido nativamente, a TUI perguntará se você autoriza a interpolação Lanczos a partir da resolução mais próxima.
   - Caso recuse, você poderá selecionar um dos tamanhos nativos detectados.
4. **Camada HiDPI 2x Retina**:
   - Confirme se deseja incluir gráficos em alta resolução 2x (ex: 48px para base 24) para monitores Retina.
5. **Metadados & Confirmação**:
   - Revise o nome da capa, autor e arquivo de saída em uma tabela formatada.
6. **Acompanhamento com Barra de Progresso**:
   - Visualize o processamento de cada um dos 51 cursores em tempo real.
7. **Pós-Conversão**:
   - Escolha entre abrir e importar imediatamente no Mousecape (`open <tema>.cape`), revelar no Finder ou sair.

---

## ⚙️ Uso Programático / Como Biblioteca

Se quiser integrar a conversão em scripts externos ou pipelines sem interface interativa:

```python
from cursor2cape.parsers.theme_parser import ThemeParser
from cursor2cape.domain.models import ConversionConfig
from cursor2cape.services.converter_service import ThemeToCapeService

# 1. Carrega o tema
theme = ThemeParser.inspect_directory("./Yaru-Orange")

# 2. Define a configuração
config = ConversionConfig(
    target_size=24,
    include_retina=True,
    allow_resampling=True,
    cape_name="Yaru-Orange",
    author="Ubuntu / Yaru Team",
    output_path="./Yaru-Orange.cape"
)

# 3. Executa a conversão
service = ThemeToCapeService()
result = service.convert(theme, config)

if result.success:
    print(f"Sucesso! Gerados {result.cursor_count} cursores em {result.output_path}")
else:
    print(f"Erro: {result.error_message}")
```

---

## 🧪 Validação dos Arquivos `.cape`

Todos os arquivos `.cape` gerados são documentos XML Property List padrão da Apple. Você pode validar sua integridade a qualquer momento via terminal:

```bash
plutil -lint Yaru-Orange.cape
```
*(Saída esperada: `Yaru-Orange.cape: OK`)*
