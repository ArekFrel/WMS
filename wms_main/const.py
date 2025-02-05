import pyodbc
from .confidential import *
from datetime import datetime
import time
import os
from stat import S_IWRITE, S_IREAD

"""Using the variable below disables the actual script execution and enters test mode"""
IS_IT_TEST = False


class TimeConsts:

    """Script runs in 10-minutes cycle,
    below variable says in which minute does it start every 10 minutes
    variable range 0 - 9 included
    this variable must comply with task manager settings:
    if Script launches everyday at 00:0X o'clock then variable should be = X
    """
    MINUTE_START = 5

    """Script does not work between:"""
    FROM_OCLOCK = 1
    TO_OCLOCK = 6

    """Reset Options - obsolete variables, currently not in use"""
    # HOUR = 14
    # MINUTES = 56

    '''GCP_OCLOCK is time when all files are checked if they're new'''
    GCP = 15

    """Time when TECO orders are set to completed. - obsolete"""
    # TECO_TIME = 15

    """Number of day after Finish date when Teco_completer completes the order"""
    TECO_DAYS = 0
    """Number of day after last drawing uploaded when Teco_completer completes the order"""
    TECO_DRAWING_DAYS = 2

    """Number of second to wait before new refreshing"""
    TIME_OF_BREAK = 120
    """Script lunches every SCHD_TIME second- variable should comply with task manager settingd."""
    SCHD_TIME = 600

    """Number of seconds after wich script work with folder from START_CATALOG"""
    if IS_IT_TEST:
        TIMEOUT_FOR_PLANERS = 0.1
        TIME_REFILL_CAT = 1
    else:
        TIMEOUT_FOR_PLANERS = 1800
        TIME_REFILL_CAT = 179


class Paths:

    RAPORT_CATALOG = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/'
    REGISTER = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/reg.txt'
    TRANSFER_FILE = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/transfer_history.txt'
    UPDATE_CAT = 'T:/__wms_update__'
    MODELS_CATALOG = 'W:/!!__PRODUKCJA__!!/5__Modele_3D/'

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

    """IQE stands for Immediate quotation export - scripts scans raport catalog for quote files in every second"""
    """, else it scans in a period of TIME_BREAK"""
    IQE = True

    """Name of file stopping quotation export script"""
    QESR_NAME = '.qesr'

    """Quotation Export bat file name"""
    QEBF = 'Quotation_export.bat'

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
        'kupowany',
        'zakup',
        'bought_script',
        'Zmiana na zakupowy'
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

    NOREG_QUERIES = [
            'delete from sap where confirmation =',
            'update sap_data',
            'update sap_data',
            'select item_data from sap_data',
            'delete from złe_pliki',
            'select sap_skrypt_zmiana from sap_data',
            'merge into sap as target']


class CatalogType:
    BOUGHT = 'BOUGHT'
    REFILL = 'REFILL'
    NORMAL = 'NORMAL'
    REFILL_BOUGHT = 'REFILL_BOUGHT'


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

    def do_quit():
        if any(text.lower().startswith(start_text) for start_text in Options.NOREG_QUERIES):
            return True

    if do_quit():
        return

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
        register('TEST =========' + query)
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


def so_list_getter():
    query = "SELECT " \
            "DISTINCT CONCAT([S.O.], ' ', [urządzenie Główne]) "\
            "FROM SAP "\
            "WHERE [S.O.] != 0 "\
            "AND [System Status] <> 'TECO'"
    try:
        CURSOR.execute(query)
        result = [str(val[0]) for val in CURSOR.fetchall()]
    except pyodbc.Error:
        print('Connection to database failed.')
        return []
    return result


def main():
    pass


if __name__ == '__main__':
    main()
