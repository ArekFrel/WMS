from datetime import datetime
import time
from const import db_commit


def update(column):
    now = str(datetime.fromtimestamp(time.time(), ))[0:-7]
    query = f"Update SAP_Data SET {column} = '{now}';"
    db_commit(query=query, func_name=update.__name__)


def main():
    pass


if __name__ == '__main__':
    main()
