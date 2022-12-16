import os
import time
import shutil
import re
from class_file import File, Catalog
from datetime import datetime
from stat import S_IWRITE
from timer_dec import timer
from const import *


catalogs_to_remove = []


@timer
def list_new_files():
    """ Adding to database drawing uploaded
    directly to PRODUCTION catalog."""
    source_cat = PRODUCTION
    query = 'Select Plik From Technologia;'
    try:
        result = CURSOR.execute(query)
    except pyodbc.Error:
        print('Connection to database failed.')
        return None

    new_files, current_db_files = [], []

    print('Data Base refreshed.')

    for file in result:
        current_db_files.append(file[0])
    files_counter = 0

    for catalog in os.listdir(source_cat):
        if catalog in ['desktop.ini', 'Thumbs.db']:
            continue

        deep_path = os.path.join(source_cat, catalog)

        if not os.path.isdir(deep_path):
            continue

        current_files = os.listdir(deep_path)

        for file in current_files:
            file_name = validate_file(file, catalog)
            if file_name and file_name not in current_db_files:
                new_files.append(file_name)
            elif not file_name and file.lower().endswith('.pdf'):
                new_bad_file(new_pdf=file, catalog=catalog)

            files_counter += 1
            print(f'{files_counter} files has been analyzed.', end="\r")

    print('\n', end='\r')

    for new_file in new_files:
        new_rec(new_pdf=new_file)
        archive(file_name=new_file)

    if len(new_files) == 0:
        print('No new files.')

    new_files.clear()


def list_new_files_new_way_class():

    for any_file in os.listdir(START_CATALOG):
        if any_file == REFILL_CAT:
            refill_doc()
            continue
        deep_path = os.path.join(START_CATALOG, any_file)

        """ If path is not directory, and loose file are not forbidden."""
        if not os.path.isdir(deep_path) and LOOSE_FILE_PERMISSION:
            file = File(name=any_file)
            if validate_file_class(file=file):
                os.chmod(file.start_path, S_IWRITE)
                if cut_file_class(file=file):
                    File.add_moved_file()
            continue
        elif not os.path.isdir(deep_path):
            continue

        catalog = Catalog(any_file)
        if not catalog.ready:
            continue

        for file in catalog.catalog_content():
            if not os.path.isdir(os.path.join(catalog.catalog_path, file)):
                file = File(name=file, catalog=catalog.name)
                if file.name in ['Thumbs.db', '_v']:
                    continue

                if validate_file_class(file):
                    os.chmod(file.start_path, S_IWRITE)
                    if cut_file_class(file=file):
                        File.add_moved_file()

                else:
                    if new_bad_file(new_pdf=file.name, catalog=file.catalog):
                        print(f'bad file: {file.file_name}')
                        File.add_bad_file()

        if not contains_pdfs(catalog=catalog.name) and catalog.ready:
            catalogs_to_remove.append(catalog.name)

    File.print_counter_status()
    File.set_counter_zero()


def refill_doc():
    start_cat = os.path.join(START_CATALOG, REFILL_CAT)
    for any_file in os.listdir(start_cat):
        file = File(name=any_file, catalog=REFILL_CAT)

        if os.path.isfile(file.dest_path):
            os.chmod(file.dest_path, S_IWRITE)
            try:
                os.rename(file.start_path, file.start_path)
                # os.rename(file.dest_path, file.dest_path)
                os.remove(file.dest_path)
                shutil.move(file.start_path, file.dest_path)
                File.add_replaced_file()
            except PermissionError:
                print(f'One of the file is opened!')
                continue
        else:
            try:
                os.rename(file.start_path, file.start_path)
                cut_file_class(file)
                File.add_refilled_file()
            except PermissionError:
                print(f'"{file.dest_path}" of the file is opened!')
                continue

    if not contains_pdfs(catalog=REFILL_CAT):
        catalogs_to_remove.append(REFILL_CAT)


def archive(file_name):
    with open(TRANSFER_FILE, 'a', encoding='utf-8') as history_file:
        now = str(datetime.fromtimestamp(time.time(), ))[0:-6]
        history_file.write(f'{now}____{file_name} \n')


