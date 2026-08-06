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

    if not texto:
        raise ValueError

    if "," in texto:
        texto = (
            texto
            .replace(".", "")
            .replace(",", ".")
        )

    return float(texto)


def formatar_moeda(valor):
    texto = f"{float(valor):,.2f}"

    texto = (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


class TransacaoScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tipo_selecionado = "Despesa"
        self.forma_pagamento = "À vista"
        self.status_selecionado = "Pago"
        self.categoria_selecionada = ""
        self.menu_categorias = None

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
            MDLabel(
                text="Tipo da transação",
                adaptive_height=True,
                font_style="Subtitle1",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.80, 0.84, 0.90, 1),
            )
        )

        conteudo.add_widget(
            self.criar_seletor_tipo()
        )

        self.area_forma_pagamento = (
            self.criar_forma_pagamento()
        )

        conteudo.add_widget(
            self.area_forma_pagamento
        )

        self.area_status = self.criar_area_status()

        conteudo.add_widget(
            self.area_status
        )

        self.campo_descricao = MDTextField(
            hint_text="Descrição",
            helper_text="Exemplo: Supermercado",
            helper_text_mode="on_focus",
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

        conteudo.add_widget(
            self.campo_descricao
        )

        conteudo.add_widget(
            self.campo_categoria
        )

        self.area_valor_simples = (
            self.criar_area_valor_simples()
        )

        conteudo.add_widget(
            self.area_valor_simples
        )

        self.area_parcelamento = (
            self.criar_area_parcelamento()
        )

        conteudo.add_widget(
            self.area_parcelamento
        )

        self.campo_data = MDTextField(
            hint_text="Data",
            text=datetime.now().strftime(
                "%d/%m/%Y"
            ),
            helper_text=(
                "Data da transação"
            ),
            helper_text_mode="persistent",
            mode="rectangle",
            size_hint_y=None,
            height=dp(72),
        )

        conteudo.add_widget(
            self.campo_data
        )

        botao_salvar = MDRaisedButton(
            text="SALVAR TRANSAÇÃO",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.10, 0.45, 0.95, 1),
        )

        botao_salvar.bind(
            on_release=self.salvar_transacao
        )

        conteudo.add_widget(
            botao_salvar
        )

        scroll.add_widget(
            conteudo
        )

        raiz.add_widget(scroll)
        self.add_widget(raiz)

        self.selecionar_tipo("Despesa")
        self.selecionar_forma_pagamento(
            "À vista"
        )
        self.selecionar_status("Pago")
        self.selecionar_status("Pago")

    def criar_cabecalho(self):
        cabecalho = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=[
                dp(8),
                dp(6),
                dp(16),
                dp(4),
            ],
        )

        botao_voltar = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(0.95, 0.96, 0.98, 1),
        )

        botao_voltar.bind(
            on_release=self.voltar_dashboard
        )

        titulo = MDLabel(
            text="Nova transação",
            font_style="H5",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.95, 0.96, 0.98, 1),
        )

        cabecalho.add_widget(
            botao_voltar
        )

        cabecalho.add_widget(
            titulo
        )

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

        seletor.add_widget(
            self.botao_receita
        )

        seletor.add_widget(
            self.botao_despesa
        )

        return seletor

    def criar_forma_pagamento(self):
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
                text="Forma de pagamento",
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

        self.botao_avista = MDRaisedButton(
            text="À VISTA",
            size_hint=(0.5, None),
            height=dp(48),
        )

        self.botao_parcelada = MDRaisedButton(
            text="PARCELADA",
            size_hint=(0.5, None),
            height=dp(48),
        )

        self.botao_avista.bind(
            on_release=lambda *_:
            self.selecionar_forma_pagamento(
                "À vista"
            )
        )

        self.botao_parcelada.bind(
            on_release=lambda *_:
            self.selecionar_forma_pagamento(
                "Parcelada"
            )
        )

        linha.add_widget(
            self.botao_avista
        )

        linha.add_widget(
            self.botao_parcelada
        )

        card.add_widget(linha)

        return card

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

    def criar_area_valor_simples(self):
        area = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(72),
        )

        self.campo_valor = MDTextField(
            hint_text="Valor",
            helper_text="Exemplo: 250,90",
            helper_text_mode="on_focus",
            mode="rectangle",
            size_hint_y=None,
            height=dp(64),
        )

        area.add_widget(
            self.campo_valor
        )

        return area

    def criar_area_parcelamento(self):
        area = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(430),
            padding=[
                dp(14),
                dp(14),
                dp(14),
                dp(16),
            ],
            spacing=dp(14),
            radius=[14, 14, 14, 14],
            md_bg_color=(0.07, 0.10, 0.17, 1),
        )

        area.add_widget(
            MDLabel(
                text="Dados do parcelamento",
                size_hint_y=None,
                height=dp(28),
                bold=True,
                theme_text_color="Custom",
                text_color=(0.85, 0.88, 0.93, 1),
            )
        )

        self.campo_valor_original = MDTextField(
            hint_text="Valor original da compra",
            helper_text="Valor à vista ou valor bruto",
            helper_text_mode="on_focus",
            mode="rectangle",
            size_hint_y=None,
            height=dp(76),
        )

        self.campo_quantidade_parcelas = MDTextField(
            hint_text="Quantidade de parcelas",
            helper_text="Exemplo: 6",
            helper_text_mode="on_focus",
            mode="rectangle",
            input_filter="int",
            size_hint_y=None,
            height=dp(76),
        )

        self.campo_valor_parcela = MDTextField(
            hint_text="Valor de cada parcela",
            helper_text="Informe o valor com juros, se houver",
            helper_text_mode="on_focus",
            mode="rectangle",
            size_hint_y=None,
            height=dp(76),
        )

        self.campo_valor_original.bind(
            text=self.atualizar_resumo_parcelas
        )

        self.campo_quantidade_parcelas.bind(
            text=self.atualizar_resumo_parcelas
        )

        self.campo_valor_parcela.bind(
            text=self.atualizar_resumo_parcelas
        )

        resumo = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(74),
            padding=[
                dp(10),
                dp(8),
                dp(10),
                dp(8),
            ],
            spacing=dp(4),
            radius=[10, 10, 10, 10],
            elevation=0,
            md_bg_color=(0.055, 0.08, 0.14, 1),
        )

        self.label_total_parcelado = MDLabel(
            text="Total parcelado: R$ 0,00",
            size_hint_y=None,
            height=dp(27),
            bold=True,
            theme_text_color="Custom",
            text_color=(0.22, 0.74, 0.97, 1),
        )

        self.label_acrescimo = MDLabel(
            text="Acréscimo: R$ 0,00",
            size_hint_y=None,
            height=dp(27),
            theme_text_color="Custom",
            text_color=(0.75, 0.80, 0.88, 1),
        )

        resumo.add_widget(
            self.label_total_parcelado
        )

        resumo.add_widget(
            self.label_acrescimo
        )

        area.add_widget(
            self.campo_valor_original
        )

        area.add_widget(
            self.campo_quantidade_parcelas
        )

        area.add_widget(
            self.campo_valor_parcela
        )

        area.add_widget(
            resumo
        )

        return area

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

    def selecionar_tipo(self, tipo):
        self.tipo_selecionado = tipo
        self.categoria_selecionada = ""
        self.campo_categoria.text = ""

        if self.menu_categorias:
            self.menu_categorias.dismiss()
            self.menu_categorias = None

        cor_inativa = (0.10, 0.14, 0.22, 1)
        texto_inativo = (0.55, 0.61, 0.70, 1)

        if tipo == "Receita":
            self.botao_receita.md_bg_color = (
                0.05, 0.55, 0.35, 1
            )
            self.botao_receita.text_color = (
                1, 1, 1, 1
            )

            self.botao_despesa.md_bg_color = (
                cor_inativa
            )
            self.botao_despesa.text_color = (
                texto_inativo
            )

            self.campo_descricao.helper_text = (
                "Exemplo: Salário, PIX, investimento"
            )

            self.area_forma_pagamento.disabled = True
            self.area_forma_pagamento.opacity = 0
            self.area_forma_pagamento.height = 0

            self.area_status.disabled = True
            self.area_status.opacity = 0
            self.area_status.height = 0

            self.selecionar_forma_pagamento(
                "À vista"
            )
            self.selecionar_status("Pago")

        else:
            self.botao_despesa.md_bg_color = (
                0.76, 0.16, 0.20, 1
            )
            self.botao_despesa.text_color = (
                1, 1, 1, 1
            )

            self.botao_receita.md_bg_color = (
                cor_inativa
            )
            self.botao_receita.text_color = (
                texto_inativo
            )

            self.campo_descricao.helper_text = (
                "Exemplo: Supermercado"
            )

            self.area_forma_pagamento.disabled = False
            self.area_forma_pagamento.opacity = 1
            self.area_forma_pagamento.height = dp(104)

            self.area_status.disabled = False
            self.area_status.opacity = 1
            self.area_status.height = dp(104)

    def selecionar_forma_pagamento(
        self,
        forma,
    ):
        self.forma_pagamento = forma

        cor_inativa = (0.10, 0.14, 0.22, 1)
        texto_inativo = (0.55, 0.61, 0.70, 1)

        if forma == "Parcelada":
            self.botao_parcelada.md_bg_color = (
                0.10, 0.45, 0.95, 1
            )
            self.botao_parcelada.text_color = (
                1, 1, 1, 1
            )

            self.botao_avista.md_bg_color = (
                cor_inativa
            )
            self.botao_avista.text_color = (
                texto_inativo
            )

            self.area_parcelamento.disabled = False
            self.area_parcelamento.opacity = 1
            self.area_parcelamento.height = dp(430)

            self.area_valor_simples.disabled = True
            self.area_valor_simples.opacity = 0
            self.area_valor_simples.height = 0

            self.campo_data.hint_text = (
                "Data da primeira parcela"
            )
            self.campo_data.helper_text = (
                "As demais parcelas serão mensais"
            )

        else:
            self.botao_avista.md_bg_color = (
                0.10, 0.45, 0.95, 1
            )
            self.botao_avista.text_color = (
                1, 1, 1, 1
            )

            self.botao_parcelada.md_bg_color = (
                cor_inativa
            )
            self.botao_parcelada.text_color = (
                texto_inativo
            )

            self.area_valor_simples.disabled = False
            self.area_valor_simples.opacity = 1
            self.area_valor_simples.height = dp(72)

            self.area_parcelamento.disabled = True
            self.area_parcelamento.opacity = 0
            self.area_parcelamento.height = 0

            self.campo_data.hint_text = "Data"
            self.campo_data.helper_text = (
                "Data da transação"
            )

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

            self.botao_pendente.md_bg_color = (
                cor_inativa
            )
            self.botao_pendente.text_color = (
                texto_inativo
            )
        else:
            self.botao_pendente.md_bg_color = (
                0.95, 0.55, 0.12, 1
            )
            self.botao_pendente.text_color = (
                1, 1, 1, 1
            )

            self.botao_pago.md_bg_color = (
                cor_inativa
            )
            self.botao_pago.text_color = (
                texto_inativo
            )

    def atualizar_resumo_parcelas(self, *_):
        try:
            valor_original = converter_valor(
                self.campo_valor_original.text
            )

            quantidade = int(
                self.campo_quantidade_parcelas.text
            )

            valor_parcela = converter_valor(
                self.campo_valor_parcela.text
            )

            total = quantidade * valor_parcela
            acrescimo = total - valor_original

            self.label_total_parcelado.text = (
                "Total parcelado: "
                f"{formatar_moeda(total)}"
            )

            if acrescimo >= 0:
                self.label_acrescimo.text = (
                    "Acréscimo: "
                    f"{formatar_moeda(acrescimo)}"
                )
                self.label_acrescimo.text_color = (
                    0.96, 0.55, 0.30, 1
                )
            else:
                self.label_acrescimo.text = (
                    "Desconto: "
                    f"{formatar_moeda(abs(acrescimo))}"
                )
                self.label_acrescimo.text_color = (
                    0.20, 0.82, 0.55, 1
                )

        except (ValueError, TypeError):
            self.label_total_parcelado.text = (
                "Total parcelado: R$ 0,00"
            )
            self.label_acrescimo.text = (
                "Acréscimo: R$ 0,00"
            )
            self.label_acrescimo.text_color = (
                0.75, 0.80, 0.88, 1
            )

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

        if not categorias:
            toast(
                "Nenhuma categoria cadastrada "
                "para este tipo."
            )
            return True

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

    def salvar_transacao(self, *_):
        descricao = (
            self.campo_descricao.text.strip()
        )

        categoria = (
            self.categoria_selecionada.strip()
        )

        data_texto = (
            self.campo_data.text.strip()
        )

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

        if (
            self.tipo_selecionado == "Despesa"
            and self.forma_pagamento == "Parcelada"
        ):
            self.salvar_compra_parcelada(
                descricao=descricao,
                categoria=categoria,
                data_banco=data_banco,
            )
            return

        try:
            valor = converter_valor(
                self.campo_valor.text
            )

            if valor <= 0:
                raise ValueError

        except ValueError:
            toast("Informe um valor válido.")
            return

        try:
            db.adicionar_transacao(
                descricao=descricao,
                valor=valor,
                tipo=self.tipo_selecionado,
                categoria=categoria,
                data=data_banco,
                status=self.status_selecionado,
            )
        except Exception as erro:
            print("Erro ao salvar:", erro)
            toast("Não foi possível salvar.")
            return

        toast(
            f"{self.tipo_selecionado} "
            "salva com sucesso."
        )

        self.limpar_formulario()
        self.voltar_dashboard()

    def salvar_compra_parcelada(
        self,
        descricao,
        categoria,
        data_banco,
    ):
        try:
            valor_original = converter_valor(
                self.campo_valor_original.text
            )

            quantidade = int(
                self.campo_quantidade_parcelas.text
            )

            valor_parcela = converter_valor(
                self.campo_valor_parcela.text
            )

            if (
                valor_original <= 0
                or quantidade < 2
                or valor_parcela <= 0
            ):
                raise ValueError

        except ValueError:
            toast(
                "Confira o valor original, "
                "a quantidade e o valor da parcela."
            )
            return

        try:
            resultado = db.adicionar_compra_parcelada(
                descricao=descricao,
                valor_original=valor_original,
                quantidade_parcelas=quantidade,
                valor_parcela=valor_parcela,
                categoria=categoria,
                data_primeira_parcela=data_banco,
                status=self.status_selecionado,
            )
        except Exception as erro:
            print(
                "Erro ao salvar compra parcelada:",
                erro,
            )
            toast(
                "Não foi possível gerar as parcelas."
            )
            return

        toast(
            f"{quantidade} parcelas geradas. "
            f"Total: {formatar_moeda(
                resultado['total_parcelado']
            )}"
        )

        self.limpar_formulario()
        self.voltar_dashboard()

    def limpar_formulario(self):
        self.campo_descricao.text = ""
        self.campo_valor.text = ""
        self.categoria_selecionada = ""
        self.campo_categoria.text = ""

        self.campo_valor_original.text = ""
        self.campo_quantidade_parcelas.text = ""
        self.campo_valor_parcela.text = ""

        self.campo_data.text = (
            datetime.now().strftime(
                "%d/%m/%Y"
            )
        )

        self.selecionar_tipo("Despesa")
        self.selecionar_forma_pagamento(
            "À vista"
        )

    def voltar_dashboard(self, *_):
        if self.menu_categorias:
            self.menu_categorias.dismiss()
            self.menu_categorias = None

        aplicativo = MDApp.get_running_app()

        aplicativo.ir_para_tela(
            "dashboard",
            "right",
        )