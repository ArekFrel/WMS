import pyodbc
from confidential import *


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
TIMEOUT_FOR_PLANERS = 1

""" Time between the script is not running"""
# time when script stops running
FROM_OCLOCK = 1
# time when script starts running
TO_OCLOCK = 6

""" PRODUCTION - catalogs where drawings are stored. """
# PRODUCTION = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'
PRODUCTION = 'C:/Dokumenty/sat/1__Rysunki/'

""" START_CATALOG - catalog where new drawing are uploaded by planners."""
# START_CATALOG = 'W:/!!__PRODUKCJA__!!/4__Nowe_Rysunki/'
START_CATALOG = 'C:/Dokumenty/sat/4__Nowe_Rysunki/'

""" RAPORT_CATALOG - catalog where Sap report are stored."""
RAPORT_CATALOG = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/'

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

"""Name of merged drawings to be ignored by script 'list_new-files'"""
MERGED_NAME = 'merged.pdf'

"""Minimal number of drawings to be merged in order"""

MERGED_MIN = 5 # should be low value, f.e. 5
MERGED_TIME_PERIOD = 5 # should be low value, f.e. 5



'''
**********************************
*                                *
*       Database information     *
*                                *
**********************************
'''

SERVER = SERVER_conf
DATABASE = DATABASE_conf
CONN = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    "Server="+SERVER+";"
    "Database="+DATABASE+";"
    "Trusted_Connection=yes;"
)
CONN.timeout = 20
CURSOR = CONN.cursor()


def db_commit(query, func_name):

    try:
        with CURSOR:
            CURSOR.execute(query)
            CURSOR.commit()
        return True

    except pyodbc.OperationalError:
        print(f'Operational Error in "{func_name}"')
        return False

    except pyodbc.DatabaseError:
        print(f'Time exceeded in "{func_name}"')
        return False

    except pyodbc.Error:
        print(f'Database Error in "{func_name}"')
        return False

    except Exception:
        print(f'Something else during "{func_name}" gone wrong!')
        return False


def main():
    pass


if __name__ == '__main__':
    main()
