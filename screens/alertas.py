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
from kivymd.uix.selectioncontrol import MDSwitch

from database.database import db
from notificacoes import (
    solicitar_permissao_notificacoes,
    verificar_e_emitir_alertas,
)


class AlertasScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dias_selecionados = 3

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
            padding=dp(18),
            spacing=dp(14),
        )

        raiz.add_widget(
            self.criar_cabecalho()
        )

        card_ativar = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(92),
            padding=dp(14),
            spacing=dp(12),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        textos = MDBoxLayout(
            orientation="vertical",
        )

        textos.add_widget(
            MDLabel(
                text="Alertas de vencimento",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        textos.add_widget(
            MDLabel(
                text=(
                    "Permitir notificações para "
                    "contas pendentes."
                ),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.55, 0.61, 0.70, 1),
            )
        )

        self.switch_ativo = MDSwitch(
            pos_hint={"center_y": 0.5},
        )

        self.switch_ativo.bind(
            active=self.ao_alterar_switch
        )

        card_ativar.add_widget(textos)
        card_ativar.add_widget(
            self.switch_ativo
        )

        raiz.add_widget(card_ativar)

        raiz.add_widget(
            MDLabel(
                text="Avisar com antecedência",
                adaptive_height=True,
                font_style="H6",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        raiz.add_widget(
            MDLabel(
                text=(
                    "Escolha quantos dias antes do "
                    "vencimento o celular deve avisar."
                ),
                adaptive_height=True,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.55, 0.61, 0.70, 1),
            )
        )

        linha_dias = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8),
        )

        self.botoes_dias = {}

        for dias in (1, 3, 5, 7):
            botao = MDRaisedButton(
                text=f"{dias} DIA"
                if dias == 1
                else f"{dias} DIAS",
                size_hint_x=0.25,
            )

            botao.bind(
                on_release=(
                    lambda _botao, valor=dias:
                    self.selecionar_dias(
                        valor
                    )
                )
            )

            self.botoes_dias[dias] = botao
            linha_dias.add_widget(botao)

        raiz.add_widget(linha_dias)

        card_info = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            padding=dp(14),
            spacing=dp(6),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        card_info.add_widget(
            MDLabel(
                text="Como funcionará",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        card_info.add_widget(
            MDLabel(
                text=(
                    "Somente despesas pendentes serão "
                    "avisadas. O mesmo aviso não será "
                    "repetido mais de uma vez no dia."
                ),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.65, 0.70, 0.78, 1),
            )
        )

        raiz.add_widget(card_info)

        botao_salvar = MDRaisedButton(
            text="SALVAR CONFIGURAÇÃO",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.10, 0.45, 0.95, 1),
        )

        botao_salvar.bind(
            on_release=self.salvar
        )

        botao_teste = MDRaisedButton(
            text="ENVIAR NOTIFICAÇÃO DE TESTE",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.10, 0.14, 0.22, 1),
        )

        botao_teste.bind(
            on_release=self.testar
        )

        raiz.add_widget(botao_salvar)
        raiz.add_widget(botao_teste)
        raiz.add_widget(MDLabel())

        self.add_widget(raiz)

    def criar_cabecalho(self):
        cabecalho = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
        )

        voltar = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(0.95, 0.96, 0.98, 1),
        )

        voltar.bind(
            on_release=self.voltar
        )

        titulo = MDLabel(
            text="Alertas e notificações",
            font_style="H5",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.95, 0.96, 0.98, 1),
        )

        cabecalho.add_widget(voltar)
        cabecalho.add_widget(titulo)

        return cabecalho

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

    def on_pre_enter(self, *_):
        configuracao = (
            db.obter_configuracao_alertas()
        )

        self.switch_ativo.active = (
            configuracao["ativo"]
        )

        self.selecionar_dias(
            configuracao[
                "dias_antecedencia"
            ]
        )

    def ao_alterar_switch(
        self,
        _switch,
        ativo,
    ):
        if ativo:
            solicitar_permissao_notificacoes()

    def selecionar_dias(self, dias):
        self.dias_selecionados = dias

        cor_inativa = (0.10, 0.14, 0.22, 1)
        texto_inativo = (0.60, 0.66, 0.75, 1)

        for valor, botao in (
            self.botoes_dias.items()
        ):
            if valor == dias:
                botao.md_bg_color = (
                    0.10, 0.45, 0.95, 1
                )
                botao.text_color = (
                    1, 1, 1, 1
                )
            else:
                botao.md_bg_color = (
                    cor_inativa
                )
                botao.text_color = (
                    texto_inativo
                )

    def salvar(self, *_):
        try:
            db.salvar_configuracao_alertas(
                ativo=self.switch_ativo.active,
                dias_antecedencia=(
                    self.dias_selecionados
                ),
                horario="08:00",
            )
        except Exception as erro:
            print(
                "Erro ao salvar alertas:",
                erro,
            )
            toast(
                "Não foi possível salvar."
            )
            return

        toast(
            "Configuração de alertas salva."
        )

    def testar(self, *_):
        if not self.switch_ativo.active:
            toast(
                "Ative os alertas primeiro."
            )
            return

        solicitar_permissao_notificacoes()

        quantidade = verificar_e_emitir_alertas(
            forcar_teste=True
        )

        if quantidade:
            toast(
                "Notificação de teste enviada."
            )
        else:
            toast(
                "Não foi possível emitir o teste."
            )

    def voltar(self, *_):
        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "dashboard",
            "right",
        )