import csv
import inspect
import os
import os.path
from datetime import datetime
from wms_main.const import TimeConsts, Paths
from wms_main import sap_date
from utils import confirmation_deleter, item_deleter, item_handler, planer_refiller
from wms_main.const import CURSOR, Paths, db_commit, so_list_getter, db_commit_getval
from utils.pump_block_tracker.pb_tracker import po_pumpblock_recorder


def upload_new_data():
    print('Refreshing SAP DataBase.')
    sap_insert_file = os.path.join(Paths.RAPORT_CATALOG, "SAP_INSERT.csv")
    with open(sap_insert_file) as file:
        changed_records = csv.reader(file)
        query = ''
        query_counter = 0
        for index, record in enumerate(changed_records):
            if index == 0:
                if ''.join(record) == '':
                    print(f'SAP_Insert file is empty.')
                    break
            query = query + formulate_query_record(record=record)
            query_counter += 1
            if query_counter == 50:
                if db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
                    print(f'Records sent to database: {index + 1}', end="\r")
                    query = ''
                    query_counter = 0
                else:
                    print('\nUnexpected error occurs during updating SAP.')
                    return False
        if query_counter != 0:
            if db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
                print(f'Records sent to database: {index + 1}', end="\r")
            else:
                print('\nUnexpected error occurs during updating SAP.')
                return False
        print('\n', end='\r')
    return True


def upload_new_items():
    item_insert_file = Paths.II_FILE
    with open(item_insert_file) as file:
        changed_records = list(csv.reader(file))
        i = 0
        query = ''
        try:
            if not changed_records[0]:
                return True
        except IndexError:
            return True

        print('Uploading new Items')
        for record in changed_records:
            po, item = record
            query = query + f"Delete from dbo.Items  WHERE Prod_Order = '{po}' "
            query = query + f"INSERT INTO dbo.Items (Prod_Order, Item) VALUES('{po}','{item}') "
            i += 1
            if i % 50 == 0:
                if db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
                    query = ''
                    print(f'Items sent to database: {i}', end="\r")
                else:
                    return False
        if query:
            if db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
                print(f'Items sent to database: {i}')
            else:
                return False
        return True




def redate(date):
    if not len(date):
        return 'Null'

    month, day, year = date.split('/')
    month = f'{month:0>2}'
    day = f'{day:0>2}'
    new_date = f"'{year}-{month}-{day}'"
    return new_date


