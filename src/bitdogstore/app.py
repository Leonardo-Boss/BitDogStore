"""
Store for all BitDogLab projects
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import tools

class BitDogStore(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

        apps = tools.read_repo.get_apps_configs("/home/eppi/Downloads/Projetos_Disciplina_IE323/")
        buttons = []
        for app in apps:
            # Create a button-like box
            button_box = toga.Box(
                style=Pack(
                    padding=10,
                    background_color='lightgray',
                    alignment='center',
                ),
                # on_press=self.on_button_press
            )
            button_label = toga.Label(app["app_name"], style=Pack(padding=(10, 0)))
            button_box.add(button_label)
            button_box.config = app
            buttons.append(button_box)

        main_box = toga.Box(children=buttons, style=Pack(direction=COLUMN))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def app_screen(self, appconfig):
        box = toga.Box(style=Pack(direction=COLUMN, alignment='center', padding=10))



def main():
    return BitDogStore()
