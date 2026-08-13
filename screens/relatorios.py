from datetime import datetime

from kivy.graphics import (
    Color,
    Rectangle,
    RoundedRectangle,
)
from kivy.metrics import dp
from kivy.uix.widget import Widget

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import (
    MDFillRoundFlatIconButton,
    MDIconButton,
)
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from database.database import db


MESES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

ABREVIACOES = {
    1: "JAN",
    2: "FEV",
    3: "MAR",
    4: "ABR",
    5: "MAI",
    6: "JUN",
    7: "JUL",
    8: "AGO",
    9: "SET",
    10: "OUT",
    11: "NOV",
    12: "DEZ",
}


def formatar_moeda(valor):
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        valor = 0.0

    texto = f"{valor:,.2f}"

    texto = (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


class BarraProgresso(Widget):

    def __init__(
        self,
        percentual=0,
        cor=(0.20, 0.82, 0.55, 1),
        altura=8,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.size_hint_y = None
        self.height = dp(altura)
        self.percentual = percentual
        self.cor = cor

        with self.canvas:
            Color(0.12, 0.15, 0.22, 1)

            self.fundo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(altura / 2)],
            )

            Color(*self.cor)

            self.preenchimento = RoundedRectangle(
                pos=self.pos,
                size=(0, self.height),
                radius=[dp(altura / 2)],
            )

        self.bind(
            pos=self.atualizar_canvas,
            size=self.atualizar_canvas,
        )

    def atualizar_canvas(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

        largura = self.width * max(
            0,
            min(self.percentual, 1),
        )

        self.preenchimento.pos = self.pos
        self.preenchimento.size = (
            largura,
            self.height,
        )


class CardResumoRelatorio(MDCard):

    def __init__(
        self,
        titulo,
        valor,
        cor,
        icone,
        subtitulo,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(132)
        self.padding = dp(14)
        self.spacing = dp(5)
        self.radius = [18, 18, 18, 18]
        self.elevation = 1
        self.md_bg_color = (0.07, 0.10, 0.17, 1)

        cabecalho = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(34),
        )

        cabecalho.add_widget(
            MDLabel(
                text=titulo,
                font_style="Caption",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.68, 0.73, 0.82, 1),
            )
        )

        cabecalho.add_widget(
            MDIconButton(
                icon=icone,
                disabled=True,
                theme_icon_color="Custom",
                icon_color=cor,
            )
        )

        self.label_valor = MDLabel(
            text=valor,
            font_style="H5",
            bold=True,
            theme_text_color="Custom",
            text_color=cor,
            size_hint_y=None,
            height=dp(42),
            shorten=True,
            shorten_from="right",
        )

        self.label_subtitulo = MDLabel(
            text=subtitulo,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.50, 0.56, 0.66, 1),
            size_hint_y=None,
            height=dp(24),
        )

        self.add_widget(cabecalho)
        self.add_widget(self.label_valor)
        self.add_widget(self.label_subtitulo)

    def atualizar(
        self,
        valor,
        subtitulo=None,
    ):
        self.label_valor.text = valor

        if subtitulo is not None:
            self.label_subtitulo.text = subtitulo


class ItemCategoriaRelatorio(MDCard):

    def __init__(
        self,
        posicao,
        categoria,
        total,
        percentual,
        quantidade,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(122)
        self.padding = dp(14)
        self.spacing = dp(8)
        self.radius = [14, 14, 14, 14]
        self.elevation = 1
        self.md_bg_color = (0.07, 0.10, 0.17, 1)

        linha = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(34),
            spacing=dp(8),
        )

        ranking = MDLabel(
            text=f"#{posicao}",
            bold=True,
            size_hint_x=None,
            width=dp(42),
            theme_text_color="Custom",
            text_color=(0.22, 0.74, 0.97, 1),
        )

        nome = MDLabel(
            text=categoria,
            bold=True,
            theme_text_color="Custom",
            text_color=(0.94, 0.96, 0.98, 1),
        )

        valor = MDLabel(
            text=formatar_moeda(total),
            halign="right",
            valign="middle",
            bold=True,
            size_hint_x=None,
            width=dp(118),
            text_size=(dp(118), None),
            theme_text_color="Custom",
            text_color=(0.96, 0.45, 0.48, 1),
        )

        linha.add_widget(ranking)
        linha.add_widget(nome)
        linha.add_widget(valor)

        detalhes = MDLabel(
            text=(
                f"{percentual:.1f}% do total • "
                f"{quantidade} lançamento(s)"
            ),
            font_style="Caption",
            size_hint_y=None,
            height=dp(22),
            theme_text_color="Custom",
            text_color=(0.55, 0.61, 0.70, 1),
        )

        self.add_widget(linha)
        self.add_widget(detalhes)

        self.add_widget(
            BarraProgresso(
                percentual=percentual / 100,
                cor=(0.96, 0.35, 0.38, 1),
                altura=9,
            )
        )


