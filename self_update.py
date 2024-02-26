import os
import shutil
from const import Paths
from stat import S_IWRITE


def check_for_update():

    if os.path.exists(Paths.UPDATE_CAT):
        return True
    else:
        return False


def update():
    folder_content = os.listdir(Paths.UPDATE_CAT)
    for file in folder_content:
        os.rename(os.path.join(Paths.UPDATE_CAT, file), os.path.join(Paths.UPDATE_CAT, file))
        shutil.move(os.path.join(Paths.UPDATE_CAT, file), os.path.join(Paths.AUTOMAT_FILES_STORED, file))
    os.chmod(Paths.UPDATE_CAT, S_IWRITE)
    shutil.rmtree(Paths.UPDATE_CAT, ignore_errors=True, )
    os.system('')
    print('WMS has been updated. \n' + '\033[91m' + 'Restarting...' + '\033[0m')


def main():
    pass


if __name__ == '__main__':
    main()
