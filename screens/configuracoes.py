from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import (
    MDIconButton,
    MDRaisedButton,
)
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField

from database.database import db


class ItemConfiguracao(MDCard):

    def __init__(
        self,
        titulo,
        subtitulo,
        icone,
        cor_icone,
        ao_clicar=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(82)
        self.padding = [
            dp(10),
            dp(8),
            dp(8),
            dp(8),
        ]
        self.spacing = dp(8)
        self.radius = [16, 16, 16, 16]
        self.elevation = 1
        self.md_bg_color = (0.07, 0.10, 0.17, 1)

        icone_widget = MDIconButton(
            icon=icone,
            disabled=True,
            theme_icon_color="Custom",
            icon_color=cor_icone,
        )

        textos = MDBoxLayout(
            orientation="vertical",
        )

        textos.add_widget(
            MDLabel(
                text=titulo,
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        textos.add_widget(
            MDLabel(
                text=subtitulo,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.52, 0.59, 0.69, 1),
            )
        )

        seta = MDIconButton(
            icon="chevron-right",
            theme_icon_color="Custom",
            icon_color=(0.48, 0.55, 0.65, 1),
        )

        if ao_clicar:
            self.bind(
                on_release=ao_clicar
            )
            seta.bind(
                on_release=ao_clicar
            )
        else:
            seta.disabled = True

        self.add_widget(icone_widget)
        self.add_widget(textos)
        self.add_widget(seta)


class ConfiguracoesScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tema_selecionado = "Dark"

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
            spacing=dp(14),
        )

        self.conteudo.add_widget(
            self.criar_perfil()
        )

        self.conteudo.add_widget(
            self.criar_titulo_secao(
                "PREFERÊNCIAS"
            )
        )

        self.conteudo.add_widget(
            self.criar_aparencia()
        )

        self.conteudo.add_widget(
            ItemConfiguracao(
                titulo="Alertas e notificações",
                subtitulo=(
                    "Defina quando receber avisos "
                    "de vencimento"
                ),
                icone="bell-outline",
                cor_icone=(1.00, 0.70, 0.25, 1),
                ao_clicar=self.abrir_alertas,
            )
        )

        self.conteudo.add_widget(
            ItemConfiguracao(
                titulo="Categorias",
                subtitulo=(
                    "Organize receitas e despesas"
                ),
                icone="tag-multiple-outline",
                cor_icone=(0.34, 0.76, 1, 1),
                ao_clicar=self.abrir_categorias,
            )
        )

        self.conteudo.add_widget(
            ItemConfiguracao(
                titulo="Relatórios",
                subtitulo=(
                    "Acompanhe sua evolução financeira"
                ),
                icone="chart-box-outline",
                cor_icone=(0.28, 0.82, 0.62, 1),
                ao_clicar=self.abrir_relatorios,
            )
        )

        self.conteudo.add_widget(
            self.criar_titulo_secao(
                "DADOS E SEGURANÇA"
            )
        )

        self.conteudo.add_widget(
            ItemConfiguracao(
                titulo="Backup e restauração",
                subtitulo=(
                    "Proteja os dados do aplicativo"
                ),
                icone="cloud-upload-outline",
                cor_icone=(0.58, 0.66, 1, 1),
                ao_clicar=self.abrir_backup,
            )
        )

        self.conteudo.add_widget(
            self.criar_titulo_secao(
                "SOBRE"
            )
        )

        self.conteudo.add_widget(
            self.criar_sobre()
        )

        botao_salvar = MDRaisedButton(
            text="SALVAR CONFIGURAÇÕES",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.10, 0.45, 0.95, 1),
        )

        botao_salvar.bind(
            on_release=self.salvar
        )

        self.conteudo.add_widget(
            botao_salvar
        )

        scroll.add_widget(
            self.conteudo
        )

        raiz.add_widget(scroll)
        self.add_widget(raiz)

    def criar_cabecalho(self):
        cabecalho = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(72),
            padding=[
                dp(8),
                dp(6),
                dp(16),
                dp(4),
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
                text="Configurações",
                font_style="H5",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.97, 0.98, 1, 1),
            )
        )

        textos.add_widget(
            MDLabel(
                text="Personalize sua experiência",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.52, 0.59, 0.69, 1),
            )
        )

        cabecalho.add_widget(voltar)
        cabecalho.add_widget(textos)

        return cabecalho

    def criar_titulo_secao(self, texto):
        return MDLabel(
            text=texto,
            font_style="Caption",
            bold=True,
            adaptive_height=True,
            theme_text_color="Custom",
            text_color=(0.42, 0.68, 0.96, 1),
        )

    def criar_perfil(self):
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=dp(16),
            spacing=dp(8),
            radius=[20, 20, 20, 20],
            elevation=2,
            md_bg_color=(0.055, 0.20, 0.40, 1),
        )

        linha = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
        )

        linha.add_widget(
            MDIconButton(
                icon="account-circle-outline",
                disabled=True,
                theme_icon_color="Custom",
                icon_color=(0.84, 0.91, 1, 1),
            )
        )

        linha.add_widget(
            MDLabel(
                text="Seu perfil",
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            )
        )

        self.campo_nome = MDTextField(
            hint_text="Como deseja ser chamado?",
            helper_text=(
                "Esse nome aparecerá no Dashboard"
            ),
            helper_text_mode="persistent",
            mode="rectangle",
            size_hint_y=None,
            height=dp(72),
        )

        card.add_widget(linha)
        card.add_widget(self.campo_nome)

        return card

    def criar_aparencia(self):
        card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(92),
            padding=dp(12),
            spacing=dp(10),
            radius=[16, 16, 16, 16],
            elevation=1,
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        card.add_widget(
            MDIconButton(
                icon="theme-light-dark",
                disabled=True,
                theme_icon_color="Custom",
                icon_color=(0.72, 0.60, 1, 1),
            )
        )

        textos = MDBoxLayout(
            orientation="vertical",
        )

        textos.add_widget(
            MDLabel(
                text="Tema escuro",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        textos.add_widget(
            MDLabel(
                text=(
                    "Desative para usar o tema claro"
                ),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.52, 0.59, 0.69, 1),
            )
        )

        self.switch_tema = MDSwitch(
            pos_hint={"center_y": 0.5},
        )

        self.switch_tema.bind(
            active=self.ao_alterar_tema
        )

        card.add_widget(textos)
        card.add_widget(self.switch_tema)

        return card

    def criar_sobre(self):
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(112),
            padding=dp(14),
            spacing=dp(4),
            radius=[16, 16, 16, 16],
            elevation=1,
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        card.add_widget(
            MDLabel(
                text="Finanças Pro",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        card.add_widget(
            MDLabel(
                text="Versão de desenvolvimento 0.9",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.52, 0.59, 0.69, 1),
            )
        )

        card.add_widget(
            MDLabel(
                text=(
                    "Controle inteligente das suas "
                    "finanças pessoais."
                ),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.66, 0.72, 0.82, 1),
            )
        )

        return card

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

    def on_pre_enter(self, *_):
        configuracoes = (
            db.obter_configuracoes_app()
        )

        self.campo_nome.text = (
            configuracoes["nome_usuario"]
        )

        self.tema_selecionado = (
            configuracoes["tema"]
        )

        self.switch_tema.active = (
            self.tema_selecionado == "Dark"
        )

    def ao_alterar_tema(
        self,
        _switch,
        ativo,
    ):
        self.tema_selecionado = (
            "Dark"
            if ativo
            else "Light"
        )

        aplicativo = MDApp.get_running_app()
        aplicativo.theme_cls.theme_style = (
            self.tema_selecionado
        )

    def salvar(self, *_):
        try:
            db.salvar_configuracoes_app(
                nome_usuario=(
                    self.campo_nome.text
                ),
                tema=self.tema_selecionado,
                moeda="R$",
            )
        except Exception as erro:
            print(
                "Erro ao salvar configurações:",
                erro,
            )
            toast(
                "Não foi possível salvar."
            )
            return

        toast(
            "Configurações salvas."
        )

    def abrir_alertas(self, *_):
        MDApp.get_running_app().ir_para_tela(
            "alertas",
            "left",
        )

    def abrir_categorias(self, *_):
        MDApp.get_running_app().ir_para_tela(
            "categorias",
            "left",
        )

    def abrir_relatorios(self, *_):
        MDApp.get_running_app().ir_para_tela(
            "relatorios",
            "left",
        )

    def abrir_backup(self, *_):
        MDApp.get_running_app().ir_para_tela(
            "backup",
            "left",
        )

    def voltar_dashboard(self, *_):
        MDApp.get_running_app().ir_para_tela(
            "dashboard",
            "right",
        )