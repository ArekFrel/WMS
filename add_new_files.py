import os
import time
import shutil
import pyodbc
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


def list_new_files_new_way():
    source_cat = START_CATALOG
    now = time.time()
    files_counter_good = 0
    files_counter_bad = 0

    for any_file in os.listdir(source_cat):
        deep_path = os.path.join(source_cat, any_file)

        """ If path is not directory, and loose file are not forbidden."""
        if not os.path.isdir(deep_path) and LOOSE_FILE_PERMISSION:
            any_file_name = validate_file(name=any_file)
            if any_file_name:
                os.chmod(deep_path, S_IWRITE)
                if cut_file(file=any_file_name, catalog=any_file_name[0:7], no_dir=False):
                    files_counter_good += 1
            continue
        elif not os.path.isdir(deep_path):
            continue

        catalog = any_file
        folder_data = os.path.getctime(deep_path)
        folder_age = now - folder_data
        if folder_age < TIMEOUT_FOR_PLANERS:
            continue

        new_files = os.listdir(deep_path)

        for file in new_files:
            if file in ['Thumbs.db', '_v']:
                continue

            file_name = validate_file(file, catalog)

            if file_name:
                os.chmod(os.path.join(deep_path, file), S_IWRITE)
                if cut_file(file=file_name, catalog=catalog):
                    files_counter_good += 1
            else:
                if new_bad_file(new_pdf=file, catalog=catalog):
                    print(f'bad file: {file}')
                    files_counter_bad += 1

        if not contains_pdfs(catalog=catalog):
            catalogs_to_remove.append(catalog)

    if files_counter_good != 1:
        num_g_files = 'files'
    else:
        num_g_files = 'file'

    if files_counter_bad != 1:
        num_b_files = 'files'
    else:
        num_b_files = 'file'

    if files_counter_good > 0:
        print(f'{files_counter_good} {num_g_files} moved to production and added to Database')

    if files_counter_bad > 0:
        print(f'{files_counter_bad} bad {num_b_files}')


def list_new_files_new_way_class():

    for any_file in os.listdir(START_CATALOG):
        if any_file == REFILL_CAT:
            refill_doc()
        deep_path = os.path.join(START_CATALOG, any_file)

        """ If path is not directory, and loose file are not forbidden."""
        if not os.path.isdir(deep_path) and LOOSE_FILE_PERMISSION:
            file = File(name=any_file)
            if validate_file_class(file=file):
                os.chmod(file.start_path, S_IWRITE)
                cut_file_class(file=file)
            continue
        elif not os.path.isdir(deep_path):
            continue

        catalog = Catalog(any_file)
        if not catalog.ready:
            continue

        for file in catalog.catalog_content():
            file = File(name=file, catalog=catalog.name)
            if file.name in ['Thumbs.db', '_v']:
                continue

            if validate_file_class(file):
                os.chmod(file.start_path, S_IWRITE)
                cut_file_class(file=file)
            else:
                if new_bad_file(new_pdf=file.name, catalog=file.catalog):
                    print(f'bad file: {file.file_name}')
                    File.add_bad_file()

        if not contains_pdfs(catalog=catalog.name):
            catalogs_to_remove.append(catalog.name)

    File.print_counter_status()
    File.set_counter_zero()


def refill_doc():
    start_cat = os.path.join(START_CATALOG, REFILL_CAT)
    for any_file in os.listdir(start_cat):
        file = File(name=any_file, catalog=REFILL_CAT)

        if os.path.isfile(file.dest_path):
            try:
                os.rename(file.start_path, file.start_path)
                os.rename(file.dest_path, file.dest_path)
                os.remove(file.dest_path)
                cut_file(file)
            except PermissionError:
                print(f'One of the file is opened!')
                continue
        else:
            try:
                os.rename(file.start_path, file.start_path)
                cut_file_class(file)
                new_rec(file.file_name)
            except PermissionError:
                print(f'"{file.dest_path}" of the file is opened!')
                continue


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

    # with CURSOR:
    #     CURSOR.execute(query)
    #     CURSOR.commit()
    print(query)
    return None


def del_empty_catalogs():
    for folder in catalogs_to_remove:
        catalog_to_remove = os.path.join(START_CATALOG, folder)
        shutil.rmtree(catalog_to_remove, ignore_errors=True)
    catalogs_to_remove.clear()


def cut_file(file, catalog, no_dir=True):
    dest_cat = os.path.join(PRODUCTION, catalog)
    moved_file = file + '.pdf'
    dest_file = os.path.join(dest_cat, moved_file)

    if not os.path.exists(dest_cat) and no_dir:
        os.mkdir(dest_cat)
    elif not os.path.exists(dest_cat) and not no_dir:
        print(f'{file} --  not moved, catalog does not exist.')
        return False

    a = 1
    new_name_moved_file = moved_file
    while os.path.exists(dest_file):
        new_name_moved_file = name_if_exist(new_name_moved_file, a)
        dest_file = os.path.join(PRODUCTION, catalog, new_name_moved_file)
        a += 1

    if no_dir:
        moved_file_path = os.path.join(START_CATALOG, catalog, moved_file)
    else:
        moved_file_path = os.path.join(START_CATALOG, moved_file)

    try:
        os.rename(moved_file_path, moved_file_path)
        shutil.move(moved_file_path, dest_file)
    except PermissionError:
        print(f'{moved_file} -- not moved, permission error .')
        return False

    new_rec_name = new_name_moved_file[0:-4]
    new_rec(new_pdf=new_rec_name)
    return True


def cut_file_class(file):

    if not os.path.exists(file.dest_catalog) and not file.loose:
        os.mkdir(file.catalog_path)
    elif not os.path.exists(file.dest_catalog) and file.loose:
        print(f'{file} --  not moved, catalog does not exist.')
        return False

    while os.path.exists(file.dest_path):
        file.name_if_exist_class()

    try:
        file.move_file()
    except PermissionError:
        print(f'{file.name} -- not moved, permission error .')
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


def validate_file_class(file: File, catalog=''):

    """ If name is proper, returns True"""

    if file.name == '_V':
        return False

    if '.' not in file.name:
        return False

    if file.extension.lower() != 'pdf':
        return False

    if not file.loose:
        if not file.proper_name:
            return False

    if file.file_name[7] != ' ':
        return False

    if not file.file_name[:6].isnumeric():
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
    new_files_to_db()
    truncate_bad_files()
    # list_new_files()
    list_new_files_new_way_class()
    del_empty_catalogs()


if __name__ == '__main__':
    main()
