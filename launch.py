import time
from datetime import datetime
from wms_main.timer_dec import time_break
import math
from utils.quotation_export import check_for_qoutation_export
from wms_main import sap_date, file_manager, new_data_uploader, self_update, add_new_files
import subprocess
import os
from wms_main.const import Paths, TimeConsts, Options


class Restart:
    proceed = False

    @staticmethod
    def launch_able(arg):
        minutes_rest = int(datetime.now().minute % 10)
        minutes_break = math.ceil(TimeConsts.TIME_OF_BREAK / 60)
        if arg == "start":
            return not(TimeConsts.MINUTE_START - minutes_rest in range(1, minutes_break))
        if arg == "continue":
            return not(TimeConsts.MINUTE_START - minutes_rest in range(1, minutes_break + 1))

        return True


def countdown():
    rest_minutes = datetime.now().minute % 10
    secs = 60 * (TimeConsts.MINUTE_START - rest_minutes - 1) + (60 - datetime.now().second) - 2
    # print(secs)
    while secs >= 0:
        timer = f'The window closes in {secs:03d}s'
        print(timer,  end="\r")
        time.sleep(1)
        secs -= 1
        print(' ' * len(timer),  end="\r")


def print_reset_break():
    os.system('')
    print('\033[1;32m' + 'Everything is ok, restart soon' + '\033[0m')
    countdown()


def wait(period):
    exec_time = 0
    while period > 0:
        if Options.IQE:
            exec_time = check_for_qoutation_export()
        text = f'Next Refresh in {period:03d}s'
        print(text, end="\r")
        time.sleep(1 - exec_time)
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

    if not Options.IQE:
        check_for_qoutation_export()


def main():
    restart = Restart()
    if self_update.check_for_update():
        self_update.update()
        subprocess.call(Paths.AUTOMAT_BAT)
        Restart.proceed = False
        return None

    if restart.launch_able(arg="start"):
        print_introduction()
        while True:
            cycle()
            if restart.launch_able(arg="continue"):
                wait(TimeConsts.TIME_OF_BREAK)
                if self_update.check_for_update():
                    self_update.update()
                    Restart.proceed = True
                    return None
            else:
                print_reset_break()
                return None
    else:
        print_reset_break()


if __name__ == '__main__':

    main()
    if Restart.proceed:
        subprocess.call(Paths.AUTOMAT_BAT)
