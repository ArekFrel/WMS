import pyodbc
from confidential import *
from datetime import datetime
import time
import os
from stat import S_IWRITE, S_IREAD

"""Using the variable below disables the actual script execution and enters test mode"""
IS_IT_TEST = True


class TimeConsts:
    """Script is stopped between:"""
    FROM_OCLOCK = 1
    TO_OCLOCK = 6

    """Reset Options:"""
    HOUR = 14
    MINUTES = 56

    '''GCP_OCLOCK is time when all files are checked if they're new'''
    GCP = 15

    """Time when TECO orders are set to completed."""
    TECO_TIME = 15

    """Number of day after which Teco_completer completes the order"""
    TECO_DAYS = 0

    """Number of second to wait before new refreshing"""
    TIME_OF_BREAK = 119
    SCHD_TIME = 600
    if IS_IT_TEST:
        TIMEOUT_FOR_PLANERS = 0.1
    else:
        TIMEOUT_FOR_PLANERS = 180


class Paths:

    RAPORT_CATALOG = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/'
    REGISTER = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/reg.txt'
    TRANSFER_FILE = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/transfer_history.txt'
    UPDATE_CAT = 'T:/__wms_update__'
    """Path of AUTOMAT file"""
    AUTOMAT_FILES_STORED = 'C:/Dokumenty/automat_light/WMS/'
    AUTOMAT_BAT = 'C:/Dokumenty/automat_light/WMS/AUTOMAT.bat'
    """Path of watermarks"""
    WATERMARK_BOUGHT = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/_images/water_mark_bought.jpg'
    WATERMARK_SUB_BOUGHT = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/_images/water_mark_sub_bought.jpg'
    if IS_IT_TEST:
        PRODUCTION = 'C:/Dokumenty/sat/1__Rysunki/'
        START_CATALOG = 'C:/Dokumenty/sat/4__Nowe_Rysunki/'
    else:
        """PRODUCTION - catalogs where drawings are stored. """
        PRODUCTION = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'
        """START_CATALOG - catalog where new drawing are uploaded by planners."""
        START_CATALOG = 'W:/!!__PRODUKCJA__!!/4__Nowe_Rysunki/'


class Options:
    """The number of records sent to the database at one time"""
    QUERY_WRAPPER = 50

    """Permission to adding loose files to Paths.START_CATALOG"""
    LOOSE_FILE_PERMISSION = True

    """Names of catalogs to be considered to be bought."""
    BOUGHT_NAMES = [
        'kup',
        'buy',
        'bought',
        'zakupowy',
        'zakupowe',
        'kupne',
        'kupowane',
        'bought_script'
    ]

    """Extensions of the files, that are allowed to go."""
    ACC_EXT = [
        'pdf',
        'xlsx'  # to add another extensions add coma here
        # and type another extension between '' in this line
    ]

    '''Permission to adding files uploaded directly into Paths.PRODUCTION catalog once per day
    GCP_OCLOCK is time when all files are checked if they're new'''
    GENERAL_CHECK_PERMISSION = True


TEST_RETURN_ORDERS = []
TEST_RETURN_DRAWINGS = []
TEST_RETURN_NUM = 5


'''Name of refill catalogue.'''
REFILL_CAT = 'X'


"""Name of merged drawings to be ignored by script 'list_new-files'"""
MERGED_NAME = 'merged.pdf'

"""Minimal number of drawings to be merged in order"""

MERGED_MIN = 2  # should be low value, f.e. 5
# MERGED_TIME_PERIOD = 120# should be low value, f.e. 5

'''
**********************************
*                                *
*       Database information     *
*                                *
**********************************
'''

SERVER = SERVER_conf
DATABASE = DATABASE_conf
DRIVER = DRIVER_conf
CONN = pyodbc.connect(
    "Driver="+DRIVER+";"
    "Server="+SERVER+";"
    "Database="+DATABASE+";"
    "Trusted_Connection=yes;"
)
CONN.timeout = 20
CURSOR = CONN.cursor()


def register(text):
    if text.startswith('Delete from SAP WHERE Confirmation ='):
        return None
    os.chmod(Paths.REGISTER, S_IWRITE)
    with open(Paths.REGISTER, 'a', encoding='utf-8') as history_file:
        now = str(datetime.fromtimestamp(time.time(), ))[0:-6]
        history_file.write(f'{now}____{text} \n')
    os.chmod(Paths.REGISTER, S_IREAD)


def db_commit(query, func_name):

    def print_red(text):
        COL_START = '\33[91m'
        COL_END = '\033[0m'
        print(COL_START + f'{text}' + COL_END)
        register(text)
        register(query)

    if IS_IT_TEST:
        print(query)
        return None

    try:
        with CURSOR:
            register(query)
            CURSOR.execute(query)
            CURSOR.commit()
        return True

    except pyodbc.OperationalError:
        print_red(f'Operational Error in "{func_name}"')
        return False

    except pyodbc.DatabaseError:
        print_red(f'Time exceeded in "{func_name}"')
        return False

    except pyodbc.Error:
        print_red(f'Database Error in "{func_name}"')
        return False

    except Exception:
        print_red(f'Something else during "{func_name}" gone wrong!')
        return False


def main():
    pass


if __name__ == '__main__':
    main()

