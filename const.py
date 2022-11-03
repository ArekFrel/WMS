import pyodbc
"""Number of second to wait before new refreshing"""
TIME_OF_BREAK = 300

"""Number of second after which the catalog is moved."""
TIMEOUT_FOR_PLANERS = 1800

""" Time between the script is not running"""

# time when script stops running
FROM_OCLOCK = 2

# time when script starts running
TO_OCLOCK = 6

""" PRODUCTION - catalogs where drawings are stored. """
PRODUCTION = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'

""" START_CATALOG - catalog where new drawing are uploaded by planners."""
START_CATALOG = 'W:/!!__PRODUKCJA__!!/4__Nowe_Rysunki/'

""" RAPORT_CATALOG - catalog where Sap report are stored."""
RAPORT_CATALOG = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/'

'''Database information'''
SERVER = 'SELUSQL16'
DATABASE = 'PRODUKCJAWORKFLOW'
CONN = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                          "Server="+SERVER+";"
                          "Database="+DATABASE+";"
                          "Trusted_Connection=yes;")
CURSOR = CONN.cursor()

'''Text file, arhivising files added the old way.'''
TRANSFER_FILE = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/transfer_history.txt'

'''Permission for adding loose files from START_CATALOG'''
LOOSE_FILE_PERMISSION = True


