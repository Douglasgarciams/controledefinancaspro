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
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField

from database.database import db


class ItemCategoria(MDCard):

    def __init__(
        self,
        categoria_id,
        nome,
        tipo,
        quantidade_transacoes,
        tela_categorias,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.categoria_id = categoria_id
        self.nome = nome
        self.tipo = tipo
        self.quantidade_transacoes = quantidade_transacoes
        self.tela_categorias = tela_categorias

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(78)
        self.padding = [
            dp(12),
            dp(8),
            dp(8),
            dp(8),
        ]
        self.spacing = dp(8)
        self.radius = [14, 14, 14, 14]
        self.elevation = 1
        self.md_bg_color = (
            0.07,
            0.10,
            0.17,
            1,
        )

        cor = (
            (0.20, 0.82, 0.55, 1)
            if tipo == "Receita"
            else (0.96, 0.35, 0.38, 1)
        )

        icone = (
            "arrow-down-bold-circle-outline"
            if tipo == "Receita"
            else "arrow-up-bold-circle-outline"
        )

        botao_icone = MDIconButton(
            icon=icone,
            theme_icon_color="Custom",
            icon_color=cor,
            disabled=True,
        )

        informacoes = MDBoxLayout(
            orientation="vertical",
        )

        label_nome = MDLabel(
            text=nome,
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.95, 0.96, 0.98, 1),
        )

        label_detalhes = MDLabel(
            text=(
                f"{tipo} • "
                f"{quantidade_transacoes} transação(ões)"
            ),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.55, 0.61, 0.70, 1),
        )

        informacoes.add_widget(label_nome)
        informacoes.add_widget(label_detalhes)

        botao_excluir = MDIconButton(
            icon="trash-can-outline",
            theme_icon_color="Custom",
            icon_color=(0.96, 0.35, 0.38, 1),
        )

        botao_excluir.bind(
            on_release=self.confirmar_exclusao
        )

        self.add_widget(botao_icone)
        self.add_widget(informacoes)
        self.add_widget(botao_excluir)

    def confirmar_exclusao(self, *_):
        self.tela_categorias.confirmar_exclusao(
            categoria_id=self.categoria_id,
            nome=self.nome,
            quantidade=self.quantidade_transacoes,
        )


class CategoriasScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tipo_selecionado = "Despesa"
        self.dialogo = None

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
            spacing=dp(12),
        )

        raiz.add_widget(
            self.criar_cabecalho()
        )

        raiz.add_widget(
            MDLabel(
                text="Nova categoria",
                adaptive_height=True,
                font_style="H6",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        raiz.add_widget(
            self.criar_seletor_tipo()
        )

        self.campo_nome = MDTextField(
            hint_text="Nome da categoria",
            helper_text="Exemplo: Educação",
            helper_text_mode="on_focus",
            mode="rectangle",
        )

        raiz.add_widget(self.campo_nome)

        botao_adicionar = MDRaisedButton(
            text="ADICIONAR CATEGORIA",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.10, 0.45, 0.95, 1),
        )

        botao_adicionar.bind(
            on_release=self.adicionar_categoria
        )

        raiz.add_widget(botao_adicionar)

        raiz.add_widget(
            MDLabel(
                text="Categorias cadastradas",
                adaptive_height=True,
                font_style="H6",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        scroll = MDScrollView(
            do_scroll_x=False,
        )

        self.lista_categorias = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(10),
            padding=[
                0,
                0,
                0,
                dp(30),
            ],
        )

        scroll.add_widget(
            self.lista_categorias
        )

        raiz.add_widget(scroll)

        self.add_widget(raiz)

        self.selecionar_tipo("Despesa")

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

    def criar_cabecalho(self):
        cabecalho = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
        )

        botao_voltar = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(0.95, 0.96, 0.98, 1),
        )

        botao_voltar.bind(
            on_release=self.voltar
        )

        titulo = MDLabel(
            text="Categorias",
            font_style="H5",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.95, 0.96, 0.98, 1),
        )

        cabecalho.add_widget(botao_voltar)
        cabecalho.add_widget(titulo)

        return cabecalho

    def criar_seletor_tipo(self):
        seletor = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            spacing=dp(10),
        )

        self.botao_receita = MDRaisedButton(
            text="RECEITA",
            size_hint_x=0.5,
            height=dp(48),
        )

        self.botao_despesa = MDRaisedButton(
            text="DESPESA",
            size_hint_x=0.5,
            height=dp(48),
        )

        self.botao_receita.bind(
            on_release=lambda *_: self.selecionar_tipo(
                "Receita"
            )
        )

        self.botao_despesa.bind(
            on_release=lambda *_: self.selecionar_tipo(
                "Despesa"
            )
        )

        seletor.add_widget(self.botao_receita)
        seletor.add_widget(self.botao_despesa)

        return seletor

    def selecionar_tipo(self, tipo):
        self.tipo_selecionado = tipo

        cor_inativa = (
            0.10,
            0.14,
            0.22,
            1,
        )

        texto_inativo = (
            0.55,
            0.61,
            0.70,
            1,
        )

        if tipo == "Receita":
            self.botao_receita.md_bg_color = (
                0.05,
                0.55,
                0.35,
                1,
            )

            self.botao_receita.text_color = (
                1,
                1,
                1,
                1,
            )

            self.botao_despesa.md_bg_color = cor_inativa
            self.botao_despesa.text_color = texto_inativo

        else:
            self.botao_despesa.md_bg_color = (
                0.76,
                0.16,
                0.20,
                1,
            )

            self.botao_despesa.text_color = (
                1,
                1,
                1,
                1,
            )

            self.botao_receita.md_bg_color = cor_inativa
            self.botao_receita.text_color = texto_inativo

    def on_pre_enter(self, *_):
        self.carregar_categorias()

    def carregar_categorias(self):
        self.lista_categorias.clear_widgets()

        categorias = db.obter_todas_categorias()

        for categoria in categorias:
            self.lista_categorias.add_widget(
                ItemCategoria(
                    categoria_id=categoria["id"],
                    nome=categoria["nome"],
                    tipo=categoria["tipo"],
                    quantidade_transacoes=(
                        categoria["quantidade_transacoes"]
                    ),
                    tela_categorias=self,
                )
            )

    def adicionar_categoria(self, *_):
        nome = self.campo_nome.text.strip()

        if not nome:
            toast("Digite o nome da categoria.")
            return

        try:
            db.adicionar_categoria(
                nome=nome,
                tipo=self.tipo_selecionado,
            )

        except ValueError as erro:
            toast(str(erro))
            return

        except Exception as erro:
            print("Erro ao adicionar categoria:", erro)
            toast("Não foi possível cadastrar.")
            return

        self.campo_nome.text = ""

        toast("Categoria adicionada.")

        self.carregar_categorias()

    def confirmar_exclusao(
        self,
        categoria_id,
        nome,
        quantidade,
    ):
        if quantidade > 0:
            toast(
                "A categoria possui transações e não pode ser excluída."
            )
            return

        self.dialogo = MDDialog(
            title="Excluir categoria",
            text=(
                f"Deseja excluir a categoria "
                f"'{nome}'?"
            ),
            buttons=[
                MDRaisedButton(
                    text="CANCELAR",
                    md_bg_color=(
                        0.20,
                        0.23,
                        0.30,
                        1,
                    ),
                    on_release=lambda *_: (
                        self.fechar_dialogo()
                    ),
                ),
                MDRaisedButton(
                    text="EXCLUIR",
                    md_bg_color=(
                        0.76,
                        0.16,
                        0.20,
                        1,
                    ),
                    on_release=lambda *_: (
                        self.excluir_categoria(
                            categoria_id
                        )
                    ),
                ),
            ],
        )

        self.dialogo.open()

    def fechar_dialogo(self):
        if self.dialogo:
            self.dialogo.dismiss()
            self.dialogo = None

    def excluir_categoria(self, categoria_id):
        try:
            db.excluir_categoria(categoria_id)

        except ValueError as erro:
            toast(str(erro))
            self.fechar_dialogo()
            return

        except Exception as erro:
            print("Erro ao excluir categoria:", erro)
            toast("Não foi possível excluir.")
            self.fechar_dialogo()
            return

        self.fechar_dialogo()
        self.carregar_categorias()

        toast("Categoria excluída.")

    def voltar(self, *_):
        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "dashboard",
            "right",
        )