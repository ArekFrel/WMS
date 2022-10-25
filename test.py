import os
import time
import shutil
from datetime import datetime
from stat import S_IWRITE

from add_new_files import validate_file
from timer_dec import timer
from const import PRODUCTION, START_CATALOG, CURSOR, TRANSFER_FILE


@timer
def list_new_files():
    source_cat = PRODUCTION

    current_db_files = []
    for file in range(0, 32):
        current_db_files.append(file)
    files_counter = 0

    print('Data Base refreshed.')
    for catalog in os.listdir(source_cat):
        if catalog in ['desktop.ini', 'Thumbs.db']:
            continue

        deep_path = os.path.join(source_cat, catalog)

        if not os.path.isdir(deep_path):
            continue

        current_files = os.listdir(deep_path)
        new_files = []

        for file in current_files:
            file_name = validate_file(file, catalog)
            if file_name and file_name not in current_db_files:
                new_files.append(file_name)
            elif not file_name and file.lower().endswith('.pdf'):
                pass

            files_counter += 1
            print(f'{files_counter} files has been analyzed.', end="\r")


def main():
    list_new_files()


if __name__ == '__main__':
    main()
