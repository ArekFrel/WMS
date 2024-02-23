import time
from datetime import datetime
from timer_dec import time_break
import add_new_files
import new_data_uploader
import file_manager
import sap_date
import self_update
import subprocess
import os
from const import Paths, TimeConsts


def launch_able():
    if datetime.now().hour == TimeConsts.HOUR and datetime.now().minute > TimeConsts.MINUTES:
        return False
    return True


def print_reset_break():
    os.system('')
    print('\033[1;32m' + 'Please wait until Script will be launched by Microsoft Windows At 6:00' + '\033[0m')


def wait(period):
    while period > 0:
        text = f'Next Refresh in {period:03d}s'
        print(text, end="\r")
        time.sleep(1)
        period -= 1
        print(' ' * len(text), end="\r")
    print(' ')


def print_now():
    os.system('')
    COL_START = '\33[93m'
    COL_END = '\033[0m'
    print(f'{COL_START}{str(datetime.fromtimestamp(time.time(), ))[0:-7]} {COL_END}')


def print_introduction():
    os.system('')
    start = 'Launched at : ' + str(datetime.fromtimestamp(time.time(), ))[0:-7]
    line_1 = 'AUTOMAT'
    COL_START = '\33[94m'
    COL_END = '\033[0m'
    print(COL_START + ' ' + 48 * '_' + ' ' + COL_END)
    print(COL_START + '|' + 48 * ' ' + '|' + COL_END)
    print(COL_START + f'|{line_1: ^48}|' + COL_END)
    print(COL_START + '|' + 48 * ' ' + '|' + COL_END)
    print(COL_START + f'|{start: ^48}|' + COL_END)
    print(COL_START + '|' + 48 * '_' + '|' + COL_END)
    print('')


@time_break(from_=TimeConsts.FROM_OCLOCK, to_=TimeConsts.TO_OCLOCK)
def main():
    if self_update.check_for_update():
        self_update.update()
        subprocess.call(Paths.AUTOMAT_BAT)
    print_now()
    sap_date.update(column='Automat')
    add_new_files.main()
    sap_date.update(column='Automat_Start')
    if new_data_uploader.main():
        file_manager.main()



if __name__ == '__main__':
    if launch_able():
        print_introduction()
        while launch_able():
            main()
            wait(TimeConsts.TIME_OF_BREAK)
        print_reset_break()
    else:
        print_reset_break()


