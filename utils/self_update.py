import os
import shutil
from const import UPDATE_CAT, AUTOMAT_FILES_STORED
from stat import S_IWRITE


def check_for_update():

    if os.path.exists(UPDATE_CAT):
        return True
    else:
        return False


def update():
    folder_content = os.listdir(UPDATE_CAT)
    for file in folder_content:
        os.rename(os.path.join(UPDATE_CAT, file), os.path.join(UPDATE_CAT, file))
        shutil.move(os.path.join(UPDATE_CAT, file), os.path.join(AUTOMAT_FILES_STORED, file))
    os.chmod(UPDATE_CAT, S_IWRITE)
    shutil.rmtree(UPDATE_CAT, ignore_errors=True, )
    os.system('')
    print('WMS has been updated. \n' + '\033[91m' + 'Restarting...' + '\033[0m')


def main():
    pass


if __name__ == '__main__':
    main()
