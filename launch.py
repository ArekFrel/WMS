import time
from datetime import datetime
import add_new_files
import new_data_uploader
import file_manager
import sap_date
from constant import TIME_OF_BREAK

LINE_CLEAR = '\x1b[2K'


def wait(period):
    while period > 0:
        text = f'Next Refresh in {period:03d}s'
        print(text, end="\r")
        time.sleep(1)
        period -= 1
    print(end=LINE_CLEAR)


def print_introduction():
    start = 'launched at : ' + str(datetime.fromtimestamp(time.time(), ))[0:-7]
    line_1 = 'AUTOMAT'
    print(50 * '-')
    print(f'|{line_1: ^48}|')
    print('|' + 48 * ' ' + '|')
    print(f'|{start: ^48}|')
    print('|' + 48 * ' ' + '|')
    print(50 * '-')


def main():
    sap_date.update(column='Automat')
    add_new_files.main()
    sap_date.update(column='Automat_Start')
    new_data_uploader.main()
    file_manager.main()
    wait(TIME_OF_BREAK)
    print(' ')


if __name__ == '__main__':
    print_introduction()
    while True:
        # main()
        wait(5)