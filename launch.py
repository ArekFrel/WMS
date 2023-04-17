import time
from datetime import datetime
from timer_dec import time_break
import add_new_files
import new_data_uploader
import file_manager
import sap_date
import self_update
import subprocess
from const import TIME_OF_BREAK, FROM_OCLOCK, TO_OCLOCK, AUTOMAT_BAT


def wait(period):
    while period > 0:
        text = f'Next Refresh in {period:03d}s'
        print(text, end="\r")
        time.sleep(1)
        period -= 1
        print(' ' * len(text), end="\r")


def print_now():
    print(f'{str(datetime.fromtimestamp(time.time(), ))[0:-7]}')


def print_introduction():
    start = 'Launched at : ' + str(datetime.fromtimestamp(time.time(), ))[0:-7]
    line_1 = 'AUTOMAT'
    COL_START = '\33[34m'
    COL_END = '\033[0m'
    print(COL_START + 50 * '-' + COL_END)
    print(COL_START + f'|{line_1: ^48}|' + COL_END)
    print(COL_START + '|' + 48 * ' ' + '|' + COL_END)
    print(COL_START + f'|{start: ^48}|' + COL_END)
    print(COL_START + '|' + 48 * ' ' + '|' + COL_END)
    print(COL_START + 50 * '-' + COL_END)


@time_break(from_=FROM_OCLOCK, to_=TO_OCLOCK)
def main():
    print_now()
    sap_date.update(column='Automat')
    add_new_files.main()
    sap_date.update(column='Automat_Start')
    new_data_uploader.main()
    file_manager.main()


if __name__ == '__main__':
    print_introduction()
    while True:
        main()
        if self_update.check_for_update():
            self_update.update()
            subprocess.call(AUTOMAT_BAT)
            break
        wait(TIME_OF_BREAK)
        print(' ')
