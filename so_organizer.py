import pyodbc
import os
from const import CONN, CURSOR , Paths


def initial_sctructure():
    catalog_creator()


def so_list_getter():
    query = "SELECT DISTINCT CONCAT([S.O.], ' ', [urządzenie Główne]) FROM SAP WHERE [S.O.] != 0"
    result = []
    try:
        CURSOR.execute(query)
        result = [str(val[0]) for val in CURSOR.fetchall()]
    except pyodbc.Error:
        print('Connection to database failed.')
        return []
    return result


def catalog_creator():
    so_list = so_list_getter()
    for so in so_list:
        dest_path = os.path.join(Paths.MODELS_CATALOG, so)
        if not os.path.exists(dest_path):
            os.mkdir(dest_path)
            print(f'{dest_path} - has been created.')
            continue
        else:
            print(f'{dest_path} - already exists.')


def main():
    initial_sctructure()


if __name__ == '__main__':
    main()

