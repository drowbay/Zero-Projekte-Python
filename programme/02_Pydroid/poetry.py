from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from poetry_engine import generate_poem


class PoetryUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.poem_label = Label(text="Drücke den Button für ein Gedicht")
        self.add_widget(self.poem_label)

        btn = Button(text="Gedicht generieren")
        btn.bind(on_press=self.make_poem)
        self.add_widget(btn)

    def make_poem(self, instance):
        poem = generate_poem()
        self.poem_label.text = poem


class PoetryApp(App):
    def build(self):
        return PoetryUI()


if __name__ == "__main__":
    PoetryApp().run()
