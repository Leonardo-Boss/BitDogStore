"""
Store for all BitDogLab projects
"""

from ast import dump
from asyncio import sleep
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import tools
import time
import os
import json

from tools import ampy
from tools import push_py
from tools import gen_hash
from tools import push_c

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
        apps = tools.read_repo.get_apps_configs("/home/eduardo/Desktop/Projetos_Disciplina_IE323/")
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
        widget.enabled = True
        self.installing = False
        print(f"done")

    async def install_micropython(self, config):
        dev = '/dev/ttyACM0'
        # hash_firmware = tools.gen_hash(config['micropython_config']['firmware'])
        # TODO: update firmware
        # firmware_changed = True
        # if firmware_changed:
        #     await self.install_firmware(config['micropython_config']['firmware'])
        # TODO: Remover arquivos
        new_firmware = gen_hash(config['micropython_config']['firmware'])
        try:
            cur_firmware = push_py.get('firmware',dev).decode()
        except:
            cur_firmware = None
            
        if new_firmware != cur_firmware:
            print('Firmware Diferente')
            input()
            mounts = push_c.get_mounts()
            #ToDo tirar sa porra de for
            for mount in mounts:
                push_c.push(config['micropython_config']['firmware'],mount)
                cur_mounts = push_c.get_mounts()
                while mount in cur_mounts:
                    cur_mounts = push_c.get_mounts()
                    await sleep(1)
        
        with open('firmware', 'w') as file:
            file.write(new_firmware)
        tools.push_py.push('firmware', 'firmware', dev)
        os.remove('firmware')
        
        print(f"Installing {config['path']}")
        new_version = await self.gen_version(config)
        try:
            cur_version = json.loads(push_py.get('version.json',dev))
        except:
            cur_version = None
        
        for file in config['micropython_config']['files']:
            # remover caminho do sistema para ter o caminho que será salvo no BitDogLab
            destine_path = file.removeprefix(config['path']+'/').split('/')
            destine_name = '/'.join(destine_path)
            if cur_version:
                if new_version.get(destine_name) == cur_version.get(destine_name):
                    print(f'{destine_name} igual')
                    continue
            print(f'{destine_name} diferente')
            # Criar pastas
            if len(destine_path) > 1:
                for i, dir in enumerate(destine_path[:1]):
                    tools.push_py.mkdir(dir, dev)
            tools.push_py.push(file, destine_name, dev)
            
        with open('version.json', 'w') as file:
            json.dump(new_version,file)
        tools.push_py.push('version.json', 'version.json', dev)
        os.remove('version.json')

    def windows_path_to_linux(self, path:str):
        return path.replace(r'\\', '/')


    async def install_firmware(self, firmware):
        pass

    def back_to_main(self, widget):
        """Return to the main screen."""
        self.main_window.content = self.main_box  # Set the content back to the main layout

    async def gen_version(self,config):
        version = {}
        for file in config['micropython_config']['files']:
            hash = gen_hash(file)
            destine_path = file.removeprefix(config['path']+'/')
            version[destine_path] = hash
        return version
        
def main():
    return BitDogStore()