def contains_pdfs(catalog):
    catalog_path = os.path.join(START_CATALOG, catalog)
    for file in os.listdir(catalog_path):
        if file.lower().endswith('pdf'):
            return True
    return False


def new_rec(new_pdf):
    table = "Technologia"
    now = str(datetime.fromtimestamp(time.time(), ))[0:-3]
    query = f"Insert Into {table} (" \
            f"Plik,Status_Op, Stat, Liczba_Operacji, Kiedy" \
            f") VALUES (" \
            f"'{new_pdf}', 6, 0, 11, '{now}'" \
            f");"

    with CURSOR:
        CURSOR.execute(query)
        CURSOR.commit()
    return None


def del_empty_catalogs():
    for folder in catalogs_to_remove:
        catalog_to_remove = os.path.join(START_CATALOG, folder)
        shutil.rmtree(catalog_to_remove, ignore_errors=True)
    catalogs_to_remove.clear()


def cut_file_class(file):

    if not os.path.exists(file.dest_catalog) and not file.loose:
        os.mkdir(file.dest_catalog)
    elif not os.path.exists(file.dest_catalog) and file.loose:
        print(f'{file} --  not moved, catalog does not exist.')
        return False

    while os.path.exists(file.dest_path):
        file.name_if_exist_class()
    try:
        file.move_file()
    except PermissionError:
        print(f'{file.name} -- not moved, permission error.')
        return False

    new_rec(new_pdf=file.new_name)
    return True


def new_bad_file(new_pdf, catalog):
    if new_pdf.lower().endswith('.pdf'):
        while '--' in new_pdf:
            new_pdf = new_pdf.replace('--', '-')
        table = "Złe_Pliki"
        query = f"Begin " \
                f"If Not Exists (Select * From {table} Where u_Folder = {catalog} And u_Plik = '{new_pdf}') " \
                f"Begin " \
                f"Insert Into {table} (u_Folder, u_Plik) " \
                f" VALUES ('{catalog}', '{new_pdf}') " \
                f"End " \
                f"End"
        with CURSOR:
            CURSOR.execute(query)
            CURSOR.commit()
        return True
    return False


def validate_file(name, catalog=''):

    """ If name is proper, returns name without extension"""

    if name == '_V':
        return False

    if '.' not in name:
        return False

    base_name, extension = name.rsplit('.', 1)

    if extension.lower() != 'pdf':
        return False

    if catalog:
        if catalog != name[0:7]:
            return False

    if name[7] != ' ':
        return False

    if not name[:6].isnumeric():
        return False

    if base_name.endswith('_99'):
        return False

    if '--' in name:
        return False

    return base_name


def validate_file_class(file: File):

    """ If name is proper, returns True"""

    if not (re.search(r"\d{7} .*[.]pdf", file.name.lower())):
        return False

    if not file.loose:
        if not file.proper_name:
            return False

    if file.file_name.endswith('_99'):
        return False

    if '--' in file.file_name:
        return False

    return True


def name_if_exist(file: str, number: int):
    name, extension = file.rsplit(sep='.', maxsplit=1)
    if '_' in name[-3:-1]:
        base_name, ord_num = name.split(sep='_')
        new_name = f'{base_name}_{int(ord_num) + 1}.{extension}'
    else:
        new_name = f'{name}_{number}.{extension}'
    return new_name


def truncate_bad_files():
    table = "Złe_Pliki"
    query = f"Delete From {table}"
    with CURSOR:
        CURSOR.execute(query)
        CURSOR.commit()
    return None


def new_files_to_db():
    table = "SAP_data"
    now = str(datetime.fromtimestamp(time.time(), ))[0:-7]
    query = f"Update {table} SET Automat = '{now}';"

    with CURSOR:
        CURSOR.execute(query)
        CURSOR.commit()


def main():
    # new_files_to_db()
    truncate_bad_files()
    list_new_files()
    list_new_files_new_way_class()
    del_empty_catalogs()


if __name__ == '__main__':
    main()
