import os
import pyodbc
import time
import shutil
from datetime import datetime
from stat import S_IWRITE

from add_new_files import validate_file
from timer_dec import timer
from const import PRODUCTION, START_CATALOG, CURSOR, TRANSFER_FILE


def list_new_files():
    """ Adding to database drawing uploaded directly to PRODUCTION catalog."""
    source_cat = PRODUCTION
    query = 'Select Plik From Technologia;'
    try:
        result = CURSOR.execute(query)
    except pyodbc.Error:
        print('Connection to database failed.')
        return None

    new_files, current_db_files = [], []

    print('Data Base refreshed.')

    current_db_files = [file[0] for file in result]
    files_counter = 0
    pdf_list = ''

    for catalog in os.listdir(source_cat):
        if catalog in ['desktop.ini', 'Thumbs.db']:
            continue

        deep_path = os.path.join(source_cat, catalog)

        if not os.path.isdir(deep_path):
            continue

        current_files = os.listdir(deep_path)

        for file in current_files:
            if file.lower().endswith('pdf'):
                files_counter += 1
                pdf_list = f'{pdf_list}\n{file}'
                print(f'{files_counter} files has been analyzed.', end="\r")

    archive(pdf_list)

    print('\n', end='\r')


def archive(file_name):
    with open('W:/!!__PRODUKCJA__!!/2__Baza_Danych/pdf_list.txt', 'a', encoding='utf-8') as history_file:
        history_file.write(file_name)


def query_maker(new_pdf, komentarz):
    now = str(datetime.fromtimestamp(time.time(), ))[0:-3]
    query_2 = f"Insert Into Technologia (" \
        f"Plik, Status_Op, Komentarz, Stat, Liczba_Operacji, Kiedy" \
        f") VALUES (" \
        f"'{new_pdf}' ,6 ,'{komentarz}' ,0 ,11 ,'{now}'" \
        f");"
    print(query_2)


def main():
    # list_new_files()
    query_maker(new_pdf='1999999 1740-00-0000', komentarz='testowy',)


if __name__ == '__main__':
    main()
