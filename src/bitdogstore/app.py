"""
Store for all BitDogLab projects
"""

from asyncio import sleep
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import tools
import time
import os

class BitDogStore(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.home_button = toga.Button("Back", on_press=self.back_to_main, style=Pack(padding=10))
        self.install_button = toga.Button("Install", on_press=self.install, style=Pack(padding=10))
        self.installing = False
        self.main_box = self.create_main_box()
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def create_main_box(self):
        """Create the main layout with buttons for each app."""
        apps = tools.read_repo.get_apps_configs("/home/eppi/Downloads/Projetos_Disciplina_IE323/")
        buttons = []
        for app in apps:
            # Create a button
            button = toga.Button(
                app["app_name"],
                on_press=self.on_button_press,
                style=Pack(padding=10, flex=1)
            )
            button.config = app  # Store app config in the button
            buttons.append(button)

        return toga.Box(children=buttons, style=Pack(direction=COLUMN))

    def on_button_press(self, widget):
        """Handle button press to show app details."""
        app_config = widget.config
        self.show_app_screen(app_config)


    def show_app_screen(self, appconfig):
        """Display the screen for the selected app."""
        box = toga.Box(style=Pack(direction=COLUMN, alignment='center', padding=10))
        label = toga.Label(appconfig["app_name"], style=Pack(padding=(10, 0)))
        description = toga.Label(appconfig["description"], style=Pack(padding=(10, 0)))

        # Add a back button to return to the main screen
        self.install_button.config = appconfig
        
        box.add(label)
        box.add(description)
        button_box = toga.Box(children=[self.home_button, self.install_button], style=Pack(direction=ROW))
        box.add(button_box)

        self.main_window.content = box

    async def install(self, widget):
        if self.installing:
            return
        self.installing = True
        widget.enabled = False
        if widget.config.get('micropython_config'):
            await self.install_micropython(widget.config)
        else:
            await self.install_firmware(widget.config['c_config']['firmware'])

        print(f"installing {widget.config['app_name']} {time.time()}")
        await sleep(6)
        widget.enabled = True
        self.installing = False
        print(f"done")

    async def install_micropython(self, config):
        dev = '/dev/ttyACM0'
        #TODO: get hash file from board if exists
        # hash_firmware = tools.gen_hash(config['micropython_config']['firmware'])
        #TODO: update firmware
        # firmware_changed = True
        # if firmware_changed:
        #     await self.install_firmware(config['micropython_config']['firmware'])
        #TODO: verificar se arquivos mudaram usar dev dinamico
        print(config['path'])
        for file in config['micropython_config']['files']:
            print(file)
            # tools.push_py.push(file, dev)

    def windows_path_to_linux(self, path:str):
        return path.replace(r'\\', '/')


    async def install_firmware(self, firmware):
        pass

    def back_to_main(self, widget):
        """Return to the main screen."""
        self.main_window.content = self.main_box  # Set the content back to the main layout



def main():
    return BitDogStore()
