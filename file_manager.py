import os
from const import CURSOR
from const import RAPORT_CATALOG
from datetime import datetime

s_ins = 'SAP_INSERT.csv'
s3 = 'SAP3.xlsx'
s3old = 'SAP3_old.xlsx'


def manage_files():

    cat_con = os.listdir(RAPORT_CATALOG)

    if s_ins in cat_con and s3 in cat_con and s3old in cat_con:

        sap_insert_path = os.path.join(RAPORT_CATALOG, s_ins)
        sap_path = os.path.join(RAPORT_CATALOG, s3)
        sap_insert_date = os.path.getmtime(sap_insert_path)
        sap_date = os.path.getmtime(sap_path)

        if sap_insert_date > sap_date:
            sap_script_date(date=sap_date)
            if remove_old():
                rename_new()

    if s_ins not in cat_con and s3old not in cat_con or s3old not in cat_con:
        rename_new()


def remove_old():
    files = ['SAP1', 'SAP2', 'SAP3', 'SAP1_old', 'SAP2_old', 'SAP3_old']
    if not files_permitted(files=files):
        return False
    files = ['SAP1_old', 'SAP2_old', 'SAP3_old']
    for s_old in files:
        file_to_delete = os.path.join(RAPORT_CATALOG, s_old + '.xlsx')
        os.remove(file_to_delete)
    print('SAP_old files removed.')
    return True


def rename_new():
    files = ['SAP1', 'SAP2', 'SAP3']
    if files_permitted(files=files):
        for file in files:
            file_to_rename = os.path.join(RAPORT_CATALOG, file + '.xlsx')
            new_name = os.path.join(RAPORT_CATALOG, file + '_old.xlsx')
            os.rename(file_to_rename, new_name)
        print('SAP files renamed into SAP_old.')


def sap_script_date(date):

    date = str(datetime.fromtimestamp(date, ))[0:-3]
    query = f"Update Sap_data Set SAP_Skrypt = '{date}';"
    with CURSOR:
        CURSOR.execute(query)
        CURSOR.commit()
    print(f'SAP_Skrypt in DataBase updated to {date[0:-3]}')


def files_permitted(files):
    for name in files:
        try:
            file = os.path.join(RAPORT_CATALOG, name + '.xlsx')
            os.rename(file, file)
        except PermissionError:
            print(f'{name} report is opened!')
            return False
        except FileNotFoundError:
            print(f'{name}  file not found.')
            return False
    return True


def main():
    manage_files()


if __name__ == '__main__':
    main()
