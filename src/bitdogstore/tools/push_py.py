from . import ampy

#Carregar um arquivo python na placa
def push(file, destine, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    with open(file, 'rb') as f:
        file_manager.put(destine, f.read())

#Carregar uma pasta na placa
def mkdir(dir, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    file_manager.mkdir(dir, True)

#Remover um arquivo da placa
def rm(path, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    file_manager.rm(path)

#Remover uma pasta da placa
def rmdir(dir, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    file_manager.rmdir(dir)

#Listar arquivos na placa
def ls(device,dir=None,recursive=True):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    if dir:
        return file_manager.ls(dir,long_format=False,recursive=True)
    else:
        return file_manager.ls(long_format=False,recursive=True)

#Carregar um arquivos da placa
def get(file, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    return file_manager.get(file)
