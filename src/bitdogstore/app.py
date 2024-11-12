"""
Store for all BitDogLab projects
"""

from ast import dump
from asyncio import sleep
import textwrap
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets.scrollcontainer import ScrollContainer
import tools
import time
import os
import json
import serial
from markdown import markdown  # To convert Markdown text to HTML

from tools import ampy
from tools import push_py
from tools import gen_hash
from tools import push_c
from tools.find import is_micropython,find_porta

class BitDogStore(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

        self.ports = {}

        self.apps = tools.read_repo.get_apps_configs("/home/eduardo/Desktop/Projetos_Disciplina_IE323/")

        dropdown = toga.Selection(items=[], style=Pack(padding=10, flex=1))
        dropdown_refresh = toga.Button("Refresh", on_press=self.create_dropdown, style=Pack(padding=10))
        self.dropdown = toga.Box(children=[dropdown, dropdown_refresh], style=Pack(direction=ROW))

        self.create_dropdown()
        # Optional: add a function to handle selection changes
        self.dropdown.children[0].on_change = self.on_change

        # Label to display selected option
        self.label = toga.Label("Select an option from the dropdown menu.",style=Pack(padding=10, flex=1))

        self.home_button = toga.Button("Back", on_press=self.back_to_main, style=Pack(padding=10))
        self.install_button = toga.Button("Install", on_press=self.install, style=Pack(padding=10))
        self.installing = False
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.create_main_box()
        self.main_window.show()

    def on_change(self, widget):
        print(self.dropdown.children[0].value)

    def create_dropdown(self, widget=None):
        # Dropdown menu (Selection widget)
        serial_ports = list(map(lambda x: x.device, tools.find.find_pico_porta()))
        self.ports = {}
        for serial_port in serial_ports:
            self.ports[serial_port] = True
        mount_ports = push_c.get_mounts()
        for mount_port in mount_ports:
            self.ports[mount_port] = False
        items = serial_ports + mount_ports
        self.dropdown.children[0].items = items
        self.dropdown.children[1].on_press = self.create_dropdown

    def create_dropdown_c(self, widget=None):
        # Dropdown menu (Selection widget)
        mount_ports = push_c.get_mounts()
        self.ports = {}
        for serial_port in mount_ports:
            self.ports[serial_port] = False
        self.dropdown.children[0].items = mount_ports
        self.dropdown.children[1].on_press = self.create_dropdown_c

    def create_dropdown_py(self, widget=None):
        # Dropdown menu (Selection widget)
        items = list(map(lambda x: x.device, tools.find.find_pico_porta()))
        self.ports = {}
        for serial_port in items:
            self.ports[serial_port] = True
        self.dropdown.children[0].items = items
        self.dropdown.children[1].on_press = self.create_dropdown_py

    def create_main_box(self):
        """Create the main layout with buttons for each app."""
        buttons = []
        dropdown = toga.Box(children=[self.label, self.dropdown], style=Pack(direction=COLUMN))
        width = 300
        j = 0
        boxes_ = []
        boxes = []
        for app in self.apps:
            j += 1
            image = toga.Image(app['icon'])
            image_widget = toga.ImageView(image,style=Pack(width=width))

            button = toga.Button(
                app["app_name"],
                on_press=self.on_button_press,
                style=Pack(padding=10, flex=1, width=width)
            )
            button.config = app  # Store app config in the button
            box = toga.Box(children=[image_widget,button], style=Pack(direction=COLUMN))
            # agora deve funcionar deu
            boxes.append(box)
            boxes_.append(toga.Box(children=boxes,style=Pack(direction=ROW))) 
            if j == 5:
                j = 0
                boxes = []
                continue
        stuff = toga.Box(children=[dropdown]+boxes_, style=Pack(direction=COLUMN))
        return toga.ScrollContainer(content= stuff)

    def on_button_press(self, widget):
        """Handle button press to show app details."""
        app_config = widget.config
        self.show_app_screen(app_config)


    def show_app_screen(self, appconfig):
        """Display the screen for the selected app."""
        box = toga.Box(style=Pack(direction=COLUMN, alignment='center', padding=10))
        label = toga.Label(appconfig["app_name"], style=Pack(padding=(10, 0)))
        description = toga.Label(appconfig["description"], style=Pack(padding=(10, 0)))
        has_app_page_docs = False
        if appconfig.get("app_page_docs"):
            has_app_page_docs = True
            with open(appconfig["app_page_docs"],"r") as readme:
                app_page_docs_md =  readme.read()
                
            app_page_docs_box = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))
            app_page_docs_html = markdown(app_page_docs_md)
            text_display = toga.WebView(style=Pack(flex=1))
            text_display.set_content('file://', f"<html><body>{app_page_docs_html}</body></html>")
            app_page_docs_box.add(text_display)

        # Add a back button to return to the main screen
        self.install_button.config = appconfig

        box.add(self.dropdown)
        box.add(self.label)
        box.add(label)
        box.add(description)
        if has_app_page_docs:
            box.add(app_page_docs_box)
        button_box = toga.Box(children=[self.home_button, self.install_button], style=Pack(direction=ROW))
        box.add(button_box)

        self.main_window.content = box

    async def install(self, widget):
        if self.installing:
            return
        self.installing = True
        widget.enabled = False
        if widget.config.get('micropython_config'):
            print('install_micropython')
            await self.install_micropython(widget.config)
        else:
            print('install_c')
            if self.ports[self.dropdown.children[0].value]:
                print('install_c python')
                await self.select_device_window_c(widget.config)
            else:
                print('install_c c')
                await self.update_firmware(widget.config['c_config']['firmware'])

        print(f"installing {widget.config['app_name']} {time.time()}")
        widget.enabled = True
        self.installing = False
        print(f"done")

    async def install_micropython(self, config):
        dev = self.dropdown.children[0].value

        await self.check_change_micropython_firmware(config,dev)
        print(f"Installing {config['path']}")
        new_version = await self.gen_version(config)
        cur_version = await self.get_cur_version(dev)
        files_remove = await self.get_cur_app_files(dev)
        for file in config['micropython_config']['files']:
            # remover caminho do sistema para ter o caminho que será salvo no BitDogLab
            destine_path = file.removeprefix(config['path']+'/').split('/')
            destine_name = '/'.join(destine_path)
            if f'/{destine_name}' in files_remove:
                files_remove.pop(files_remove.index(f'/{destine_name}'))
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
        await self.remove_files(files_remove,dev)
        await self.update_version(new_version,dev)

    async def check_change_micropython_firmware(self,config,dev):
        new_firmware = gen_hash(config['micropython_config']['firmware'])
        print('self.ports',self.ports[dev],dev)
        if self.ports[dev]:
            if not is_micropython(find_porta(dev)):
                print("Mudando Firmware para micropython")
                self.firmware_updated = False
                self.select_device_window(config)
                while not self.firmware_updated:
                    await sleep(0.5)
                return
            else:
                try:
                    cur_firmware = push_py.get('firmware',dev).decode()
                except:
                    cur_firmware = None

                if new_firmware != cur_firmware:
                    print('Firmware Diferente')
                    self.firmware_updated = False
                    self.select_device_window(config)
                    while not self.firmware_updated:
                        await sleep(0.5)
                    return
        else:
            await self.update_firmware(config['micropython_config']['firmware'])
        self.create_firmware(new_firmware, dev)

    def create_firmware(self, new_firmware, dev):
        with open('firmware', 'w') as file:
            file.write(new_firmware)
        tools.push_py.push('firmware', 'firmware', dev)
        os.remove('firmware')

    async def remove_files(self,files,dev):
        for file in files:
            try:
                push_py.rm(file,dev)
            except:
                push_py.rmdir(file,dev)
            print(f'arquivo {file} apagado')

    async def get_cur_version(self,dev):
        try:
            cur_version = json.loads(push_py.get('version.json',dev))
        except:
            cur_version = None

        return cur_version

    async def get_cur_app_files(self,dev):
        files_remove = push_py.ls(dev)
        if '/firmware' in files_remove:
            files_remove.remove('/firmware')
        if '/version.json' in files_remove:
            files_remove.remove('/version.json')
        return files_remove

    async def update_version(self,new_version,dev):
        with open('version.json', 'w') as file:
            json.dump(new_version,file)
        tools.push_py.push('version.json', 'version.json', dev)
        os.remove('version.json')

    def windows_path_to_linux(self, path:str):
        return path.replace(r'\\', '/')

    def back_to_main(self, widget):
        """Return to the main screen."""
        self.main_window.content = self.create_main_box()

    def select_device_window(self, config):
        """window for selecting a device after python firmware install"""
        self.create_dropdown_c()
        box = toga.Box(style=Pack(direction=COLUMN, alignment='center', padding=10))
        label = toga.Label("Selecione o BitDogLab Correto", style=Pack(padding=(10, 0)))

        box.add(self.dropdown)
        box.add(self.label)
        box.add(label)
        button = toga.Button("Ok", on_press=self.update_firmware_go_back, style=Pack(padding=10))
        button.config = config
        box.add(button)

        self.main_window.content = box

    def select_device_window_py(self, config):
        """window for selecting a device after python firmware install"""
        self.create_dropdown_py()
        box = toga.Box(style=Pack(direction=COLUMN, alignment='center', padding=10))
        label = toga.Label("Selecione o BitDogLab Correto", style=Pack(padding=(10, 0)))

        box.add(self.dropdown)
        box.add(self.label)
        box.add(label)
        button = toga.Button("Ok", on_press=self.create_firmware_version_go_back, style=Pack(padding=10))
        button.config = config
        box.add(button)

        self.main_window.content = box

    async def create_firmware_version_go_back(self, widget):
        config = widget.config
        self.show_app_screen(config)
        self.create_dropdown()
        new_firmware = config['micropython_config']['firmware']
        self.create_firmware(new_firmware, self.dropdown.children[0].value)
        self.firmware_updated = True

    async def update_firmware_go_back(self, widget):
        config = widget.config
        self.show_app_screen(config)
        self.create_dropdown()
        new_firmware = config['micropython_config']['firmware']
        await self.update_firmware(new_firmware)
        self.select_device_window_py(widget.config)

    async def select_device_window_c(self, config):
        """window for selecting a device after python firmware install"""
        self.create_dropdown_c()
        box = toga.Box(style=Pack(direction=COLUMN, alignment='center', padding=10))
        label = toga.Label("Selecione o BitDogLab Correto", style=Pack(padding=(10, 0)))

        box.add(self.dropdown)
        box.add(self.label)
        box.add(label)
        button = toga.Button("Ok", on_press=self.update_firmware_go_back_c, style=Pack(padding=10))
        button.config = config
        box.add(button)

        self.main_window.content = box

    async def update_firmware_go_back_c(self, widget):
        config = widget.config
        self.create_dropdown()
        self.show_app_screen(config)
        new_firmware = config['c_config']['firmware']
        await self.update_firmware(new_firmware)
        self.firmware_updated = True

    def ok(self, widget):
        print('ok')

    async def gen_version(self,config):
        version = {}
        for file in config['micropython_config']['files']:
            hash = gen_hash(file)
            destine_path = file.removeprefix(config['path']+'/')
            version[destine_path] = hash
        return version

    async def update_firmware(self,firmware):
        mount = self.dropdown.children[0].value

        push_c.push(firmware,mount)
        cur_mounts = push_c.get_mounts()
        while mount in cur_mounts:
            cur_mounts = push_c.get_mounts()
            await sleep(1)

def main():
    return BitDogStore()