def formulate_query_record(record):
    table = 'SAP'

    if len(record) < 29:
        for i in range(0, (29 - len(record))):
            record.append('')

    if record[23] != '':
        so = record[0]
        obiekt = record[1]
        po = record[2]
        start_po = redate(record[3])
        finish_po = redate(record[4])
        ilosc = record[5]
        urzadzenie = slash_remover(str(record[6]))
        brygada = record[7]
        nr_op = record[8]
        operacja = record[9]
        start_op = redate(record[10])
        finish_op = redate(record[11])
        czas_plan = record[12]
        czas_raport = record[13]
        opis = record[14]
        create = redate(record[15])
        planista_0 = record[16]
        ostatnia_zmiana = redate(record[17])
        planista_1 = record[18]
        release_aktualny = redate(record[19])
        release_plan = redate(record[20])
        network = record[21]
        system_status = status_select(record[22])
        confirmation = record[23]
        start_po_aktualny = redate(record[24])
        finish_po_aktualny = redate(record[25])
        start_op_aktualny = redate(record[26])
        finish_op_aktualny = redate(record[27])
        urzadzenie_glowne = slash_remover(str(record[28]))
        system_status_full = record[22]

        # zmiana kwerendy na MERGE

        query = f"MERGE INTO {table} As target " \
                f"USING (" \
                f"VALUES('{so}', '{obiekt}', '{po}', {start_po}, {finish_po}, '{ilosc}', '{urzadzenie}', '{brygada}', "\
                f"'{nr_op}', '{operacja}', {start_op}, {finish_op}, '{czas_plan}', '{czas_raport}', '{opis}', {create}, "\
                f"'{planista_0}', {ostatnia_zmiana}, '{planista_1}', {release_aktualny}, "\
                f"{release_plan}, '{network}', '{system_status}', '{confirmation}', {start_po_aktualny}," \
                f"{finish_po_aktualny}, {start_op_aktualny}, {finish_op_aktualny}, " \
                f"'{urzadzenie_glowne}', '{system_status_full}')) " \
                f"AS source ([S.O.],[Obiekt],[P.O.],[Start P.O.],[Finish P.O.],[Ilość],[Urządzenie],[Brygada]," \
                f"[Nr Op],[Operacja],[Start Op],[Finish Op],[Czas Plan],[Czas Raport],[Opis],[Create],[Planista 0]," \
                f"[Ostatnia Zmiana],[Planista 1],[Release Aktualny],[Release Plan],[Network],[System Status]," \
                f"[Confirmation],[Start P.O. Aktualny],[Finish P.O. Aktualny],[Start Op Aktualny]," \
                f"[Finish Op Aktualny],[Urządzenie Główne], [System Status Full])" \
                f"ON target.Confirmation = source.Confirmation " \
                f"WHEN MATCHED THEN " \
                f"UPDATE SET " \
                f"target.[S.O.] = source.[S.O.], " \
                f"target.[Obiekt] = source.[Obiekt], " \
                f"target.[P.O.] = source.[P.O.], " \
                f"target.[Start P.O.] = source.[Start P.O.], " \
                f"target.[Finish P.O.] = source.[Finish P.O.], " \
                f"target.[Ilość] = source.[Ilość], " \
                f"target.[Urządzenie] = source.[Urządzenie], " \
                f"target.[Brygada] = source.[Brygada], " \
                f"target.[Nr Op] = source.[Nr Op], " \
                f"target.[Operacja] = source.[Operacja], " \
                f"target.[Start Op] = source.[Start Op], " \
                f"target.[Finish Op] = source.[Finish Op], " \
                f"target.[Czas Plan] = source.[Czas Plan], " \
                f"target.[Czas Raport] = source.[Czas Raport], " \
                f"target.[Opis] = source.[Opis], " \
                f"target.[Create] = source.[Create], " \
                f"target.[Planista 0] = source.[Planista 0], " \
                f"target.[Ostatnia Zmiana] = source.[Ostatnia Zmiana], " \
                f"target.[Planista 1] = source.[Planista 1], " \
                f"target.[Release Aktualny] = source.[Release Aktualny], " \
                f"target.[Release Plan] = source.[Release Plan], " \
                f"target.[Network] = source.[Network], " \
                f"target.[System Status] = source.[System Status], " \
                f"target.[Confirmation] = source.[Confirmation], " \
                f"target.[Start P.O. Aktualny] = source.[Start P.O. Aktualny], " \
                f"target.[Finish P.O. Aktualny] = source.[Finish P.O. Aktualny], " \
                f"target.[Start Op Aktualny] = source.[Start Op Aktualny], " \
                f"target.[Finish Op Aktualny] = source.[Finish Op Aktualny], " \
                f"target.[Urządzenie Główne] = source.[Urządzenie Główne], " \
                f"target.[System Status Full] = source.[System Status Full] " \
                f"WHEN NOT MATCHED BY TARGET THEN " \
                f"INSERT ([S.O.],[Obiekt],[P.O.],[Start P.O.],[Finish P.O.],[Ilość],[Urządzenie],[Brygada],[Nr Op]," \
                f"[Operacja],[Start Op],[Finish Op],[Czas Plan],[Czas Raport],[Opis]," \
                f"[Create],[Planista 0],[Ostatnia Zmiana],[Planista 1],[Release Aktualny],[Release Plan]," \
                f"[Network],[System Status],[Confirmation],[Start P.O. Aktualny],[Finish P.O. Aktualny]," \
                f"[Start Op Aktualny],[Finish Op Aktualny],[Urządzenie Główne],[System Status Full])" \
                f"VALUES (source.[S.O.], source.[Obiekt],source.[P.O.], source.[Start P.O.], source.[Finish P.O.], " \
                f"source.[Ilość], source.[Urządzenie],   source.[Brygada], source.[Nr Op], source.[Operacja], " \
                f"source.[Start Op], source.[Finish Op], source.[Czas Plan], source.[Czas Raport],   source.[Opis], " \
                f"source.[Create], source.[Planista 0], source.[Ostatnia Zmiana], source.[Planista 1], " \
                f"source.[Release Aktualny],   source.[Release Plan], source.[Network], source.[System Status], " \
                f"source.[Confirmation], source.[Start P.O. Aktualny], source.[Finish P.O. Aktualny], " \
                f"source.[Start Op Aktualny], source.[Finish Op Aktualny], " \
                f"source.[Urządzenie Główne], source.[System Status Full]); "

    else:
        query = ''
    return query


def status_select(stat: str) -> str:
    if 'CNF' in stat and 'PCNF' not in stat:
        return "TECO"
    for _ in ('DSPT', 'DSEX', 'EXPL', 'EXTS'):
        if _ in stat:
            stat = stat.replace(_, '')
    while '  ' in stat:
        stat = stat.replace('  ', ' ')
    else:
        return stat.rstrip().split(' ')[-1]


