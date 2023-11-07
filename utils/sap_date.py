from datetime import datetime
import inspect
import time
from const import db_commit


def update(column):
    now = str(datetime.fromtimestamp(time.time(), ))[0:-7]
    query = f"Update SAP_Data SET {column} = '{now}';"
    func_name = inspect.currentframe().f_code.co_name

    db_commit(query=query, func_name=func_name)


def main():
    pass


if __name__ == '__main__':
    main()
