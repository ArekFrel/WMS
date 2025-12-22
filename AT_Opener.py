import ctypes, os, shutil, sys, time

class Paths:
    LP = '\\\\PLOLFPS01.tp1.ad1.tetrapak.com\\PUBLIC\\!!__PRODUKCJA__!!\\'
    AT_FILE = f'{LP}3__Pliki\\Brygady\\Brygady.xlsm'

def update():
    if getattr(sys, 'frozen', False):
        current_path = os.path.dirname(sys.executable)
    else:
        current_path = os.path.dirname(os.path.abspath(__file__))
    current_file = os.path.join(current_path, "Brygady.xlsm")
    if os.path.exists(current_file):
        try:
            os.remove(current_file)
        except PermissionError:
            pass
        except FileNotFoundError:
            pass
    try:
        shutil.copy(Paths.AT_FILE, current_file)
        hide_file(current_file)
    except PermissionError:
        pass
    time.sleep(0.3)
    os.startfile(current_file, 'open')
    t=0

def hide_file(filepath):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    ctypes.windll.kernel32.SetFileAttributesW(filepath, FILE_ATTRIBUTE_HIDDEN)



def main():
    update()

if __name__ == '__main__':
    main()


