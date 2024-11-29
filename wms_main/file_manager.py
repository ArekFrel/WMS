import inspect
import os
from wms_main.const import Paths, db_commit
from datetime import datetime

s_ins = 'sap_insert.csv'
s3 = 'sap3.xlsx'
s3old = 'sap3_old.xlsx'
s7 = 'sap7_all.xlsx'
s7old = 'sap7_all_old.xlsx'
i_ins = 'item_insert.csv'


def manage_files():
    cat_con = {x.lower() for x in os.listdir(Paths.RAPORT_CATALOG)}
    # if s_ins in cat_con and s3 in cat_con and s3old in cat_con:
    if {s_ins, s3, s3old}.issubset(cat_con):
        sap_insert_path = os.path.join(Paths.RAPORT_CATALOG, s_ins)
        sap_path = os.path.join(Paths.RAPORT_CATALOG, s3)
        sap_insert_date = os.path.getmtime(sap_insert_path)
        sap_date = os.path.getmtime(sap_path)

        if sap_insert_date > sap_date:
            sap_script_date(date=sap_date)
            if remove_old():
                rename_new()

    if s_ins not in cat_con and s3old not in cat_con or s3old not in cat_con:
        rename_new()

    if i_ins in cat_con and s7 in cat_con and s7old in cat_con:

        item_insert_path = os.path.join(Paths.RAPORT_CATALOG, i_ins)
        item_path = os.path.join(Paths.RAPORT_CATALOG, s7)
        item_insert_date = os.path.getmtime(item_insert_path)
        item_date = os.path.getmtime(item_path)

        if item_insert_date > item_date:
            item_script_date(date=item_date)
            if remove_item_old():
                rename_new_item()

    if i_ins.lower() not in cat_con and s7old.lower() not in cat_con or s7old.lower() not in cat_con:
        rename_new_item()


def remove_old():
    files = ['SAP1', 'SAP2', 'SAP3', 'SAP1_old', 'SAP2_old', 'SAP3_old']
    if not files_permitted(files=files):
        return False
    files = ['SAP1_old', 'SAP2_old', 'SAP3_old']
    for s_old in files:
        file_to_delete = os.path.join(Paths.RAPORT_CATALOG, s_old + '.xlsx')
        os.remove(file_to_delete)
    print('SAP_old files removed.')
    return True


def remove_item_old():
    files = ['SAP7_ALL', 'SAP7_ALL_old']
    if not files_permitted(files=files):
        return False
    files = ['SAP7_ALL_old']
    for s_old in files:
        file_to_delete = os.path.join(Paths.RAPORT_CATALOG, s_old + '.xlsx')
        os.remove(file_to_delete)
    print('SAP7_ALL_old files removed.')
    return True


def rename_new():
    files = ['SAP1', 'SAP2', 'SAP3']
    if files_permitted(files=files):
        for file in files:
            file_to_rename = os.path.join(Paths.RAPORT_CATALOG, file + '.xlsx')
            new_name = os.path.join(Paths.RAPORT_CATALOG, file + '_old.xlsx')
            os.rename(file_to_rename, new_name)
        print('SAP files renamed into SAP_old.')


def rename_new_item():
    file = 'SAP7_All'
    if file_permitted(file=file):
        file_to_rename = os.path.join(Paths.RAPORT_CATALOG, file + '.xlsx')
        new_name = os.path.join(Paths.RAPORT_CATALOG, file + '_old.xlsx')
        os.rename(file_to_rename, new_name)
    print('SAP7_ALL file renamed into SAP7_ALL_old.')


def sap_script_date(date):

    date = str(datetime.fromtimestamp(date, ))[0:-3]
    query = f"Update Sap_data Set SAP_Skrypt = '{date}';"
    db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)
    print(f'SAP_Skrypt in DataBase updated to {date[0:-3]}')


def item_script_date(date):

    date = str(datetime.fromtimestamp(date, ))[0:-3]
    query = f"UPDATE Sap_data SET Item_Data = '{date}';"
    db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)
    print(f'Item_data in DataBase updated to {date[0:-3]}')


def files_permitted(files):
    COL_START = '\33[91m'
    COL_END = '\033[0m'
    for name in files:
        try:
            file = os.path.join(Paths.RAPORT_CATALOG, name + '.xlsx')
            os.rename(file, file)
        except PermissionError:
            print(COL_START + f'{name} report is opened!' + COL_END)
            return False
        except FileNotFoundError:
            print(COL_START + f'{name}  file not found.' + COL_END)
            return False
    return True


def file_permitted(file):
    try:
        file = os.path.join(Paths.RAPORT_CATALOG, file + '.xlsx')
        os.rename(file, file)
    except PermissionError:
        print(f'{file} report is opened!')
        return False
    except FileNotFoundError:
        print(f'{file}  file not found.')
        return False
    return True


def main():
    manage_files()


if __name__ == '__main__':
    main()
