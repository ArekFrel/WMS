import pyodbc
from confidential import *
from datetime import datetime
import time
import os
from stat import S_IWRITE, S_IREAD

"""Using the variable below disables the actual script execution and enters test mode"""
IS_IT_TEST = False

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

"""Number of second to wait before new refreshing"""
TIME_OF_BREAK = 120

"""Number of second after which the catalog is moved."""
""" Time between the script is not running"""
# time when script stops running
FROM_OCLOCK = 1
# time when script starts running
TO_OCLOCK = 6

if IS_IT_TEST:
    PRODUCTION = 'C:/Dokumenty/sat/1__Rysunki/'
    START_CATALOG = 'C:/Dokumenty/sat/4__Nowe_Rysunki/'
    TIMEOUT_FOR_PLANERS = 0.1
else:
    """ PRODUCTION - catalogs where drawings are stored. """
    PRODUCTION = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'
    """ START_CATALOG - catalog where new drawing are uploaded by planners."""
    START_CATALOG = 'W:/!!__PRODUKCJA__!!/4__Nowe_Rysunki/'
    """Number of second after which the catalog is moved."""
    TIMEOUT_FOR_PLANERS = 1800

TEST_RETURN_ORDERS = []
TEST_RETURN_DRAWINGS = []
TEST_RETURN_NUM = 5

""" RAPORT_CATALOG - catalog where Sap report are stored."""
RAPORT_CATALOG = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/'

REGISTER = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/reg.txt'

'''Text file, archiving files added the old way.'''
TRANSFER_FILE = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/transfer_history.txt'

'''Permission to adding loose files to START_CATALOG'''
LOOSE_FILE_PERMISSION = True

'''Name of refill catalogue.'''
REFILL_CAT = 'X'

'''Permission to adding files uploaded directly into PRODUCTION catalog once per day
GCP_OCLOCK is time when all files are checked if they're new'''
GENERAL_CHECK_PERMISSION = True
GCP_OCLOCK = 15

'''Name of catalogue in TEMP, where new version is updated'''
UPDATE_CAT = 'T:/__wms_update__'

AUTOMAT_FILES_STORED = 'C:/Dokumenty/automat_light/WMS/'
"""Path of AUTOMAT file"""
AUTOMAT_BAT = 'C:/Dokumenty/automat_light/WMS/AUTOMAT.bat'

"""Path of watermarks"""
WATERMARK_BOUGHT = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/_images/water_mark_bought.jpg'
WATERMARK_SUB_BOUGHT = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/_images/water_mark_sub_bought.jpg'

"""Name of merged drawings to be ignored by script 'list_new-files'"""
MERGED_NAME = 'merged.pdf'

"""Minimal number of drawings to be merged in order"""

MERGED_MIN = 2# should be low value, f.e. 5
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
    os.chmod(REGISTER, S_IWRITE)
    with open(REGISTER, 'a', encoding='utf-8') as history_file:
        now = str(datetime.fromtimestamp(time.time(), ))[0:-6]
        history_file.write(f'{now}____{text} \n')
    os.chmod(REGISTER, S_IREAD)


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


def generate_timeout_for_planners():
    return 0.1 if IS_IT_TEST else 1800


def main():
    pass


if __name__ == '__main__':
    main()

