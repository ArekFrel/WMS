import os, shutil
from wms_main.const import Paths
files_list = os.listdir(Paths.LASER_NEW_BASE)

def catalog_handler(path):
    for direcotry in os.listdir(path):
        if direcotry == 'ARCHIWUM' or direcotry.endswith('.db'):
            continue
        deep_path = os.path.join(path, direcotry)
        if os.path.isdir(deep_path):
            catalog_handler(deep_path)
        if os.path.isfile(deep_path):
            file_handler(deep_path)
    return None


def file_handler(path):
    if path.lower().endswith(".dxf"):
        new_name = new_namer(path)
        if new_name in files_list or '304L' in new_name:
            print(f'{new_name} skipped')
            return None
        new_path = os.path.join(Paths.LASER_NEW_BASE, new_name)
        try:
            shutil.copy(path, new_path)
            print(f'Copied {path.split('\\')[-1]}')
        except PermissionError:
            pass

    return None



def new_namer(file_name):

    main_name, extension = file_name.rsplit(".", 1)
    fin_index = main_name.rindex("a")
    new_main_name = f'{main_name[:fin_index].rsplit('\\', 1)[1]}' + '.' + extension
    return new_main_name



def base_creator():
    for directory in os.listdir(Paths.LASER_FORMER_BASE):
        deep_path = os.path.join(Paths.LASER_FORMER_BASE, directory)
        catalog_handler(deep_path)
#         \\PLOLFPS01.tp1.ad1.tetrapak.com\PLOL\P5_Material_Technology




def main():
    pass

if __name__ == '__main__':
    main()
