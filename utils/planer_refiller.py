from wms_main.const import *
from pyodbc import Error, DataError, OperationalError
import inspect

def main():
    query =f"SELECT * FROM UPDATE_PLANNER(); "
    try:
        CURSOR.execute(query)
        records = CURSOR.fetchall()
        if not records:
            return

    except Error:
        print('Connection to database failed.')
        return []
    except OperationalError:
        print('Operatinal Error.')
        return []
    except DataError:
        print('Data Error.')
        return []

    new_query = ''
    cntr = 0
    records = [[po, new_planner] for po, new_planner in records if new_planner is not None]
    for rec in records:
        po, new_planner = rec
        new_query = new_query + f"UPDATE SAP SET [Planista 0] = '{new_planner}' WHERE [P.O.] = '{po}'; "
        cntr += 1
        if cntr == 10:
            db_commit(new_query, inspect.currentframe())
            cntr = 0
            new_query = ''
    if new_query:
        db_commit(new_query, inspect.currentframe())


if __name__ == '__main__':
    main()

