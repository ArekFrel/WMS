import csv
import os
import os.path
from const import CURSOR, RAPORT_CATALOG


def delete_confirmation_old():
    print('Confirmation Delete started.')
    sap_delete_file = os.path.join(RAPORT_CATALOG, "SAP_DELETE.csv")
    with open(sap_delete_file, encoding='utf-8') as file:
        good_records = []
        for record in csv.reader(file):
            conf_no = record[0]
            delete_in_db(number=conf_no)
            good_records.append(int(record[0]))

        i = 0
        current_db_conf = get_confirmation_from_db()
        for conf_no in current_db_conf:
            if conf_no not in good_records:
                delete_in_db(number=conf_no)
                i += 1
        print(f'{i} records Deleted')


def delete_confirmation():
    print('Confirmation Delete started.')
    sap_delete_file = os.path.join(RAPORT_CATALOG, "SAP_DELETE.csv")
    with open(sap_delete_file, encoding='utf-8') as file:
        i = 0
        for record in csv.reader(file):
            if len(record) == 0:
                break
            conf_no = int(record[0])
            delete_in_db(number=conf_no)
            i += 1

    print(f'{i} records Deleted')


def get_confirmation_from_db():
    query = 'Select Distinct Confirmation from Sap;'
    result = CURSOR.execute(query)
    current_db_conf = []

    for conf_no in result:
        current_db_conf.append(conf_no[0])

    return current_db_conf


def delete_in_db(number):
    query = f"DELETE FROM sap WHERE Confirmation = {number}"
    # print(query)
    with CURSOR:
        CURSOR.execute(query)
        CURSOR.commit()
    return None


def main():
    delete_confirmation()


if __name__ == '__main__':
    main()
