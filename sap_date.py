from datetime import datetime
import time

import pyodbc

from const import CURSOR
from pyodbc import DatabaseError, OperationalError


def update(column):
    now = str(datetime.fromtimestamp(time.time(), ))[0:-7]
    query = f"Update SAP_Data SET {column} = '{now}';"

    with CURSOR:
        try:
            CURSOR.execute(query)
            CURSOR.commit()

        except OperationalError:
            print('Operational Error Error')
            return False

        except DatabaseError:
            print('Time exceeded')
            return False

        except pyodbc.Error:
            print('Database Error')
            return False


def main():
    pass


if __name__ == '__main__':
    main()
