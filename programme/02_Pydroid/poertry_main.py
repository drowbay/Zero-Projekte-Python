from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from poetry_engine import generate_poem

class PoetryApp(App):

    def show_poem(self, instance):
        poem = generate_poem()

        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        box.add_widget(Label(text=poem, halign="center"))

        close_btn = Button(text="✨ Noch eins", size_hint=(1, 0.3))
        box.add_widget(close_btn)

        popup = Popup(
            title="Mini Poetry",
            content=box,
            size_hint=(0.85, 0.6),
            auto_dismiss=True
        )

        close_btn.bind(on_press=lambda x: (popup.dismiss(), self.show_poem(x)))
        popup.open()

    def build(self):
        return Button(text="🪶 Gedicht generieren", on_press=self.show_poem)

if __name__ == "__main__":
    PoetryApp().run()
