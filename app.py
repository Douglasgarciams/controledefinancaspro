from kivy.uix.screenmanager import (
    ScreenManager,
    SlideTransition,
)
from kivymd.app import MDApp

from database.database import db

from screens.splash import SplashScreen
from screens.dashboard import DashboardScreen
from screens.transacao import TransacaoScreen
from screens.categorias import CategoriasScreen
from screens.editar_transacao import EditarTransacaoScreen
from screens.relatorios import RelatoriosScreen
from screens.alertas import AlertasScreen
from screens.configuracoes import ConfiguracoesScreen
from screens.backup import BackupScreen


class FinanceiroApp(MDApp):

    def build(self):
        self.title = "Finanças Pro"

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Green"

        gerenciador = ScreenManager(
            transition=SlideTransition(
                duration=0.25
            )
        )

        gerenciador.add_widget(
            SplashScreen(
                name="splash"
            )
        )

        gerenciador.add_widget(
            DashboardScreen(
                name="dashboard"
            )
        )

        gerenciador.add_widget(
            TransacaoScreen(
                name="transacao"
            )
        )

        gerenciador.add_widget(
            CategoriasScreen(
                name="categorias"
            )
        )

        gerenciador.add_widget(
            EditarTransacaoScreen(
                name="editar_transacao"
            )
        )

        gerenciador.add_widget(
            RelatoriosScreen(
                name="relatorios"
            )
        )

        gerenciador.add_widget(
            AlertasScreen(
                name="alertas"
            )
        )

        gerenciador.add_widget(
            ConfiguracoesScreen(
                name="configuracoes"
            )
        )

        gerenciador.add_widget(
            BackupScreen(
                name="backup"
            )
        )

        configuracoes = (
            db.obter_configuracoes_app()
        )

        self.theme_cls.theme_style = (
            configuracoes["tema"]
        )

        return gerenciador

    def ir_para_tela(
        self,
        nome_tela,
        direcao="left",
    ):
        if not self.root:
            return

        if not self.root.has_screen(nome_tela):
            raise ValueError(
                f"A tela '{nome_tela}' não foi registrada."
            )

        self.root.transition.direction = direcao
        self.root.current = nome_tela