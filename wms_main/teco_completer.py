import inspect
from .const import CURSOR, db_commit, register, TimeConsts
from pyodbc import OperationalError, DatabaseError, Error


def get_data():

    func_name = inspect.currentframe().f_code.co_name
    try:
        with CURSOR:
            query = "SELECT PO, Fin_date FROM [dbo].[Teco_not_completed]()"
            CURSOR.execute(query)
            records = CURSOR.fetchall()
            return records

    except OperationalError:
        print_red(f'Operational Error in "{func_name}"')
        return False

    except DatabaseError:
        print_red(f'Time exceeded in "{func_name}"')
        return False

    except Error:
        print_red(f'Database Error in "{func_name}"')
        return False

    except Exception:
        print_red(f'Something else during "{func_name}" gone wrong!')
        return False


def print_red(text):
    COL_START = '\33[91m'
    COL_END = '\033[0m'
    print(COL_START + f'{text}' + COL_END)
    register(text)


def last_drawing(po_number):
    func_name = inspect.currentframe().f_code.co_name
    try:
        with CURSOR:
            query = f"Select datediff(day, MAX(kiedy), GETDATE()) from technologia where po = {po_number}"
            CURSOR.execute(query)
            result = CURSOR.fetchone()[0]

            return result >= TimeConsts.TECO_DRAWING_DAYS

    except Exception:
        print_red(f'Something else during "{func_name}" gone wrong!')
        return False


def teco_closer(records):
    for order, days_passed in records:
        if days_passed > TimeConsts.TECO_DAYS and last_drawing(order):
            db_commit(
                query=f"EXECUTE [dbo].[finish_TECO_drawings_PO] {order}",
                func_name="teco_closer"
            )
            print(f'{order} prod. order set as completed due to TECO Status.')


def main():
    records = get_data()
    teco_closer(records)


if __name__ == '__main__':
    main()
