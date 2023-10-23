import inspect
import os
import time
import shutil
import re

from class_file import File, Catalog
from datetime import datetime, date
from stat import S_IWRITE
from timer_dec import timer
from const import *
from pyodbc import Error
import stamps_adder
from merger import merging


catalogs_to_remove = []


@timer
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

    for catalog in os.listdir(source_cat):
        if catalog in ['desktop.ini', 'Thumbs.db']:
            continue

        deep_path = os.path.join(source_cat, catalog)

        if not os.path.isdir(deep_path):
            continue

        current_files = os.listdir(deep_path)

        for file in current_files:
            if file.endswith(MERGED_NAME):
                continue
            file_name = validate_file(file, catalog)
            if file_name and file_name not in current_db_files:
                new_files.append(file_name)
            elif not file_name and file.lower().endswith('.pdf'):
                new_bad_file(new_pdf=file, catalog=catalog)
                print(f'bad file: {file} in catalog:"1__Rysunki/{catalog}"')

            files_counter += 1
            print(f'{files_counter} files has been analyzed.', end="\r")

    print('\n', end='\r')

    for new_file in new_files:
        new_rec(new_pdf=new_file, order=new_file[0:7])
        archive(file_name=new_file)

    if len(new_files) == 0:
        print('No new files.')

    new_files.clear()


def general_checker():

    """Function providing other function runs once per day after a certain hour of the day."""
    query = 'SELECT General_check FROM SAP_data;'

    try:
        with CURSOR:
            CURSOR.execute(query)
            gen_checker_date = CURSOR.fetchone()[0]

    except Error:
        print(f'Database Error {inspect.currentframe().f_code.co_name}')
        return False

    if gen_checker_date:
        today = date.today()
        if gen_checker_date < today and datetime.now().hour > (GCP_OCLOCK - 1):
            query = f"UPDATE SAP_Data SET General_check = '{today}'"
            db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)
            return True
    return False


def list_new_files_new_way_class():

    for any_file in os.listdir(START_CATALOG):
        if any_file.upper() == REFILL_CAT:
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
                if file in ['Thumbs.db', '_v']:
                    continue
                file = File(name=file, bought_cat=catalog.bought, catalog=catalog.name)

                if validate_file_class(file):
                    os.chmod(file.start_path, S_IWRITE)
                    if cut_file_class(file=file):
                        File.add_moved_file()
                else:
                    if new_bad_file(new_pdf=file.name, catalog=file.catalog):
                        print(f'bad file: {file.file_name} in catalog: "4__Nowe_Rysunki/{file.catalog}"')
                        File.add_bad_file()
            elif file in BOUGHT_NAMES or catalog.bought:
                init_path = os.path.join(START_CATALOG, catalog.name, file)
                end_path = os.path.join(START_CATALOG, 'bought_script')
                shutil.move(init_path, end_path)

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
    if [file for file in os.listdir(catalog_path) if file.lower().endswith("pdf")]:
        return True
    else:
        return False


def new_rec(new_pdf, buy=False, order=''):
    now = str(datetime.fromtimestamp(time.time(), ))[0:-3]
    if buy:
        komentarz = 'kupowany'
    elif new_pdf.lower().endswith('h'):
        komentarz = 'częściowa kooperacja'
    else:
        komentarz = ''

    if 'info' in new_pdf.lower() or 'sap' in new_pdf.lower():
        query_1 = ""
    else:
        query_1 = f"IF NOT EXISTS (SELECT PO FROM OTM WHERE PO = {order}) " \
                  f"BEGIN " \
                  f"INSERT INTO OTM (PO, QUANTITY) VALUES ({order}, 1) " \
                  f"END " \
                  f"ELSE " \
                  f"BEGIN " \
                  f"UPDATE OTM " \
                  f"SET quantity = quantity + 1, merged = 0 WHERE PO = {order} " \
                  f"END; "

    query_2 = f"Insert Into Technologia (" \
        f"Plik, Status_Op, Komentarz, Stat, Liczba_Operacji, Kiedy" \
        f") VALUES (" \
        f"'{new_pdf}' ,6 ,'{komentarz}' ,0 ,11 ,'{now}'" \
        f");"
    query = query_1 + query_2

    db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)
    return None


def del_empty_catalogs():
    for folder in catalogs_to_remove:
        catalog_to_remove = os.path.join(START_CATALOG, folder)
        os.chmod(catalog_to_remove, S_IWRITE)
        shutil.rmtree(catalog_to_remove, ignore_errors=True, )
    catalogs_to_remove.clear()


def cut_file_class(file):

    if not os.path.exists(file.dest_catalog) and not file.loose:
        os.mkdir(file.dest_catalog)

    elif not os.path.exists(file.dest_catalog) and check_po_in_sap(file.po):
        os.mkdir(file.dest_catalog)

    while os.path.exists(file.dest_path):
        file.name_if_exist_class()

    if os.path.exists(file.dest_catalog):
        if file.bought_cat or file.bought_name:
            stamps_adder.stamper(file=file)
        else:
            try:
                file.move_file()
            except PermissionError:
                print(f'{file.name} -- not moved, permission error.')
                return False
    else:
        print(f'{file.name} -- not moved, There is no such Prod Order in Sap.')
        return False

    new_rec(new_pdf=file.file_name, buy=(file.bought_name or file.bought_cat), order=file.po)

    return True


def new_bad_file(new_pdf, catalog):
    if new_pdf.lower().endswith('.pdf'):
        while '--' in new_pdf:
            new_pdf = new_pdf.replace('--', '-')
        table = "Złe_Pliki"
        query = f"Begin " \
                f"If Not Exists (Select * From {table} Where u_Folder = '{catalog}' And u_Plik = '{new_pdf}') " \
                f"Begin " \
                f"Insert Into {table} (u_Folder, u_Plik) " \
                f" VALUES ('{catalog}', '{new_pdf}') " \
                f"End " \
                f"End"
        db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)
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

    if MERGED_NAME in name:
        return False

    return base_name


def validate_file_class(file: File):

    """ If name is proper, returns True"""

    if re.search(r"\d{7} .*[.]*", file.new_name.lower()) is None:
        return False

    if file.extension.lower() not in ACC_EXT:
        return False

    if not file.loose:
        if not file.proper_name:
            return False

    if file.file_name.endswith('_99'):
        return False

    if '--' in file.file_name:
        return False

    if MERGED_NAME in file.file_name:
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
    db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)

    return None


def new_files_to_db():
    table = "SAP_data"
    now = str(datetime.fromtimestamp(time.time(), ))[0:-7]
    query = f"Update {table} SET Automat = '{now}';"
    db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)


def check_po_in_sap(po_num):
    query = f"SELECT COUNT(Confirmation) FROM Sap WHERE [P.O.] = {po_num};"
    with CURSOR:
        try:
            CURSOR.execute(query)
            result = CURSOR.fetchone()

        except Error:
            print(f'Database Error in "check_po_in_sap"')
            return False

    return result[0] > 0


def main():
    new_files_to_db()
    truncate_bad_files()
    if GENERAL_CHECK_PERMISSION:
        if general_checker():
            list_new_files()
    else:
        list_new_files()
    list_new_files_new_way_class()
    merging()
    del_empty_catalogs()


if __name__ == '__main__':
    main()
