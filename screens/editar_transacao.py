from datetime import datetime

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
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField

from database.database import db


def converter_valor(texto):
    texto = (
        texto.strip()
        .replace("R$", "")
        .replace(" ", "")
    )

    if "," in texto:
        texto = (
            texto
            .replace(".", "")
            .replace(",", ".")
        )

    return float(texto)


class EditarTransacaoScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.transacao_id = None
        self.tipo_selecionado = "Despesa"
        self.status_selecionado = "Pago"
        self.categoria_selecionada = ""
        self.menu_categorias = None
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
        )

        raiz.add_widget(
            self.criar_cabecalho()
        )

        scroll = MDScrollView(
            do_scroll_x=False,
        )

        conteudo = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[
                dp(18),
                dp(8),
                dp(18),
                dp(40),
            ],
            spacing=dp(14),
        )

        conteudo.add_widget(
            self.criar_seletor_tipo()
        )

        self.area_status = (
            self.criar_area_status()
        )

        conteudo.add_widget(
            self.area_status
        )

        self.campo_descricao = MDTextField(
            hint_text="Descrição",
            mode="rectangle",
            size_hint_y=None,
            height=dp(64),
        )

        self.campo_valor = MDTextField(
            hint_text="Valor",
            mode="rectangle",
            size_hint_y=None,
            height=dp(64),
        )

        self.campo_categoria = MDTextField(
            hint_text="Categoria",
            helper_text="Toque para selecionar",
            helper_text_mode="persistent",
            mode="rectangle",
            readonly=True,
            icon_right="menu-down",
            size_hint_y=None,
            height=dp(72),
        )

        self.campo_categoria.bind(
            on_touch_down=self.abrir_menu_categoria
        )

        self.campo_data = MDTextField(
            hint_text="Data",
            mode="rectangle",
            size_hint_y=None,
            height=dp(64),
        )

        conteudo.add_widget(
            self.campo_descricao
        )
        conteudo.add_widget(
            self.campo_valor
        )
        conteudo.add_widget(
            self.campo_categoria
        )
        conteudo.add_widget(
            self.campo_data
        )

        botao_salvar = MDRaisedButton(
            text="SALVAR ALTERAÇÕES",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.10, 0.45, 0.95, 1),
        )

        botao_salvar.bind(
            on_release=self.salvar_alteracoes
        )

        botao_excluir = MDRaisedButton(
            text="EXCLUIR TRANSAÇÃO",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.76, 0.16, 0.20, 1),
        )

        botao_excluir.bind(
            on_release=self.confirmar_exclusao
        )

        conteudo.add_widget(botao_salvar)
        conteudo.add_widget(botao_excluir)

        scroll.add_widget(conteudo)
        raiz.add_widget(scroll)
        self.add_widget(raiz)

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

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
            on_release=self.voltar_dashboard
        )

        titulo = MDLabel(
            text="Editar transação",
            font_style="H5",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.95, 0.96, 0.98, 1),
        )

        cabecalho.add_widget(voltar)
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
            size_hint=(0.5, None),
            height=dp(48),
        )

        self.botao_despesa = MDRaisedButton(
            text="DESPESA",
            size_hint=(0.5, None),
            height=dp(48),
        )

        self.botao_receita.bind(
            on_release=lambda *_:
            self.selecionar_tipo("Receita")
        )

        self.botao_despesa.bind(
            on_release=lambda *_:
            self.selecionar_tipo("Despesa")
        )

        seletor.add_widget(self.botao_receita)
        seletor.add_widget(self.botao_despesa)
        return seletor

    def criar_area_status(self):
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(104),
            padding=dp(12),
            spacing=dp(8),
            radius=[14, 14, 14, 14],
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        card.add_widget(
            MDLabel(
                text="Status da despesa",
                size_hint_y=None,
                height=dp(24),
                bold=True,
                theme_text_color="Custom",
                text_color=(0.85, 0.88, 0.93, 1),
            )
        )

        linha = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(10),
        )

        self.botao_pago = MDRaisedButton(
            text="PAGO",
            size_hint=(0.5, None),
            height=dp(48),
        )

        self.botao_pendente = MDRaisedButton(
            text="PENDENTE",
            size_hint=(0.5, None),
            height=dp(48),
        )

        self.botao_pago.bind(
            on_release=lambda *_:
            self.selecionar_status("Pago")
        )

        self.botao_pendente.bind(
            on_release=lambda *_:
            self.selecionar_status("Pendente")
        )

        linha.add_widget(self.botao_pago)
        linha.add_widget(self.botao_pendente)
        card.add_widget(linha)
        return card

    def carregar_transacao(self, transacao_id):
        transacao = db.obter_transacao_por_id(
            transacao_id
        )

        if not transacao:
            toast("Transação não encontrada.")
            return

        self.transacao_id = transacao["id"]
        self.tipo_selecionado = transacao["tipo"]
        self.status_selecionado = (
            transacao.get("status")
            or "Pago"
        )
        self.categoria_selecionada = (
            transacao["categoria"] or ""
        )

        self.campo_descricao.text = (
            transacao["descricao"]
        )

        self.campo_valor.text = (
            f"{float(transacao['valor']):.2f}"
            .replace(".", ",")
        )

        self.campo_categoria.text = (
            self.categoria_selecionada
        )

        self.campo_data.text = datetime.strptime(
            transacao["data"],
            "%Y-%m-%d",
        ).strftime("%d/%m/%Y")

        self.atualizar_botoes_tipo()
        self.selecionar_status(
            self.status_selecionado
        )

    def selecionar_tipo(self, tipo):
        if self.tipo_selecionado != tipo:
            self.categoria_selecionada = ""
            self.campo_categoria.text = ""

        self.tipo_selecionado = tipo
        self.atualizar_botoes_tipo()

        if tipo == "Receita":
            self.area_status.disabled = True
            self.area_status.opacity = 0
            self.area_status.height = 0
            self.selecionar_status("Pago")
        else:
            self.area_status.disabled = False
            self.area_status.opacity = 1
            self.area_status.height = dp(104)

    def atualizar_botoes_tipo(self):
        cor_inativa = (0.10, 0.14, 0.22, 1)
        texto_inativo = (0.55, 0.61, 0.70, 1)

        if self.tipo_selecionado == "Receita":
            self.botao_receita.md_bg_color = (
                0.05, 0.55, 0.35, 1
            )
            self.botao_receita.text_color = (
                1, 1, 1, 1
            )
            self.botao_despesa.md_bg_color = cor_inativa
            self.botao_despesa.text_color = texto_inativo
        else:
            self.botao_despesa.md_bg_color = (
                0.76, 0.16, 0.20, 1
            )
            self.botao_despesa.text_color = (
                1, 1, 1, 1
            )
            self.botao_receita.md_bg_color = cor_inativa
            self.botao_receita.text_color = texto_inativo

        self.selecionar_tipo(
            self.tipo_selecionado
        ) if False else None

        if self.tipo_selecionado == "Receita":
            self.area_status.disabled = True
            self.area_status.opacity = 0
            self.area_status.height = 0
        else:
            self.area_status.disabled = False
            self.area_status.opacity = 1
            self.area_status.height = dp(104)

    def selecionar_status(self, status):
        self.status_selecionado = status

        cor_inativa = (0.10, 0.14, 0.22, 1)
        texto_inativo = (0.55, 0.61, 0.70, 1)

        if status == "Pago":
            self.botao_pago.md_bg_color = (
                0.05, 0.55, 0.35, 1
            )
            self.botao_pago.text_color = (
                1, 1, 1, 1
            )
            self.botao_pendente.md_bg_color = cor_inativa
            self.botao_pendente.text_color = texto_inativo
        else:
            self.botao_pendente.md_bg_color = (
                0.95, 0.55, 0.12, 1
            )
            self.botao_pendente.text_color = (
                1, 1, 1, 1
            )
            self.botao_pago.md_bg_color = cor_inativa
            self.botao_pago.text_color = texto_inativo

    def abrir_menu_categoria(
        self,
        campo,
        toque,
    ):
        if not campo.collide_point(*toque.pos):
            return False

        categorias = db.obter_categorias(
            self.tipo_selecionado
        )

        itens = []

        for categoria in categorias:
            nome = categoria["nome"]

            itens.append(
                {
                    "text": nome,
                    "viewclass": "OneLineListItem",
                    "height": dp(48),
                    "on_release": (
                        lambda nome_categoria=nome:
                        self.selecionar_categoria(
                            nome_categoria
                        )
                    ),
                }
            )

        if self.menu_categorias:
            self.menu_categorias.dismiss()

        self.menu_categorias = MDDropdownMenu(
            caller=self.campo_categoria,
            items=itens,
            width_mult=4,
        )

        self.menu_categorias.open()
        return True

    def selecionar_categoria(
        self,
        nome_categoria,
    ):
        self.categoria_selecionada = nome_categoria
        self.campo_categoria.text = nome_categoria

        if self.menu_categorias:
            self.menu_categorias.dismiss()
            self.menu_categorias = None

    def salvar_alteracoes(self, *_):
        if self.transacao_id is None:
            toast("Nenhuma transação selecionada.")
            return

        descricao = self.campo_descricao.text.strip()
        categoria = self.categoria_selecionada.strip()
        data_texto = self.campo_data.text.strip()

        try:
            valor = converter_valor(
                self.campo_valor.text
            )
            if valor <= 0:
                raise ValueError
        except ValueError:
            toast("Informe um valor válido.")
            return

        if not descricao:
            toast("Informe a descrição.")
            return

        if not categoria:
            toast("Selecione uma categoria.")
            return

        try:
            data_banco = datetime.strptime(
                data_texto,
                "%d/%m/%Y",
            ).strftime("%Y-%m-%d")
        except ValueError:
            toast(
                "Use a data no formato DD/MM/AAAA."
            )
            return

        try:
            db.atualizar_transacao(
                transacao_id=self.transacao_id,
                descricao=descricao,
                valor=valor,
                tipo=self.tipo_selecionado,
                categoria=categoria,
                data=data_banco,
                status=self.status_selecionado,
            )
        except Exception as erro:
            print("Erro ao atualizar:", erro)
            toast("Não foi possível atualizar.")
            return

        toast("Transação atualizada.")
        self.voltar_dashboard()

    def confirmar_exclusao(self, *_):
        self.dialogo = MDDialog(
            title="Excluir transação",
            text=(
                "Deseja realmente excluir esta transação?"
            ),
            buttons=[
                MDRaisedButton(
                    text="CANCELAR",
                    on_release=lambda *_:
                    self.fechar_dialogo(),
                ),
                MDRaisedButton(
                    text="EXCLUIR",
                    md_bg_color=(0.76, 0.16, 0.20, 1),
                    on_release=lambda *_:
                    self.excluir_transacao(),
                ),
            ],
        )

        self.dialogo.open()

    def excluir_transacao(self):
        if self.transacao_id is None:
            return

        try:
            db.excluir_transacao(
                self.transacao_id
            )
        except Exception as erro:
            print("Erro ao excluir:", erro)
            toast("Não foi possível excluir.")
            self.fechar_dialogo()
            return

        self.fechar_dialogo()
        toast("Transação excluída.")
        self.voltar_dashboard()

    def fechar_dialogo(self):
        if self.dialogo:
            self.dialogo.dismiss()
            self.dialogo = None

    def voltar_dashboard(self, *_):
        if self.menu_categorias:
            self.menu_categorias.dismiss()
            self.menu_categorias = None

        aplicativo = MDApp.get_running_app()
        aplicativo.ir_para_tela(
            "dashboard",
            "right",
        )