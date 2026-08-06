from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen


class SplashScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.02, 0.04, 0.10, 1)
            self.fundo = Rectangle(pos=self.pos, size=self.size)

        self.bind(
            pos=self.atualizar_fundo,
            size=self.atualizar_fundo
        )

        titulo = MDLabel(
            text="FINANÇAS PRO",
            halign="center",
            font_style="H3",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.22, 0.74, 0.97, 1),
        )

        subtitulo = MDLabel(
            text="Controle financeiro simples e inteligente",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(0.58, 0.64, 0.72, 1),
            pos_hint={"center_y": 0.42},
        )

        self.add_widget(titulo)
        self.add_widget(subtitulo)

    def atualizar_fundo(self, *_):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

    def on_enter(self):
        Clock.schedule_once(self.ir_para_dashboard, 1.5)

    def ir_para_dashboard(self, *_):
        self.manager.transition.direction = "left"
        self.manager.current = "dashboard"