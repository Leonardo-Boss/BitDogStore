from . import ampy

def push(file, destine, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    with open(file, 'rb') as f:
        file_manager.put(destine, f.read())

def mkdir(dir, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    file_manager.mkdir(dir, True)

def rm(path, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    file_manager.rm(path)
    
def rmdir(dir, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    file_manager.rmdir(dir)

def ls(device,dir=None):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    if dir:
        return file_manager.ls(dir,long_format=False)
    else:
        return file_manager.ls(long_format=False)

def get(file, device):
    board = ampy.pyboard.Pyboard(device)
    file_manager = ampy.files.Files(board)
    return file_manager.get(file)
    
if __name__ == "__main__":
    import find
    pipicos = filter(lambda x: find.is_micropython(x), find.find_pico_porta())
    for pipico in pipicos:
        push('/home/eduardo/Desktop/BitDogStore/test.txt', 'test.txt', pipico.device)