import inspect
import os.path

from wms_main import teco_completer
import shutil
import re
from wms_main.class_file import File, Catalog
from datetime import date
from utils.watermark_remover import watermarks_remover as wm
from wms_main.timer_dec import timer
from wms_main.const import *
from pyodbc import Error
from utils import stamps_adder
from utils.merger import merging
from utils.pump_block_tracker import pb_tracker

catalogs_to_remove = []


@timer
def list_new_files():
    """ Adding to database drawing uploaded directly to PRODUCTION catalog."""
    source_cat = Paths.PRODUCTION
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
            if file_name and file_name not in current_db_files + ['merged']:
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
        if gen_checker_date < today and datetime.now().hour > (TimeConsts.GCP - 1):
            query = f"UPDATE SAP_Data SET General_check = '{today}'"
            db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)
            return True
    return False


def refill_doc():
    start_cat = os.path.join(Paths.START_CATALOG, REFILL_CAT)
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
    with open(Paths.TRANSFER_FILE, 'a', encoding='utf-8') as history_file:
        now = str(datetime.fromtimestamp(time.time(), ))[0:-6]
        history_file.write(f'{now}____{file_name} \n')


def contains_pdfs(catalog):
    if [file for file in os.listdir(catalog.catalog_path) if file.lower().endswith('pdf')]:
        return True
    if [file for file in os.listdir(catalog.catalog_path) if os.path.isdir(catalog.catalog_path + f'//{file}')]:
        return True
    else:
        return False


def new_rec(new_pdf, buy=False, sub_buy=False, order=''):
    if buy:
        komentarz = 'kupowany'
    elif sub_buy:
        komentarz = 'Część złożenia kupowanego'
    elif new_pdf.lower().endswith('h'):
        komentarz = 'częściowa kooperacja'
        # last_id = -1                      '''recently deleted'''
        # if new_pdf[-2] == ' ':            '''recently deleted'''
        #     last_id = 2                   '''recently deleted'''
        # new_pdf = new_pdf[:last_id]       '''recently deleted'''
    else:
        komentarz = ''

    now = str(datetime.fromtimestamp(time.time(), ))[0:-3]

    if 'info' in new_pdf.lower() or 'sap' in new_pdf.lower():
        query = f"Insert Into Technologia (" \
                  f"Plik, PO, Rysunek, OP_1, Status_Op, Komentarz, Stat, Liczba_Operacji, Kiedy" \
                  f") VALUES (" \
                  f"'{new_pdf}', '{new_pdf[0:7]}', '{new_pdf[8:]}', 'Info', 8, '{komentarz}', 0, 1, '{now}'" \
                  f");"
        db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)
        return None
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
    if buy | sub_buy:
        query_2 = f"Insert Into Technologia (" \
            f"Plik, PO, Rysunek, OP_1, OP0, Status_Op, Komentarz, Stat, Liczba_Operacji, Kiedy" \
            f") VALUES (" \
            f"'{new_pdf}', '{new_pdf[0:7]}', '{new_pdf[8:]}', 'Kupowany', 'Kupowany', 1 ,'{komentarz}' ,0 ,1 ,'{now}'" \
            f");"
    else:
        query_2 = f"Insert Into Technologia (" \
            f"Plik, PO, Rysunek, Status_Op, Komentarz, Stat, Liczba_Operacji, Kiedy" \
            f") VALUES (" \
            f"'{new_pdf}', '{new_pdf[0:7]}', '{new_pdf[8:]}', 6 ,'{komentarz}' ,0 ,11 ,'{now}'" \
            f");"

    query = query_1 + query_2
    db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)
    return None


def update_rec(file):
    draw_id, former_bought, tech_made = check_db_buy(file)

    if (file.bought_cat or file.bought_name or file.sub_bought) and not former_bought:
        if tech_made:
            if not file.sub_bought:
                change_txt = 'Zmiana na zakupowy'
            else:
                change_txt = 'Zmiana na Część złożenia zakupowego'
        if not tech_made:
            if file.sub_bought:
                change_txt = 'Część złożenia zakupowego'
            else:
                change_txt = 'kupowany'

        # if updating made to bought
        query = f"UPDATE TECHNOLOGIA SET OP_1 = 'Kupowany', OP0 = 'Kupowany', OP1 = '', KOMENTARZ = '{change_txt}'," \
                f"OP_2 = '', OP_3 = '',OP_4 = '',OP_5 = '',OP_6 = '',OP_7 = '',OP_8 = '',OP_9 = '',OP_10 = ''," \
                f"MATERIAŁ = '', PRZYGOTÓWKA = '', CIĘCIA = '', STATUS_OP = 1, STAT = 0 WHERE ID = {draw_id};"
        db_commit(query, 'update_rec made to bought')
        merger_information(file, text=change_txt)
        return

    if not (file.bought_cat or file.bought_name) and former_bought:
        query = f"UPDATE TECHNOLOGIA SET OP_1 = '', OP0 = '', OP1 = '', KOMENTARZ = 'Zmiana na do zrobienia', " \
                f"STATUS_OP = 6, STAT = 0 WHERE ID = {draw_id};"
        db_commit(query, 'update_rec bought to made')
        wm.remove_watermark(file.file_name)  # added, not tested
        merger_information(file, text='zmiana na do zrobienia.')
        return


