import serial.tools.list_ports

PID_MICRO_PYTHON = 0x0005
VID = 0x2E8A

def find_pico_porta():
    portas = serial.tools.list_ports.comports()
    return portas
    # return [porta for porta in portas if VID == porta.vid]

def is_micropython(porta):
    return porta.pid == PID_MICRO_PYTHON

def print_info(porta):
        print('description', porta.description)
        print('device', porta.device)
        print('device_path',porta.device_path)
        print('hwid',porta.hwid)
        print('interface',porta.interface)
        print('location',porta.location)
        print('manufacturer',porta.manufacturer)
        print('name',porta.name)
        print('pid',porta.pid)
        print('product',porta.product)
        print('serial_number',porta.serial_number)
        print('subsystem',porta.subsystem)
        print('usb_description',porta.usb_description())
        print('usb_device_path',porta.usb_device_path)
        print('usb_info',porta.usb_info())
        print('usb_interface_path',porta.usb_interface_path)
        print('vid',porta.vid)

picos = find_pico_porta()
print(picos)
for pico in picos:
    print()
    print(pico.device, is_micropython(pico))
    print_info(pico)
    print()

