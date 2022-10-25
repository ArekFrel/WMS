import pyodbc
"""Number of second to wait before new refreshing"""
TIME_OF_BREAK = 300

""" PRODUCTION - catalogs where drawings are stored. """
PRODUCTION = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'

""" START_CATALOG - catalog where new drawing are uploaded by planners."""
START_CATALOG = 'W:/!!__PRODUKCJA__!!/4__Nowe_Rysunki/'

""" RAPORT_CATALOG - catalog where Sap report are stored."""
RAPORT_CATALOG = 'W:/!!__PRODUKCJA__!!/2__Baza_Danych/'

SERVER = 'SELUSQL16'
DATABASE = 'PRODUKCJAWORKFLOW'
CONN = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                          "Server="+SERVER+";"
                          "Database="+DATABASE+";"
                          "Trusted_Connection=yes;")
CURSOR = CONN.cursor()

TRANSFER_FILE = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'
