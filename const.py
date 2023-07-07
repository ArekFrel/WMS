import pyodbc
from pyodbc import DatabaseError, OperationalError, Error


"""Extensions of the files, that are allowed to go."""
ACC_EXT = [
    'pdf',
    'xlsx'  # to add another extensions add coma here
            # and type another extension between '' in this line
]

"""Number of second to wait before new refreshing"""
TIME_OF_BREAK = 120

"""Number of second after which the catalog is moved."""
TIMEOUT_FOR_PLANERS = 1800

""" Time between the script is not running"""
# time when script stops running
FROM_OCLOCK = 1
# time when script starts running
TO_OCLOCK = 6

""" PRODUCTION - catalogs where drawings are stored. """
PRODUCTION = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'

""" START_CATALOG - catalog where new drawing are uploaded by planners."""
START_CATALOG = 'W:/!!__PRODUKCJA__!!/4__Nowe_Rysunki/'

""" RAPORT_CATALOG - catalog where Sap report are stored."""
RAPORT_CATALOG = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/'

'''Text file, arhivising files added the old way.'''
TRANSFER_FILE = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/transfer_history.txt'

'''Permission to adding loose files to START_CATALOG'''
LOOSE_FILE_PERMISSION = True

'''Name of refill catalogue.'''
REFILL_CAT = 'X'

'''Permission to adding files uploaded directly into PRODUCTION catalog once per day
GCP_OCLOCK is time when all files are checked if they're new'''
GENERAL_CHECK_PERMISSION = True
GCP_OCLOCK = 15

'''Name of catalogue in TEMP, where nwe version is updated'''
UPDATE_CAT = 'T:/__wms_update__'

AUTOMAT_FILES_STORED = 'C:/Dokumenty/automat_light/WMS/'
"""Path of AUTOMAT file"""
AUTOMAT_BAT = 'C:/Dokumenty/automat_light/WMS/AUTOMAT.bat'



'''
**********************************
*                                *
*       Database information     *
*                                *
**********************************
'''

SERVER = 'SELUSQL16'
DATABASE = 'PRODUKCJAWORKFLOW'
CONN = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                          "Server="+SERVER+";"
                          "Database="+DATABASE+";"
                          "Trusted_Connection=yes;")
CONN.timeout = 10
CURSOR = CONN.cursor()


def db_commit(query, func_name):
    with CURSOR:
        try:
            CURSOR.execute(query)
            CURSOR.commit()

        except OperationalError:
            print(f'Operational Error in "{func_name}"')
            return False

        except DatabaseError:
            print(f'Time exceeded in "{func_name}"')
            return False

        except Error:
            print(f'Database Error in "{func_name}"')
            return False

    return True


def main():
    pass


if __name__ == '__main__':
    main()
