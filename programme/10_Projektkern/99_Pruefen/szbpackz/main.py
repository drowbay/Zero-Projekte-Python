from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '1')
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'window_state', 'visible')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        label = Label(text="🚀 Buildozer Test OK", font_size=32)
        btn = Button(text="Klick mich", size_hint=(1, 0.3))

        btn.bind(on_press=lambda *_: setattr(label, "text", "✅ Button funktioniert"))

        layout.add_widget(label)
        layout.add_widget(btn)
        return layout


if __name__ == "__main__":
    TestApp().run()
