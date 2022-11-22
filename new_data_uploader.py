import csv
import os
import os.path
import sap_date
from const import CURSOR, RAPORT_CATALOG


def upload_new_data():
    print('Refreshing SAP DataBase.')
    sap_insert_file = os.path.join(RAPORT_CATALOG, "SAP_INSERT.csv")
    with open(sap_insert_file) as file:
        changed_records = csv.reader(file)
        i = 0
        for record in changed_records:
            if send_record_to_db(record=record):
                i += 1
                print(f'Records sent to database: {i}', end="\r")
        print('\n', end='\r')


def redate(date):
    if not len(date):
        return 'Null'

    month, day, year = date.split('/')
    month = f'{month:0>2}'
    day = f'{day:0>2}'
    new_date = f"'{year}-{month}-{day}'"
    return new_date


def send_record_to_db(record):
    table = 'SAP'

    if record[23] != '':
        so = record[0]
        obiekt = record[1]
        po = record[2]
        start_po = redate(record[3])
        finish_po = redate(record[4])
        ilosc = record[5]
        urzadzenie = record[6]
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
        system_status = record[22]
        confirmation = record[23]
        start_po_aktualny = redate(record[24])
        finish_po_aktualny = redate(record[25])
        start_op_aktualny = redate(record[26])
        finish_op_aktualny = redate(record[27])
        urzadzenie_główne = record[28]

        query = f"Delete from {table} WHERE Confirmation = {confirmation}; "\
                f"Insert into dbo.{table} ([S.O.],[Obiekt],[P.O.],[Start P.O.],[Finish P.O.],[Ilość],[Urządzenie],[Brygada]," \
                f"[Nr Op],[Operacja],[Start Op],[Finish Op],[Czas Plan],[Czas Raport],[Opis],[Create],[Planista 0]," \
                f"[Ostatnia Zmiana],[Planista 1],[Release Aktualny],[Release Plan],[Network],[System Status]," \
                f"[Confirmation],[Start P.O. Aktualny],[Finish P.O. Aktualny],[Start Op Aktualny],[Finish Op Aktualny]," \
                f"[Urządzenie Główne]) " \
                f"VALUES('{so}','{obiekt}','{po}',{start_po},{finish_po},'{ilosc}','{urzadzenie}','{brygada}',"\
                f"'{nr_op}','{operacja}',{start_op},{finish_op},'{czas_plan}','{czas_raport}','{opis}',{create},"\
                f"'{planista_0}',{ostatnia_zmiana},'{planista_1}',{release_aktualny},"\
                f"{release_plan},'{network}','{system_status}','{confirmation}',{start_po_aktualny}," \
                f"{finish_po_aktualny},{start_op_aktualny},{finish_op_aktualny},'{urzadzenie_główne}')"

        CURSOR.execute(query)
        CURSOR.commit()
        return True
    return False


def uploader_checker():
    sap_insert_path = os.path.join(RAPORT_CATALOG, 'SAP_INSERT.csv')
    if not os.path.exists(sap_insert_path):
        sap_insert_date = os.path.getmtime(sap_insert_path)

        query = 'Select SAP_Skrypt_Zmiana From SAP_data;'
        result = CURSOR.execute(query)

        for date_time in result:
            sap_db_date = date_time[0].timestamp()
            if sap_insert_date > sap_db_date:
                return True

    return False


def main():
    if uploader_checker():
        upload_new_data()
        sap_date.update(column='SAP_Skrypt_zmiana')
    else:
        print('No new data uploaded.')


if __name__ == '__main__':
    # main()
    uploader_checker()
