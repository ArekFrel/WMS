import csv
import os
import os.path
from quote_dict import list_of_operations
from const import CURSOR, Paths
from pyodbc import DatabaseError, OperationalError
from timer_dec import timer


def upload_quotation():
    quot_files = [os.path.join(Paths.RAPORT_CATALOG, file) for file in os.listdir(Paths.RAPORT_CATALOG) if file.startswith('SAP_QUOT')]
    for quot_file in quot_files:
        with open(quot_file) as file:
            changed_records = csv.reader(file)
            for index, record in enumerate(changed_records, start=1):
                if index % 2 == 0:
                    send_quotation(record=record)
        os.remove(quot_file)
    return True


def send_quotation(record):
    drawing_number = record.pop(0)
    query_update = ''
    query_insert = 'BEGIN\nINSERT INTO Quotation (drawing_number, '
    query_values = f"VALUES ('{drawing_number}', "
    pairs = zip(list_of_operations, record[5:])
    query = f"If Exists (Select 1 From Quotation Where drawing_number = '{drawing_number}')\n" \
            f"Begin\n" \
            f"Update Quotation\n" \
            f"SET "
    for operation, quote in pairs:
        if int(quote) != 0:
            if len(query_update) == 0:
                query_update = f"{operation} = {quote}"
                query_insert = query_insert + f"{operation}"
                query_values = query_values + f"{quote}"
            else:
                query_update = query_update + f", {operation} = {quote}"
                query_insert = query_insert + f", {operation}"
                query_values = query_values + f", {quote}"

    query_update = query_update + f"\nWHERE drawing_number = '{drawing_number}'\n END\nELSE\n"
    query_insert = query_insert + ")\n"
    query_values = query_values + ")\n END;"
    query = query + query_update + query_insert + query_values

    with CURSOR:
        try:
            CURSOR.execute(query)
            CURSOR.commit()

        except OperationalError:
            print('Unknown Error')
            return False

        except DatabaseError:
            print('Time exceeded')
            return False


# @timer
def main():
    if 'SAP_QUOT.csv' in os.listdir(Paths.RAPORT_CATALOG):
        upload_quotation()


if __name__ == '__main__':
    main()