def merger_information(file, text):
    info_file_name = f'{file.po}__merge_info.txt'
    info_file = os.path.join(Paths.PRODUCTION, file.po, info_file_name)
    now = str(datetime.fromtimestamp(time.time(), ))[0:-7]
    if os.path.exists(info_file):
        with open(info_file, 'a', encoding='utf-8') as info:
            info.write(f'{now}  {file.file_name}: {text}\n')
    else:
        with open(info_file, 'w', encoding='utf-8') as info:
            info.write(f'{now}  {file.file_name}: {text}\n')
    return


def check_db_buy(file):
    query = f"SELECT ID, KOMENTARZ, Status_Op FROM TECHNOLOGIA WHERE PO ='{file.po}' AND Plik = '{file.file_name}';"
    with CURSOR:
        try:
            CURSOR.execute(query)
            register(query)
            result = CURSOR.fetchone()
            if result is None:
                return None, None, None
            else:
                rec_id, komentarz, status_op = result
        except Error:
            print(f'Database Error in "check_db_buy"')
            return None, None, None
    bought = komentarz in Options.BOUGHT_NAMES
    tech_done = int(status_op) != 6
    return rec_id, bought, tech_done


def del_empty_catalogs():
    for folder in catalogs_to_remove:
        os.chmod(folder, S_IWRITE)
        shutil.rmtree(folder, ignore_errors=True, )
    catalogs_to_remove.clear()


def cut_file_class(file):

    file.set_file_modifable()   # set file as modifiable
    file.create_catalog()       # Creating po folder if not exists
    file.set_available_name()   # Change name if file exists in PRODUCTION and is not replaced

    if os.path.exists(file.dest_catalog):
        if file.bought_cat | file.bought_name | file.sub_bought:
            try:
                os.rename(file.dest_path, file.dest_path)
            except PermissionError:
                print(f'{file.name} -- not stamped, permission error.')
                return
            except RuntimeError:
                print(f'{file.name} -- not stamped, runtime error.')
                return
            except FileNotFoundError:
                pass
            # print('stamping here')
            if not stamps_adder.stamper(file=file):
                return False
        else:
            try:
                file.move_file()
            except PermissionError:
                print(f'{file.name} -- not moved, permission error.')
                return False
    else:
        print(f'{file.name} -- not moved, There is no such Prod Order in Sap.')
        return False

    # if file has not been replaced, add it into database
    if not file.replace:
        new_rec(new_pdf=file.file_name,
                buy=(file.bought_name or file.bought_cat),
                sub_buy=file.sub_bought,
                order=file.po)
        return True
    else:
        update_rec(file)

    return True


def generate_end_path():
    number = 1
    path_to_check = os.path.join(Paths.START_CATALOG, f'bought_script')
    while os.path.isdir(path_to_check):
        path_to_check = os.path.join(Paths.START_CATALOG, f'bought_script_{number}')
        number += 1
    return path_to_check


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

    if 'merged' in name:
        return 'merged'

    if catalog:
        if catalog != name[0:7]:
            return False

    if name[7] != ' ':
        return False

    if not name[:6].isnumeric():
        return False

    if '--' in name:
        return False

    base_name, extension = name.rsplit('.', 1)

    if extension.lower() != 'pdf':
        return False

    if base_name.endswith('_99'):
        return False

    return base_name


def validate_file_class(file: File):

    """ If name is proper, returns True"""

    if re.search(r"\d{7} .*[.]*", file.new_name.lower()) is None:
        return False

    if file.extension.lower() not in Options.ACC_EXT:
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


def list_new_files_class():

    for item in os.listdir(Paths.START_CATALOG):

        deep_path = os.path.join(Paths.START_CATALOG, item)
        """ If path is not directory, and loose file are not forbidden."""
        if not os.path.isdir(deep_path) and Options.LOOSE_FILE_PERMISSION:
            file_handler(file_name=item)
            continue
        elif not os.path.isdir(deep_path):
            continue
        if os.path.isdir(deep_path):
            catalog_handler(item, path=())

    File.print_counter_status()
    File.set_counter_zero()
    pb_tracker.pumpblock_drawing_handler()  # Obsługa nowych rysunków na pump blocki


def file_handler(file_name, folder=None):

    if file_name in ['Thumbs.db', '_v']:
        return
    file = File(name=file_name, catalog=folder)
    if validate_file_class(file=file):
        cut_file_class(file=file)
    else:
        if new_bad_file(new_pdf=file.name, catalog=file.catalog):
            print(f'bad file: {file.file_name} in catalog: "4__Nowe_Rysunki/{file.catalog}"')
            File.add_bad_file()


def catalog_handler(name, path):
    catalog = Catalog(name, path)
    if catalog.quit_catalog():
        return
    for item in catalog.catalog_content():
        if not os.path.isdir(os.path.join(catalog.catalog_path, item)):
            file_handler(file_name=item, folder=catalog)
        else:
            catalog_handler(name=item, path=(path + (name,)))

    if not contains_pdfs(catalog=catalog) and catalog.ready:
        catalogs_to_remove.append(catalog.catalog_path)


def main():
    new_files_to_db()  # just SAP annotation
    truncate_bad_files()
    if Options.GENERAL_CHECK_PERMISSION and general_checker():
        teco_completer.main()
        list_new_files()
    elif not Options.GENERAL_CHECK_PERMISSION:
        list_new_files()
    list_new_files_class()
    merging()
    del_empty_catalogs()


if __name__ == '__main__':
    pass

