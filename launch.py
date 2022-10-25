import time
from datetime import datetime
from timer_dec import time_break
import add_new_files
import new_data_uploader
import file_manager
import sap_date
from const import TIME_OF_BREAK, FROM_OCLOCK, TO_OCLOCK


def wait(period):
    while period > 0:
        text = f'Next Refresh in {period:03d}s'
        print(text, end="\r")
        time.sleep(1)
        period -= 1
        print(' ' * len(text), end="\r")


def print_introduction():
    start = 'launched at : ' + str(datetime.fromtimestamp(time.time(), ))[0:-7]
    line_1 = 'AUTOMAT'
    print(50 * '-')
    print(f'|{line_1: ^48}|')
    print('|' + 48 * ' ' + '|')
    print(f'|{start: ^48}|')
    print('|' + 48 * ' ' + '|')
    print(50 * '-')


@time_break(from_=FROM_OCLOCK, to_=TO_OCLOCK)
def main():
    sap_date.update(column='Automat')
    add_new_files.main()
    sap_date.update(column='Automat_Start')
    new_data_uploader.main()
    file_manager.main()


if __name__ == '__main__':
    print_introduction()
    while True:
        main()
        wait(TIME_OF_BREAK)
        print(' ')
