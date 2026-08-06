from datetime import datetime

from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import (
    MDFillRoundFlatIconButton,
    MDFloatingActionButton,
    MDIconButton,
    MDRaisedButton,
    MDFlatButton,
)
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

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


def formatar_data(data_banco):
    try:
        return datetime.strptime(
            data_banco,
            "%Y-%m-%d",
        ).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return data_banco or ""


class CardSaldoPrincipal(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(210)
        self.padding = dp(20)
        self.spacing = dp(10)
        self.radius = [24, 24, 24, 24]
        self.elevation = 3
        self.md_bg_color = (0.055, 0.20, 0.40, 1)

        topo = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
        )

        topo.add_widget(
            MDLabel(
                text="SALDO DO PERÍODO",
                font_style="Caption",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.72, 0.84, 0.98, 1),
            )
        )

        topo.add_widget(
            MDIconButton(
                icon="wallet-outline",
                disabled=True,
                theme_icon_color="Custom",
                icon_color=(0.82, 0.90, 1, 1),
            )
        )

        self.valor_label = MDLabel(
            text="R$ 0,00",
            font_style="H3",
            bold=True,
            size_hint_y=None,
            height=dp(66),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )

        self.label_resultado = MDLabel(
            text="Resultado do período",
            font_style="Caption",
            size_hint_y=None,
            height=dp(24),
            theme_text_color="Custom",
            text_color=(0.72, 0.84, 0.98, 1),
        )

        self.add_widget(topo)
        self.add_widget(self.valor_label)
        self.add_widget(self.label_resultado)

    def atualizar_valor(self, valor, saldo_numerico=0):
        self.valor_label.text = valor

        if saldo_numerico >= 0:
            self.label_resultado.text = (
                "Seu resultado está positivo"
            )
            self.label_resultado.text_color = (
                0.55, 0.96, 0.76, 1
            )
        else:
            self.label_resultado.text = (
                "Seu resultado está negativo"
            )
            self.label_resultado.text_color = (
                1.00, 0.68, 0.68, 1
            )


