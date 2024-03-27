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


class Restart:

    proceed = False

    def __init__(self):
        self.start_time = time.time()

    def launch_able(self):
        if datetime.now().hour == TimeConsts.HOUR and datetime.now().minute > TimeConsts.MINUTES:
            return False
        if time.time() - self.start_time > TimeConsts.SCHD_TIME - TimeConsts.TIME_OF_BREAK:
            return False
        return True


def countdown(restart_start):
    secs = TimeConsts.SCHD_TIME - (int(time.time() - restart_start)) - 1
    # print(f'{t} rest\n')
    # print(f'{int(restart_start)} restart start \n')
    # print(f'{int(time.time())} now time \n')
    while secs >= 0:
        timer = f'The window closes in {secs:02d}'
        print(timer, end="\r")
        time.sleep(1)
        secs -= 1


def launch_able():
    if datetime.now().hour == TimeConsts.HOUR and datetime.now().minute > TimeConsts.MINUTES:
        return False
    return True


def print_reset_break(arg):
    os.system('')
    print('\033[1;32m' + 'Everything ok, restart soon' + '\033[0m')
    countdown(arg)


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
def cycle():
    print_now()
    sap_date.update(column='Automat')
    add_new_files.main()
    sap_date.update(column='Automat_Start')
    if new_data_uploader.main():
        file_manager.main()


def main():
    restart = Restart()
    if self_update.check_for_update():
        self_update.update()
        subprocess.call(Paths.AUTOMAT_BAT)
        Restart.proceed = False
        return None

    if restart.launch_able():
        print_introduction()
        while restart.launch_able():
            cycle()
            wait(TimeConsts.TIME_OF_BREAK)
            if self_update.check_for_update():
                self_update.update()
                Restart.proceed = True
                return None
        print_reset_break(restart.start_time)
    else:
        print_reset_break(restart.start_time)


if __name__ == '__main__':
    main()
    if Restart.proceed:
        subprocess.call(Paths.AUTOMAT_BAT)
