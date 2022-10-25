from datetime import datetime
import time
from const import CURSOR


def update(column):
    now = str(datetime.fromtimestamp(time.time(), ))[0:-7]
    query = f"Update SAP_Data SET {column} = '{now}';"

    with CURSOR:
        CURSOR.execute(query)
        CURSOR.commit()


def main():
    pass


if __name__ == '__main__':
    main()