class LinhaMes(MDCard):

    def __init__(
        self,
        mes,
        receitas,
        despesas,
        maior_valor,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(132)
        self.padding = dp(12)
        self.spacing = dp(7)
        self.radius = [14, 14, 14, 14]
        self.elevation = 0
        self.md_bg_color = (0.055, 0.08, 0.14, 1)

        cabecalho = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
        )

        mes_label = MDLabel(
            text=ABREVIACOES[mes],
            bold=True,
            size_hint_x=None,
            width=dp(54),
            theme_text_color="Custom",
            text_color=(0.92, 0.94, 0.98, 1),
        )

        saldo = receitas - despesas

        saldo_label = MDLabel(
            text=f"Saldo: {formatar_moeda(saldo)}",
            halign="right",
            theme_text_color="Custom",
            text_color=(
                (0.20, 0.82, 0.55, 1)
                if saldo >= 0
                else (0.96, 0.35, 0.38, 1)
            ),
        )

        cabecalho.add_widget(mes_label)
        cabecalho.add_widget(saldo_label)

        base = maior_valor if maior_valor > 0 else 1

        linha_receita = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(24),
            spacing=dp(8),
        )

        linha_receita.add_widget(
            MDLabel(
                text="Receitas",
                size_hint_x=None,
                width=dp(72),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.20, 0.82, 0.55, 1),
            )
        )

        linha_receita.add_widget(
            MDLabel(
                text=formatar_moeda(receitas),
                halign="right",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.20, 0.82, 0.55, 1),
            )
        )

        linha_despesa = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(24),
            spacing=dp(8),
        )

        linha_despesa.add_widget(
            MDLabel(
                text="Despesas",
                size_hint_x=None,
                width=dp(72),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.96, 0.35, 0.38, 1),
            )
        )

        linha_despesa.add_widget(
            MDLabel(
                text=formatar_moeda(despesas),
                halign="right",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.96, 0.35, 0.38, 1),
            )
        )

        self.add_widget(cabecalho)
        self.add_widget(linha_receita)

        self.add_widget(
            BarraProgresso(
                percentual=receitas / base,
                cor=(0.20, 0.82, 0.55, 1),
                altura=8,
            )
        )

        self.add_widget(linha_despesa)

        self.add_widget(
            BarraProgresso(
                percentual=despesas / base,
                cor=(0.96, 0.35, 0.38, 1),
                altura=8,
            )
        )


class RelatoriosScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        agora = datetime.now()

        self.filtro_mes = agora.month
        self.filtro_ano = agora.year

        self.menu_mes = None
        self.menu_ano = None

        with self.canvas.before:
            Color(0.02, 0.04, 0.09, 1)

            self.fundo = Rectangle(
                pos=self.pos,
                size=self.size,
            )

        self.bind(
            pos=self.atualizar_fundo,
            size=self.atualizar_fundo,
        )

        raiz = MDBoxLayout(
            orientation="vertical",
        )

        raiz.add_widget(
            self.criar_cabecalho()
        )

        scroll = MDScrollView(
            do_scroll_x=False,
        )

        self.conteudo = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[
                dp(16),
                dp(8),
                dp(16),
                dp(40),
            ],
            spacing=dp(16),
        )

        self.conteudo.add_widget(
            self.criar_filtros()
        )

        self.conteudo.add_widget(
            self.criar_resumo()
        )

        self.conteudo.add_widget(
            self.criar_titulo_secao(
                titulo="Despesas por categoria",
                subtitulo=(
                    "Categorias com maior impacto "
                    "no período selecionado"
                ),
            )
        )

        self.lista_categorias = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(10),
        )

        self.conteudo.add_widget(
            self.lista_categorias
        )

        self.conteudo.add_widget(
            self.criar_titulo_secao(
                titulo="Evolução mensal",
                subtitulo=(
                    "Comparação entre receitas, "
                    "despesas e saldo"
                ),
            )
        )

        self.lista_meses = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(10),
        )

        self.conteudo.add_widget(
            self.lista_meses
        )

        scroll.add_widget(
            self.conteudo
        )

        raiz.add_widget(scroll)
        self.add_widget(raiz)

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

    def criar_cabecalho(self):
        cabecalho = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(92),
            padding=[
                dp(10),
                dp(18),
                dp(16),
                dp(8),
            ],
        )

        voltar = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(0.95, 0.96, 0.98, 1),
        )

        voltar.bind(
            on_release=self.voltar_dashboard
        )

        textos = MDBoxLayout(
            orientation="vertical",
        )

        textos.add_widget(
            MDLabel(
                text="Relatórios financeiros",
                font_style="H5",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        textos.add_widget(
            MDLabel(
                text="Visão geral do seu desempenho financeiro",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.55, 0.61, 0.70, 1),
            )
        )

        cabecalho.add_widget(voltar)
        cabecalho.add_widget(textos)

        return cabecalho

    def criar_filtros(self):
        card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(78),
            padding=dp(12),
            spacing=dp(10),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        self.botao_mes = MDFillRoundFlatIconButton(
            text=MESES[self.filtro_mes].upper(),
            icon="calendar-month-outline",
            size_hint_x=0.60,
            md_bg_color=(0.10, 0.14, 0.22, 1),
        )

        self.botao_ano = MDFillRoundFlatIconButton(
            text=str(self.filtro_ano),
            icon="calendar",
            size_hint_x=0.40,
            md_bg_color=(0.10, 0.14, 0.22, 1),
        )

        self.botao_mes.bind(
            on_release=self.abrir_menu_mes
        )

        self.botao_ano.bind(
            on_release=self.abrir_menu_ano
        )

        card.add_widget(self.botao_mes)
        card.add_widget(self.botao_ano)

        return card

    def criar_resumo(self):
        bloco = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(10),
        )

        self.card_saldo = CardResumoRelatorio(
            titulo="SALDO DO PERÍODO",
            valor="R$ 0,00",
            cor=(0.22, 0.74, 0.97, 1),
            icone="wallet-outline",
            subtitulo="Resultado do período",
        )
        self.card_saldo.height = dp(146)
        self.card_saldo.md_bg_color = (0.055, 0.20, 0.40, 1)
        self.card_saldo.label_valor.font_style = "H4"

        linha_secundaria = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(132),
            spacing=dp(10),
        )

        self.card_receitas = CardResumoRelatorio(
            titulo="Receitas",
            valor="R$ 0,00",
            cor=(0.20, 0.82, 0.55, 1),
            icone="arrow-down-bold-circle-outline",
            subtitulo="Entradas no período",
            size_hint_x=0.5,
        )

        self.card_despesas = CardResumoRelatorio(
            titulo="Despesas",
            valor="R$ 0,00",
            cor=(0.96, 0.35, 0.38, 1),
            icone="arrow-up-bold-circle-outline",
            subtitulo="Saídas no período",
            size_hint_x=0.5,
        )

        linha_secundaria.add_widget(self.card_receitas)
        linha_secundaria.add_widget(self.card_despesas)

        bloco.add_widget(self.card_saldo)
        bloco.add_widget(linha_secundaria)

        return bloco

    def criar_titulo_secao(
        self,
        titulo,
        subtitulo,
    ):
        area = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(2),
        )

        area.add_widget(
            MDLabel(
                text=titulo,
                font_style="H6",
                bold=True,
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        area.add_widget(
            MDLabel(
                text=subtitulo,
                font_style="Caption",
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=(0.55, 0.61, 0.70, 1),
            )
        )

        return area

    def on_pre_enter(self, *_):
        self.carregar_relatorio()

    def abrir_menu_mes(self, *_):
        itens = [
            {
                "text": "Todos os meses",
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": (
                    lambda:
                    self.selecionar_mes(None)
                ),
            }
        ]

        for numero, nome in MESES.items():
            itens.append(
                {
                    "text": nome,
                    "viewclass": "OneLineListItem",
                    "height": dp(48),
                    "on_release": (
                        lambda mes=numero:
                        self.selecionar_mes(mes)
                    ),
                }
            )

        if self.menu_mes:
            self.menu_mes.dismiss()

        self.menu_mes = MDDropdownMenu(
            caller=self.botao_mes,
            items=itens,
            width_mult=4,
        )

        self.menu_mes.open()

    def selecionar_mes(self, mes):
        self.filtro_mes = mes

        self.botao_mes.text = (
            MESES[mes].upper()
            if mes is not None
            else "TODOS OS MESES"
        )

        if self.menu_mes:
            self.menu_mes.dismiss()
            self.menu_mes = None

        self.carregar_relatorio()

    def abrir_menu_ano(self, *_):
        anos = db.obter_anos_disponiveis()

        itens = []

        for ano in anos:
            itens.append(
                {
                    "text": str(ano),
                    "viewclass": "OneLineListItem",
                    "height": dp(48),
                    "on_release": (
                        lambda ano_item=ano:
                        self.selecionar_ano(
                            ano_item
                        )
                    ),
                }
            )

        if self.menu_ano:
            self.menu_ano.dismiss()

        self.menu_ano = MDDropdownMenu(
            caller=self.botao_ano,
            items=itens,
            width_mult=3,
        )

        self.menu_ano.open()

    def selecionar_ano(self, ano):
        self.filtro_ano = ano
        self.botao_ano.text = str(ano)

        if self.menu_ano:
            self.menu_ano.dismiss()
            self.menu_ano = None

        self.carregar_relatorio()

    def carregar_relatorio(self):
        try:
            resumo = db.obter_resumo_relatorio(
                mes=self.filtro_mes,
                ano=self.filtro_ano,
            )

            categorias = db.obter_totais_por_categoria(
                tipo="Despesa",
                mes=self.filtro_mes,
                ano=self.filtro_ano,
            )

            evolucao = db.obter_evolucao_mensal(
                ano=self.filtro_ano,
            )

        except Exception as erro:
            print(
                "Erro ao carregar relatórios:",
                erro,
            )

            resumo = {
                "receitas": 0,
                "despesas": 0,
                "saldo": 0,
            }

            categorias = []
            evolucao = []

        self.card_receitas.atualizar(
            formatar_moeda(
                resumo["receitas"]
            ),
            "Entradas no período",
        )

        self.card_despesas.atualizar(
            formatar_moeda(
                resumo["despesas"]
            ),
            "Saídas no período",
        )

        saldo = resumo["saldo"]

        self.card_saldo.atualizar(
            formatar_moeda(saldo),
            (
                "Resultado positivo"
                if saldo >= 0
                else "Resultado negativo"
            ),
        )

        self.card_saldo.label_valor.text_color = (
            (0.20, 0.82, 0.55, 1)
            if saldo >= 0
            else (0.96, 0.35, 0.38, 1)
        )

        self.lista_categorias.clear_widgets()

        total_despesas = resumo["despesas"]

        if not categorias:
            self.lista_categorias.add_widget(
                MDCard(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(96),
                    padding=dp(16),
                    radius=[14, 14, 14, 14],
                    md_bg_color=(0.07, 0.10, 0.17, 1),
                )
            )

            card_vazio = self.lista_categorias.children[0]

            card_vazio.add_widget(
                MDLabel(
                    text=(
                        "Nenhuma despesa encontrada "
                        "para o período."
                    ),
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.55, 0.61, 0.70, 1),
                )
            )

        else:
            for posicao, categoria in enumerate(
                categorias,
                start=1,
            ):
                percentual = (
                    categoria["total"]
                    / total_despesas
                    * 100
                    if total_despesas > 0
                    else 0
                )

                self.lista_categorias.add_widget(
                    ItemCategoriaRelatorio(
                        posicao=posicao,
                        categoria=(
                            categoria["categoria"]
                        ),
                        total=categoria["total"],
                        percentual=percentual,
                        quantidade=(
                            categoria["quantidade"]
                        ),
                    )
                )

        self.lista_meses.clear_widgets()

        maior_valor = 0

        for item in evolucao:
            maior_valor = max(
                maior_valor,
                item["receitas"],
                item["despesas"],
            )

        meses_com_dados = [
            item
            for item in evolucao
            if (
                item["receitas"] != 0
                or item["despesas"] != 0
            )
        ]

        if not meses_com_dados:
            card_vazio = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(96),
                padding=dp(16),
                radius=[14, 14, 14, 14],
                md_bg_color=(0.07, 0.10, 0.17, 1),
            )

            card_vazio.add_widget(
                MDLabel(
                    text=(
                        "Não há movimentações "
                        "para o ano selecionado."
                    ),
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.55, 0.61, 0.70, 1),
                )
            )

            self.lista_meses.add_widget(
                card_vazio
            )

        else:
            for item in meses_com_dados:
                self.lista_meses.add_widget(
                    LinhaMes(
                        mes=item["mes"],
                        receitas=item["receitas"],
                        despesas=item["despesas"],
                        maior_valor=maior_valor,
                    )
                )

    def voltar_dashboard(self, *_):
        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "dashboard",
            "right",
        )