class MiniCardResumo(MDCard):

    def __init__(
        self,
        titulo,
        valor,
        icone,
        cor,
        subtitulo,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(126)
        self.padding = dp(14)
        self.spacing = dp(4)
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
                text_color=(0.66, 0.72, 0.82, 1),
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

        self.valor_label = MDLabel(
            text=valor,
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=dp(42),
            theme_text_color="Custom",
            text_color=cor,
        )

        self.subtitulo_label = MDLabel(
            text=subtitulo,
            font_style="Caption",
            size_hint_y=None,
            height=dp(22),
            theme_text_color="Custom",
            text_color=(0.47, 0.53, 0.63, 1),
        )

        self.add_widget(cabecalho)
        self.add_widget(self.valor_label)
        self.add_widget(self.subtitulo_label)

    def atualizar_valor(self, valor):
        self.valor_label.text = valor


class ItemMovimentacao(MDCard):

    def __init__(
        self,
        transacao_id,
        descricao,
        categoria,
        data,
        data_banco,
        valor,
        tipo,
        status,
        data_pagamento,
        tela_dashboard,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.transacao_id = transacao_id
        self.tipo = tipo
        self.status_original = status
        self.tela_dashboard = tela_dashboard

        status_exibicao = (
            db.obter_status_exibicao(
                status,
                data_banco,
            )
            if tipo == "Despesa"
            else "Recebido"
        )

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(
            104
            if tipo == "Despesa"
            else 84
        )
        self.padding = dp(12)
        self.spacing = dp(10)
        self.radius = [18, 18, 18, 18]
        self.elevation = 1
        self.md_bg_color = (0.065, 0.09, 0.15, 1)

        cor = (
            (0.20, 0.82, 0.55, 1)
            if tipo == "Receita"
            else (0.96, 0.35, 0.38, 1)
        )

        icone_widget = MDIconButton(
            icon=(
                "arrow-down-bold-circle"
                if tipo == "Receita"
                else "arrow-up-bold-circle"
            ),
            theme_icon_color="Custom",
            icon_color=cor,
            pos_hint={"center_y": 0.5},
            disabled=True,
        )

        informacoes = MDBoxLayout(
            orientation="vertical",
            spacing=dp(2),
        )

        informacoes.add_widget(
            MDLabel(
                text=descricao,
                font_style="Subtitle1",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        detalhes_data = (
            f"Pago em {formatar_data(data_pagamento)}"
            if (
                tipo == "Despesa"
                and status_exibicao == "Pago"
                and data_pagamento
            )
            else (
                f"Venceu em {data}"
                if status_exibicao == "Atrasado"
                else f"Vence em {data}"
            )
        )

        if tipo == "Receita":
            detalhes_data = data

        informacoes.add_widget(
            MDLabel(
                text=f"{categoria} • {detalhes_data}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.55, 0.61, 0.70, 1),
            )
        )

        if tipo == "Despesa":
            cor_status = {
                "Pago": (0.20, 0.82, 0.55, 1),
                "Pendente": (1.00, 0.70, 0.25, 1),
                "Atrasado": (0.96, 0.35, 0.38, 1),
            }[status_exibicao]

            informacoes.add_widget(
                MDLabel(
                    text=status_exibicao.upper(),
                    font_style="Caption",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=cor_status,
                )
            )

        valor_label = MDLabel(
            text=valor,
            halign="right",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=cor,
            size_hint_x=0.25,
        )

        acoes = MDBoxLayout(
            orientation="horizontal",
            adaptive_width=True,
            spacing=dp(2),
        )

        if (
            tipo == "Despesa"
            and status_exibicao != "Pago"
        ):
            botao_pagar = MDFlatButton(
                text="PAGAR",
                theme_text_color="Custom",
                text_color=(0.20, 0.82, 0.55, 1),
            )

            botao_pagar.bind(
                on_release=self.marcar_como_paga
            )

            acoes.add_widget(botao_pagar)

        botao_editar = MDIconButton(
            icon="pencil-outline",
            theme_icon_color="Custom",
            icon_color=(0.55, 0.70, 0.95, 1),
            pos_hint={"center_y": 0.5},
        )

        botao_editar.bind(
            on_release=self.abrir_edicao
        )

        acoes.add_widget(botao_editar)

        self.add_widget(icone_widget)
        self.add_widget(informacoes)
        self.add_widget(valor_label)
        self.add_widget(acoes)

    def marcar_como_paga(self, *_):
        try:
            db.marcar_transacao_como_paga(
                self.transacao_id
            )
        except Exception as erro:
            print(
                "Erro ao marcar como paga:",
                erro,
            )
            return

        self.tela_dashboard.carregar_dados()

    def abrir_edicao(self, *_):
        self.tela_dashboard.abrir_edicao_transacao(
            self.transacao_id
        )


class DashboardScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        agora = datetime.now()

        self.filtro_tipo = "Todos"
        self.filtro_mes = agora.month
        self.filtro_ano = agora.year

        self.menu_mes = None
        self.menu_ano = None

        with self.canvas.before:
            Color(0.02, 0.04, 0.09, 1)
            self.fundo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[0],
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
        raiz.add_widget(
            self.criar_conteudo()
        )

        self.add_widget(raiz)

        botao_adicionar = MDFloatingActionButton(
            icon="plus",
            pos_hint={
                "right": 0.94,
                "y": 0.08,
            },
            md_bg_color=(0.10, 0.45, 0.95, 1),
        )

        botao_adicionar.bind(
            on_release=self.abrir_nova_transacao
        )

        self.add_widget(botao_adicionar)

        self.menu_lateral = self.criar_menu_lateral()
        self.add_widget(self.menu_lateral)

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

    def criar_cabecalho(self):
        cabecalho = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(116),
            padding=[
                dp(8),
                dp(8),
                dp(16),
                dp(8),
            ],
            spacing=dp(4),
        )

        topo = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            spacing=dp(4),
        )

        botao_menu = MDIconButton(
            icon="menu",
            theme_icon_color="Custom",
            icon_color=(0.95, 0.97, 1, 1),
            pos_hint={"center_y": 0.5},
        )

        botao_menu.bind(
            on_release=self.abrir_menu_lateral
        )

        titulo_app = MDLabel(
            text="ControledefinançasPRO",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.97, 0.98, 1, 1),
        )

        topo.add_widget(botao_menu)
        topo.add_widget(titulo_app)

        textos = MDBoxLayout(
            orientation="vertical",
            padding=[
                dp(8),
                0,
                0,
                0,
            ],
        )

        hora = datetime.now().hour

        if hora < 12:
            saudacao_texto = "Bom dia, Douglas"
        elif hora < 18:
            saudacao_texto = "Boa tarde, Douglas"
        else:
            saudacao_texto = "Boa noite, Douglas"

        self.label_saudacao = MDLabel(
            text=saudacao_texto,
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.92, 0.94, 0.98, 1),
        )

        subtitulo = MDLabel(
            text=(
                "Seu dinheiro, de forma simples "
                "e inteligente"
            ),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.52, 0.59, 0.69, 1),
        )

        textos.add_widget(self.label_saudacao)
        textos.add_widget(subtitulo)

        cabecalho.add_widget(topo)
        cabecalho.add_widget(textos)

        return cabecalho

    def criar_menu_lateral(self):
        menu = MDCard(
            orientation="vertical",
            size_hint=(None, 1),
            width=dp(300),
            x=-dp(300),
            y=0,
            padding=[
                dp(14),
                dp(18),
                dp(14),
                dp(18),
            ],
            spacing=dp(10),
            radius=[0, 22, 22, 0],
            elevation=10,
            md_bg_color=(0.045, 0.07, 0.13, 1),
        )

        cabecalho_menu = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(58),
        )

        titulo_menu = MDLabel(
            text="ControledefinançasPRO",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.97, 0.98, 1, 1),
        )

        fechar = MDIconButton(
            icon="close",
            theme_icon_color="Custom",
            icon_color=(0.78, 0.82, 0.90, 1),
        )

        fechar.bind(
            on_release=self.fechar_menu_lateral
        )

        cabecalho_menu.add_widget(titulo_menu)
        cabecalho_menu.add_widget(fechar)
        menu.add_widget(cabecalho_menu)

        itens_menu = [
            (
                "INÍCIO",
                "home-outline",
                "dashboard",
                (0.36, 0.78, 1, 1),
            ),
            (
                "RELATÓRIOS",
                "chart-box-outline",
                "relatorios",
                (0.36, 0.78, 1, 1),
            ),
            (
                "ALERTAS",
                "bell-outline",
                "alertas",
                (1.00, 0.70, 0.25, 1),
            ),
            (
                "CATEGORIAS",
                "tag-multiple-outline",
                "categorias",
                (0.40, 0.82, 1, 1),
            ),
            (
                "CONFIGURAÇÕES",
                "cog-outline",
                "configuracoes",
                (0.72, 0.76, 0.86, 1),
            ),
        ]

        for texto, icone, tela, cor in itens_menu:
            botao = MDFillRoundFlatIconButton(
                text=texto,
                icon=icone,
                size_hint_x=1,
                size_hint_y=None,
                height=dp(48),
                md_bg_color=(0.08, 0.12, 0.20, 1),
                text_color=(0.92, 0.94, 0.98, 1),
                icon_color=cor,
            )

            botao.bind(
                on_release=(
                    lambda *_,
                    nome_tela=tela:
                    self.navegar_pelo_menu(
                        nome_tela
                    )
                )
            )

            menu.add_widget(botao)

        menu.add_widget(
            MDLabel(
                text=(
                    "Controle suas finanças "
                    "de forma simples e inteligente."
                ),
                font_style="Caption",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.48, 0.54, 0.64, 1),
            )
        )

        return menu

    def abrir_menu_lateral(self, *_):
        Animation.cancel_all(
            self.menu_lateral
        )

        Animation(
            x=0,
            duration=0.22,
            transition="out_quad",
        ).start(
            self.menu_lateral
        )

    def fechar_menu_lateral(self, *_):
        Animation.cancel_all(
            self.menu_lateral
        )

        Animation(
            x=-self.menu_lateral.width,
            duration=0.20,
            transition="in_quad",
        ).start(
            self.menu_lateral
        )

    def navegar_pelo_menu(
        self,
        nome_tela,
    ):
        self.fechar_menu_lateral()

        if nome_tela == "dashboard":
            return

        MDApp.get_running_app().ir_para_tela(
            nome_tela,
            "left",
        )

    def criar_conteudo(self):
        scroll = ScrollView(
            do_scroll_x=False,
        )

        self.container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[
                dp(16),
                dp(8),
                dp(16),
                dp(110),
            ],
            spacing=dp(16),
        )

        self.card_saldo = CardSaldoPrincipal()

        self.container.add_widget(
            self.card_saldo
        )

        linha_resumo = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(12),
        )

        self.card_receitas = MiniCardResumo(
            titulo="RECEITAS",
            valor="R$ 0,00",
            icone="arrow-down-circle-outline",
            cor=(0.20, 0.82, 0.55, 1),
            subtitulo="Entradas do período",
            size_hint_x=0.5,
        )

        self.card_despesas = MiniCardResumo(
            titulo="DESPESAS",
            valor="R$ 0,00",
            icone="arrow-up-circle-outline",
            cor=(0.96, 0.35, 0.38, 1),
            subtitulo="Saídas do período",
            size_hint_x=0.5,
        )

        linha_resumo.add_widget(
            self.card_receitas
        )

        linha_resumo.add_widget(
            self.card_despesas
        )

        self.container.add_widget(
            linha_resumo
        )

        self.resumo_status = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(96),
            padding=dp(14),
            spacing=dp(8),
            radius=[18, 18, 18, 18],
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        titulo_status = MDLabel(
            text="Situação das despesas",
            bold=True,
            size_hint_y=None,
            height=dp(24),
            theme_text_color="Custom",
            text_color=(0.92, 0.94, 0.98, 1),
        )

        linha_status = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(12),
        )

        self.label_despesas_pagas = MDLabel(
            text="Pagas\nR$ 0,00",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.20, 0.82, 0.55, 1),
        )

        self.label_despesas_pendentes = MDLabel(
            text="Pendentes\nR$ 0,00",
            halign="right",
            bold=True,
            theme_text_color="Custom",
            text_color=(1.00, 0.70, 0.25, 1),
        )

        linha_status.add_widget(
            self.label_despesas_pagas
        )

        linha_status.add_widget(
            self.label_despesas_pendentes
        )

        self.resumo_status.add_widget(
            titulo_status
        )

        self.resumo_status.add_widget(
            linha_status
        )

        self.container.add_widget(
            self.resumo_status
        )

        self.container.add_widget(
            self.criar_area_filtros()
        )

        linha_titulo = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
        )

        titulo_movimentacoes = MDLabel(
            text="Movimentações recentes",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.96, 0.97, 1, 1),
        )

        self.label_quantidade = MDLabel(
            text="0 lançamento(s)",
            halign="right",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.52, 0.59, 0.69, 1),
        )

        linha_titulo.add_widget(
            titulo_movimentacoes
        )

        linha_titulo.add_widget(
            self.label_quantidade
        )

        self.container.add_widget(
            linha_titulo
        )

        ajuda_movimentacoes = MDLabel(
            text="Use o lápis para editar ou o botão PAGAR para concluir uma pendência.",
            font_style="Caption",
            adaptive_height=True,
            theme_text_color="Custom",
            text_color=(0.50, 0.56, 0.66, 1),
        )

        self.container.add_widget(
            ajuda_movimentacoes
        )

        self.lista_movimentacoes = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(12),
        )

        self.container.add_widget(
            self.lista_movimentacoes
        )

        scroll.add_widget(
            self.container
        )

        return scroll

    def criar_area_filtros(self):
        area = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(214),
            padding=dp(14),
            spacing=dp(10),
            radius=[18, 18, 18, 18],
            elevation=1,
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        self.campo_pesquisa = MDTextField(
            hint_text="Pesquisar movimentação",
            helper_text=(
                "Descrição, categoria, valor ou data"
            ),
            helper_text_mode="on_focus",
            icon_left="magnify",
            mode="rectangle",
            size_hint_y=None,
            height=dp(64),
        )

        self.campo_pesquisa.bind(
            text=self.ao_pesquisar
        )

        area.add_widget(
            self.campo_pesquisa
        )

        linha_tipo = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(8),
        )

        self.botao_todos = MDRaisedButton(
            text="TODAS",
            size_hint_x=1 / 3,
        )

        self.botao_receitas = MDRaisedButton(
            text="RECEITAS",
            size_hint_x=1 / 3,
        )

        self.botao_despesas = MDRaisedButton(
            text="DESPESAS",
            size_hint_x=1 / 3,
        )

        self.botao_todos.bind(
            on_release=lambda *_:
            self.selecionar_tipo_filtro("Todos")
        )

        self.botao_receitas.bind(
            on_release=lambda *_:
            self.selecionar_tipo_filtro("Receita")
        )

        self.botao_despesas.bind(
            on_release=lambda *_:
            self.selecionar_tipo_filtro("Despesa")
        )

        linha_tipo.add_widget(
            self.botao_todos
        )
        linha_tipo.add_widget(
            self.botao_receitas
        )
        linha_tipo.add_widget(
            self.botao_despesas
        )

        area.add_widget(
            linha_tipo
        )

        linha_periodo = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(8),
        )

        self.botao_mes = MDFillRoundFlatIconButton(
            text=MESES[self.filtro_mes].upper(),
            icon="calendar-month-outline",
            size_hint_x=0.58,
            md_bg_color=(0.10, 0.14, 0.22, 1),
        )

        self.botao_ano = MDFillRoundFlatIconButton(
            text=str(self.filtro_ano),
            icon="calendar",
            size_hint_x=0.42,
            md_bg_color=(0.10, 0.14, 0.22, 1),
        )

        self.botao_mes.bind(
            on_release=self.abrir_menu_mes
        )

        self.botao_ano.bind(
            on_release=self.abrir_menu_ano
        )

        linha_periodo.add_widget(
            self.botao_mes
        )
        linha_periodo.add_widget(
            self.botao_ano
        )

        area.add_widget(
            linha_periodo
        )

        self.atualizar_botoes_tipo()

        return area

    def on_pre_enter(self, *_):
        configuracoes = (
            db.obter_configuracoes_app()
        )

        nome = configuracoes[
            "nome_usuario"
        ]

        hora = datetime.now().hour

        if hora < 12:
            saudacao = "Bom dia"
        elif hora < 18:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"

        self.label_saudacao.text = (
            f"{saudacao}, {nome}"
        )

        self.carregar_dados()

    def ao_pesquisar(self, *_):
        self.carregar_dados()

    def selecionar_tipo_filtro(self, tipo):
        self.filtro_tipo = tipo
        self.atualizar_botoes_tipo()
        self.carregar_dados()

    def atualizar_botoes_tipo(self):
        cor_inativa = (0.10, 0.14, 0.22, 1)
        texto_inativo = (0.60, 0.66, 0.75, 1)

        botoes = {
            "Todos": self.botao_todos,
            "Receita": self.botao_receitas,
            "Despesa": self.botao_despesas,
        }

        for tipo, botao in botoes.items():
            if tipo == self.filtro_tipo:
                if tipo == "Receita":
                    botao.md_bg_color = (
                        0.05, 0.55, 0.35, 1
                    )
                elif tipo == "Despesa":
                    botao.md_bg_color = (
                        0.76, 0.16, 0.20, 1
                    )
                else:
                    botao.md_bg_color = (
                        0.10, 0.45, 0.95, 1
                    )

                botao.text_color = (
                    1, 1, 1, 1
                )
            else:
                botao.md_bg_color = cor_inativa
                botao.text_color = texto_inativo

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

        if mes is None:
            self.botao_mes.text = (
                "TODOS OS MESES"
            )
        else:
            self.botao_mes.text = (
                MESES[mes].upper()
            )

        if self.menu_mes:
            self.menu_mes.dismiss()
            self.menu_mes = None

        self.carregar_dados()

    def abrir_menu_ano(self, *_):
        anos = db.obter_anos_disponiveis()

        itens = [
            {
                "text": "Todos os anos",
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": (
                    lambda:
                    self.selecionar_ano(None)
                ),
            }
        ]

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

        self.botao_ano.text = (
            str(ano)
            if ano is not None
            else "TODOS"
        )

        if self.menu_ano:
            self.menu_ano.dismiss()
            self.menu_ano = None

        self.carregar_dados()

    def carregar_dados(self):
        pesquisa = ""

        if hasattr(self, "campo_pesquisa"):
            pesquisa = (
                self.campo_pesquisa.text.strip()
            )

        try:
            resumo = db.obter_resumo_filtrado(
                pesquisa=pesquisa,
                tipo=self.filtro_tipo,
                mes=self.filtro_mes,
                ano=self.filtro_ano,
            )

            transacoes = (
                db.obter_transacoes_filtradas(
                    pesquisa=pesquisa,
                    tipo=self.filtro_tipo,
                    mes=self.filtro_mes,
                    ano=self.filtro_ano,
                    limite=200,
                )
            )

            resumo_status = db.obter_resumo_status(
                mes=self.filtro_mes,
                ano=self.filtro_ano,
            )

        except Exception as erro:
            print(
                "Erro ao carregar o dashboard:",
                erro,
            )

            resumo = {
                "saldo": 0,
                "receitas": 0,
                "despesas": 0,
                "quantidade": 0,
            }

            transacoes = []
            resumo_status = {
                "pagas": 0,
                "pendentes": 0,
            }

        self.card_saldo.atualizar_valor(
            formatar_moeda(
                resumo["saldo"]
            ),
            resumo["saldo"],
        )

        self.card_receitas.atualizar_valor(
            formatar_moeda(
                resumo["receitas"]
            )
        )

        self.card_despesas.atualizar_valor(
            formatar_moeda(
                resumo["despesas"]
            )
        )

        self.label_quantidade.text = (
            f"{resumo['quantidade']} "
            "lançamento(s)"
        )

        self.label_despesas_pagas.text = (
            "Pagas\n"
            f"{formatar_moeda(
                resumo_status['pagas']
            )}"
        )

        self.label_despesas_pendentes.text = (
            "Pendentes\n"
            f"{formatar_moeda(
                resumo_status['pendentes']
            )}"
        )

        self.lista_movimentacoes.clear_widgets()

        if not transacoes:
            self.lista_movimentacoes.add_widget(
                MDLabel(
                    text=(
                        "Nenhuma movimentação "
                        "encontrada para os filtros."
                    ),
                    adaptive_height=True,
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(
                        0.55,
                        0.61,
                        0.70,
                        1,
                    ),
                )
            )

            return

        for transacao in transacoes:
            sinal = (
                "+"
                if transacao["tipo"] == "Receita"
                else "-"
            )

            valor = (
                f"{sinal} "
                f"{formatar_moeda(
                    transacao['valor']
                )}"
            )

            self.lista_movimentacoes.add_widget(
                ItemMovimentacao(
                    transacao_id=transacao["id"],
                    descricao=transacao["descricao"],
                    categoria=transacao["categoria"],
                    data=formatar_data(
                        transacao["data"]
                    ),
                    data_banco=transacao["data"],
                    valor=valor,
                    tipo=transacao["tipo"],
                    status=transacao["status"],
                    data_pagamento=(
                        transacao["data_pagamento"]
                    ),
                    tela_dashboard=self,
                )
            )

    def abrir_nova_transacao(self, *_):
        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "transacao",
            "left",
        )

    def abrir_configuracoes(self, *_):
        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "configuracoes",
            "left",
        )

    def abrir_alertas(self, *_):
        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "alertas",
            "left",
        )

    def abrir_categorias(self, *_):
        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "categorias",
            "left",
        )

    def abrir_relatorios(self, *_):
        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "relatorios",
            "left",
        )

    def abrir_edicao_transacao(
        self,
        transacao_id,
    ):
        aplicativo = MDApp.get_running_app()

        tela_edicao = aplicativo.root.get_screen(
            "editar_transacao"
        )

        tela_edicao.carregar_transacao(
            transacao_id
        )

        aplicativo.ir_para_tela(
            "editar_transacao",
            "left",
        )