def update_status(record):

    table = 'SAP'
    confirmation = record[0]
    system_status_full = record[1]
    query = f"UPDATE {table} SET [System Status Full] = '{system_status_full}' WHERE Confirmation = '{confirmation}';"

    if db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
        return True
    else:
        return False


def send_item_to_db(record):

    table = 'Items'
    if len(record) < 2:
        for i in range(0, (2 - len(record))):
            record.append('')


    if record[0] != '':
        if record[1] == '0':
            item = 'NULL'
        else:
            item = record[1]
        prod_order = int(record[0])
        query = f"DELETE FROM {table} WHERE Prod_Order = {prod_order}; "\
                f"INSERT INTO dbo.{table} (Prod_Order, Item) " \
                f"VALUES({prod_order},{item})"
        return db_commit(query=query, func_name=inspect.currentframe().f_code.co_name)


def so_folder_creator():
    current_list = os.listdir(Paths.MODELS_CATALOG)
    db_list = so_list_getter()
    list_to_create = [so for so in db_list if so not in current_list]
    if list_to_create:
        for so in list_to_create:
            dest_path = os.path.join(Paths.MODELS_CATALOG, so)
            os.mkdir(dest_path)
            print(f'{so} -- has been created.')


def slash_remover(string):
    forbidden = ['\\', '/']
    removeable = [':', '*', '?', '"', '<', '>', '|']
    for sign in forbidden:
        string = string.replace(sign, '_')
    for sign in removeable:
        string = string.replace(sign, '')
    if string.endswith('.'):
        string = string[0:-1]
    return string.rstrip()


def planer_seek(po_num, planer):
    if planer != '':
        return planer
    found_planer = db_commit_getval(
        f"Select distinct [Planista 0] from SAP where [P.O.] = {po_num} and [planista 0] != '';"
    )
    if found_planer:
        return found_planer
    return ''


def uploader_checker():
    sap_insert_path = os.path.join(Paths.RAPORT_CATALOG, 'SAP_INSERT.csv')
    if os.path.exists(sap_insert_path):
        sap_insert_date = os.path.getmtime(sap_insert_path)
        query = 'SELECT SAP_Skrypt_Zmiana FROM SAP_data;'
        if not db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
            return False

        result = CURSOR.execute(query)

        for date_time in result:
            sap_db_date = date_time[0].timestamp()
            if sap_insert_date > sap_db_date:
                return True

    return False


def item_files_delete():
    if os.path.exists(Paths.II_FILE):
        os.remove(Paths.II_FILE)
    if os.path.exists(Paths.ID_FILE):
        os.remove(Paths.ID_FILE)


def uploader_item_checker():

    query = "SELECT Item_data from sap_data;"
    CURSOR.execute(query)
    r = CURSOR.fetchval()
    if r < datetime.fromtimestamp((os.path.getmtime(Paths.IR_FILE))):
        return True
    else:
        return False



def update_system_status():
    print('Uploading System status')
    status_file = os.path.join(Paths.RAPORT_CATALOG, "SAP_INSERT_SSC.csv")
    with open(status_file) as file:
        records = csv.reader(file)
        i = 0
        for record in records:
            if update_status(record=record):
                i += 1
                print(f'Records sent to database: {i}', end="\r")
            else:
                print(f'sent {i}')
                break
        print('\n', end='\r')


def update_wms_table():
    query = "SELECT DATEDIFF(MINUTE, wms_table_update, GETDATE()) FROM sap_data;"
    CURSOR.execute(query)
    COL_START = '\033[95m'
    COL_END = '\033[0m'
    if CURSOR.fetchval() > TimeConsts.PUT - 1:
        print(f'{COL_START}Updating wms_table for planners{COL_END}')
        CURSOR.execute("EXECUTE [dbo].[wms_TABLE_update]")
        sap_date.update(column='wms_table_update')



def main():
    if uploader_checker():
        if upload_new_data():
            planer_refiller.main()
            so_folder_creator()
            po_pumpblock_recorder()  # identyfikacja nowych zleceń na pump blocki
            sap_date.update(column='SAP_Skrypt_zmiana')
        else:
            return False
        confirmation_deleter.delete_confirmation()
    else:
        print('No new data uploaded.')

    if uploader_item_checker():
        proceed = item_handler.main()
        if proceed:
            proceed = upload_new_items()
        else:
            return False
        if proceed:
            proceed = item_deleter.main()
        if proceed:
            item_files_delete()
        sap_date.update(column='Item_Data')
        print('New Items uploaded')

    update_wms_table()

    """UNREM if you need too update system Status"""
    # update_system_status()

    return True


if __name__ == '__main__':
    pass
    # uploader_item_checker()