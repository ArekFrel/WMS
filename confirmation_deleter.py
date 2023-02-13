import csv
import os
import os.path
from const import CURSOR, RAPORT_CATALOG


def delete_confirmation():
    print('Confirmation Delete started.')
    sap_delete_file = os.path.join(RAPORT_CATALOG, "SAP_DELETE.csv")
    with open(sap_delete_file, encoding='utf-8-sig') as file:
        i = 0
        for record in file:
            if len(record.strip()) == 0:
                continue
            conf_no = int(record)
            delete_in_db(number=conf_no)
            i += 1

    print(f'{i} records Deleted')


def get_confirmation_from_db():
    query = 'SELECT DISTINCT Confirmation FROM Sap;'
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
