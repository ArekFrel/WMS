import csv
import inspect
import os
import os.path
from wms_main import sap_date
from utils import confirmation_deleter
from wms_main.const import CURSOR, Paths, db_commit, so_list_getter
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
            print(f'Records sent to database: {index + 1}', end="\r")
            query_counter += 1
            if query_counter == 50:
                if db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
                    query = ''
                    query_counter = 0
                else:
                    print('\nUnexpected error occurs during updating SAP.')
                    return False
        if query_counter != 0:
            if db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
                pass
            else:
                print('\nUnexpected error occurs during updating SAP.')
                return False

        print('\n', end='\r')
    return True


def upload_new_items():
    print('Uploading new Items')
    item_insert_file = os.path.join(Paths.RAPORT_CATALOG, "ITEM_INSERT.csv")
    with open(item_insert_file) as file:
        changed_records = csv.reader(file)
        i = 0
        for record in changed_records:
            if send_item_to_db(record=record):
                i += 1
                print(f'Items sent to database: {i}', end="\r")
            else:
                break
        print('\n', end='\r')


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

        # query = f"Delete from {table} WHERE Confirmation = {confirmation}; "\
        #         f"Insert into dbo.{table} ([S.O.],[Obiekt],[P.O.],[Start P.O.],[Finish P.O.],[Ilość],[Urządzenie],[Brygada]," \
        #         f"[Nr Op],[Operacja],[Start Op],[Finish Op],[Czas Plan],[Czas Raport],[Opis],[Create],[Planista 0]," \
        #         f"[Ostatnia Zmiana],[Planista 1],[Release Aktualny],[Release Plan],[Network],[System Status]," \
        #         f"[Confirmation],[Start P.O. Aktualny],[Finish P.O. Aktualny],[Start Op Aktualny],[Finish Op Aktualny]," \
        #         f"[Urządzenie Główne], [System Status Full]) " \
        #         f"VALUES('{so}','{obiekt}','{po}',{start_po},{finish_po},'{ilosc}','{urzadzenie}','{brygada}',"\
        #         f"'{nr_op}','{operacja}',{start_op},{finish_op},'{czas_plan}','{czas_raport}','{opis}',{create},"\
        #         f"'{planista_0}',{ostatnia_zmiana},'{planista_1}',{release_aktualny},"\
        #         f"{release_plan},'{network}','{system_status}','{confirmation}',{start_po_aktualny}," \
        #         f"{finish_po_aktualny},{start_op_aktualny},{finish_op_aktualny},'{urzadzenie_glowne}','{system_status_full}')"
    else:
        query = ''
    return query


def status_select(stat: str) -> str:
    if 'CNF' in stat and 'PCNF' not in stat:
        return "TECO"
    else:
        return stat.split(' ')[-1]


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

    if record[1] != '':
        if record[0] == '0':
            item = 'NULL'
        else:
            item = record[0]
        prod_order = int(record[1])
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


def uploader_item_checker():
    item_insert_path = os.path.join(Paths.RAPORT_CATALOG, 'ITEM_INSERT.csv')
    if os.path.exists(item_insert_path):
        item_insert_date = os.path.getmtime(item_insert_path)

        query = 'SELECT Item_Data FROM SAP_data;'
        if not db_commit(query=query, func_name=inspect.currentframe().f_code.co_name):
            return False
        result = CURSOR.execute(query)

        for date_time in result:
            item_db_date = date_time[0].timestamp()
            if item_insert_date > item_db_date:
                return True
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


def main():
    if uploader_checker():
        if upload_new_data():
            so_folder_creator()
            po_pumpblock_recorder()  # identyfikacja nowych zleceń na pump blocki
            sap_date.update(column='SAP_Skrypt_zmiana')
        else:
            return False
        confirmation_deleter.delete_confirmation()
    else:
        print('No new data uploaded.')

    if uploader_item_checker():
        upload_new_items()
        sap_date.update(column='Item_Data')
        print('New Items uploaded')

    """UNREM if you need too update system Status"""
    # update_system_status()

    return True


if __name__ == '__main__':
    # upload_new_data()
    pass
    # so_folder_creator()

