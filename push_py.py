import ampy.files as files
import ampy.pyboard as pyboard

def push(file, device):
    board = pyboard.Pyboard(device)
    file_manager = files.Files(board)
    with open(file, 'rb') as f:
        file_manager.put(file, f.read())


if __name__ == "__main__":
    import find
    pipicos = filter(lambda x: find.is_micropython(x), find.find_pico_porta())
    for pipico in pipicos:
        push('test.txt', pipico.device)
