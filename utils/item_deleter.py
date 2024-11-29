import os
import os.path
from wms_main.const import CURSOR, Paths


def delete_item():
    print('Item Delete started.')
    item_delete_file = os.path.join(Paths.RAPORT_CATALOG, "ITEM_DELETE.csv")
    with open(item_delete_file, encoding='utf-8-sig') as file:
        i = 0
        for record in file:
            if len(record.strip()) == 0:
                continue
            prod_ord_no = record.strip().split(',')[1]
            delete_item_db(number=int(prod_ord_no))
            i += 1

    print(f'{i} Item Deleted')


def get_confirmation_from_db():
    query = 'SELECT DISTINCT Confirmation FROM Sap;'
    result = CURSOR.execute(query)
    current_db_conf = []

    for conf_no in result:
        current_db_conf.append(conf_no[0])

    return current_db_conf


def delete_item_db(number):
    query = f"DELETE FROM Items WHERE Prod_Order = {number}"
    with CURSOR:
        CURSOR.execute(query)
        CURSOR.commit()
    return None


def main():
    delete_item()


if __name__ == '__main__':
    main()
