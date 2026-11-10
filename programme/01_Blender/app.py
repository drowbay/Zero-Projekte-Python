from kivy.app import App
from kivy.uix.button import Button

class ZeroApp(App):
    def build(self):
        return Button(text="Hallo Zero 😎\nLumÿè lebt!")

ZeroApp().run()
