from pathlib import Path

from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import (
    MDFlatButton,
    MDIconButton,
    MDRaisedButton,
)
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from services.backup_service import (
    BackupError,
    criar_backup,
    excluir_backup,
    listar_backups,
    obter_pasta_backups,
    restaurar_backup,
)


def formatar_tamanho(tamanho):
    tamanho = float(tamanho)

    if tamanho < 1024:
        return f"{int(tamanho)} bytes"

    if tamanho < 1024 * 1024:
        return f"{tamanho / 1024:.1f} KB"

    return (
        f"{tamanho / (1024 * 1024):.1f} MB"
    )


class ItemBackup(MDCard):

    def __init__(
        self,
        backup,
        tela,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.backup = backup
        self.tela = tela

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(96)
        self.padding = dp(10)
        self.spacing = dp(8)
        self.radius = [16, 16, 16, 16]
        self.elevation = 1
        self.md_bg_color = (0.07, 0.10, 0.17, 1)

        self.add_widget(
            MDIconButton(
                icon="database-check-outline",
                disabled=True,
                theme_icon_color="Custom",
                icon_color=(0.30, 0.78, 0.96, 1),
            )
        )

        textos = MDBoxLayout(
            orientation="vertical",
        )

        textos.add_widget(
            MDLabel(
                text=backup["nome"],
                bold=True,
                shorten=True,
                shorten_from="right",
                theme_text_color="Custom",
                text_color=(0.95, 0.96, 0.98, 1),
            )
        )

        textos.add_widget(
            MDLabel(
                text=(
                    backup["data"].strftime(
                        "%d/%m/%Y às %H:%M"
                    )
                    + " • "
                    + formatar_tamanho(
                        backup["tamanho"]
                    )
                ),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.52, 0.59, 0.69, 1),
            )
        )

        acoes = MDBoxLayout(
            orientation="horizontal",
            adaptive_width=True,
        )

        restaurar = MDFlatButton(
            text="RESTAURAR",
            theme_text_color="Custom",
            text_color=(0.20, 0.82, 0.55, 1),
        )

        restaurar.bind(
            on_release=lambda *_:
            tela.confirmar_restauracao(
                backup
            )
        )

        excluir = MDIconButton(
            icon="delete-outline",
            theme_icon_color="Custom",
            icon_color=(0.96, 0.35, 0.38, 1),
        )

        excluir.bind(
            on_release=lambda *_:
            tela.confirmar_exclusao(
                backup
            )
        )

        acoes.add_widget(restaurar)
        acoes.add_widget(excluir)

        self.add_widget(textos)
        self.add_widget(acoes)


class BackupScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
                dp(16),
                dp(8),
                dp(16),
                dp(40),
            ],
            spacing=dp(14),
        )

        card_principal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(184),
            padding=dp(16),
            spacing=dp(10),
            radius=[20, 20, 20, 20],
            elevation=2,
            md_bg_color=(0.055, 0.20, 0.40, 1),
        )

        card_principal.add_widget(
            MDLabel(
                text="Proteja seus dados",
                font_style="H5",
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            )
        )

        card_principal.add_widget(
            MDLabel(
                text=(
                    "Crie uma cópia do banco com "
                    "transações, parcelas, categorias "
                    "e configurações."
                ),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.78, 0.86, 0.96, 1),
            )
        )

        botao_criar = MDRaisedButton(
            text="CRIAR BACKUP AGORA",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.10, 0.45, 0.95, 1),
        )

        botao_criar.bind(
            on_release=self.criar_novo_backup
        )

        card_principal.add_widget(
            botao_criar
        )

        conteudo.add_widget(
            card_principal
        )

        pasta = obter_pasta_backups()

        conteudo.add_widget(
            MDLabel(
                text="LOCAL DOS BACKUPS",
                font_style="Caption",
                bold=True,
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=(0.42, 0.68, 0.96, 1),
            )
        )

        conteudo.add_widget(
            MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(74),
                padding=dp(10),
                radius=[16, 16, 16, 16],
                md_bg_color=(0.07, 0.10, 0.17, 1),
            )
        )

        card_local = conteudo.children[0]

        card_local.add_widget(
            MDIconButton(
                icon="folder-outline",
                disabled=True,
                theme_icon_color="Custom",
                icon_color=(1.00, 0.70, 0.25, 1),
            )
        )

        card_local.add_widget(
            MDLabel(
                text=str(pasta),
                shorten=True,
                shorten_from="center",
                theme_text_color="Custom",
                text_color=(0.72, 0.77, 0.85, 1),
            )
        )

        conteudo.add_widget(
            MDLabel(
                text="BACKUPS DISPONÍVEIS",
                font_style="Caption",
                bold=True,
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=(0.42, 0.68, 0.96, 1),
            )
        )

        self.lista_backups = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(10),
        )

        conteudo.add_widget(
            self.lista_backups
        )

        scroll.add_widget(conteudo)
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
            on_release=self.voltar
        )

        textos = MDBoxLayout(
            orientation="vertical",
        )

        textos.add_widget(
            MDLabel(
                text="Backup e restauração",
                font_style="H5",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.97, 0.98, 1, 1),
            )
        )

        textos.add_widget(
            MDLabel(
                text="Cópias locais do banco de dados",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.52, 0.59, 0.69, 1),
            )
        )

        cabecalho.add_widget(voltar)
        cabecalho.add_widget(textos)

        return cabecalho

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

    def on_pre_enter(self, *_):
        self.carregar_backups()

    def carregar_backups(self):
        self.lista_backups.clear_widgets()

        backups = listar_backups()

        if not backups:
            vazio = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(104),
                padding=dp(14),
                radius=[16, 16, 16, 16],
                md_bg_color=(0.07, 0.10, 0.17, 1),
            )

            vazio.add_widget(
                MDLabel(
                    text=(
                        "Nenhum backup criado ainda."
                    ),
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.52, 0.59, 0.69, 1),
                )
            )

            self.lista_backups.add_widget(
                vazio
            )
            return

        for backup in backups:
            self.lista_backups.add_widget(
                ItemBackup(
                    backup=backup,
                    tela=self,
                )
            )

    def criar_novo_backup(self, *_):
        try:
            caminho = criar_backup()
        except Exception as erro:
            print(
                "Erro ao criar backup:",
                erro,
            )
            toast(
                "Não foi possível criar o backup."
            )
            return

        toast(
            f"Backup criado: {caminho.name}"
        )

        self.carregar_backups()

    def confirmar_restauracao(
        self,
        backup,
    ):
        self.fechar_dialogo()

        self.dialogo = MDDialog(
            title="Restaurar backup",
            text=(
                "O banco atual será substituído. "
                "Antes disso, o aplicativo criará "
                "automaticamente uma cópia de segurança."
            ),
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda *_:
                    self.fechar_dialogo(),
                ),
                MDRaisedButton(
                    text="RESTAURAR",
                    md_bg_color=(0.10, 0.45, 0.95, 1),
                    on_release=lambda *_:
                    self.executar_restauracao(
                        backup
                    ),
                ),
            ],
        )

        self.dialogo.open()

    def executar_restauracao(
        self,
        backup,
    ):
        self.fechar_dialogo()

        try:
            resultado = restaurar_backup(
                backup["caminho"]
            )
        except BackupError as erro:
            print(
                "Erro controlado ao restaurar:",
                erro,
            )
            toast(str(erro))
            return
        except Exception as erro:
            print(
                "Erro ao restaurar:",
                erro,
            )
            toast(
                "Não foi possível restaurar."
            )
            return

        toast(
            "Backup restaurado com sucesso."
        )

        self.carregar_backups()

        app = MDApp.get_running_app()

        if app.root.has_screen(
            "dashboard"
        ):
            app.root.get_screen(
                "dashboard"
            ).carregar_dados()

    def confirmar_exclusao(
        self,
        backup,
    ):
        self.fechar_dialogo()

        self.dialogo = MDDialog(
            title="Excluir backup",
            text=(
                f"Deseja excluir {backup['nome']}?"
            ),
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda *_:
                    self.fechar_dialogo(),
                ),
                MDRaisedButton(
                    text="EXCLUIR",
                    md_bg_color=(0.76, 0.16, 0.20, 1),
                    on_release=lambda *_:
                    self.executar_exclusao(
                        backup
                    ),
                ),
            ],
        )

        self.dialogo.open()

    def executar_exclusao(
        self,
        backup,
    ):
        self.fechar_dialogo()

        try:
            excluir_backup(
                backup["caminho"]
            )
        except Exception as erro:
            print(
                "Erro ao excluir backup:",
                erro,
            )
            toast(
                "Não foi possível excluir."
            )
            return

        toast(
            "Backup excluído."
        )

        self.carregar_backups()

    def fechar_dialogo(self):
        if self.dialogo:
            self.dialogo.dismiss()
            self.dialogo = None

    def voltar(self, *_):
        MDApp.get_running_app().ir_para_tela(
            "configuracoes",
            "right",
        )