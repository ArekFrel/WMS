import os
import time
# from const import TIMEOUT_FOR_PLANERS

START_CATALOG = 'C:/Dokumenty/stary/'
PRODUCTION = 'W:\\!!__PRODUKCJA__!!\\1__Rysunki\\'
TIMEOUT_FOR_PLANERS = 1800


class File:

    def __init__(self, name, catalog=''):

        self.name = name
        self.file_name, self.extension = name.rsplit('.', 1)
        self.catalog_path = os.path.join(START_CATALOG, catalog)
        self.start_path = os.path.join(START_CATALOG, catalog, name)
        self.catalog = name[0:7]
        self.dest_path = os.path.join(PRODUCTION, catalog, name)

    def __str__(self):
        print(f'{self.start_path}')

    def move_file(self):
        print(f'przenoszenie pliku "{self.name}" do lokalilzacji "{self.dest_path}"')


class Catalog:

    def __init__(self, name):
        self.name = name
        self.catalog_path = os.path.join(START_CATALOG, name)
        self.age = time.time() - os.path.getctime(self.catalog_path)
        self.ready = (self.age > TIMEOUT_FOR_PLANERS)

    def __str__(self):
        print(f'{self.name}')



file1 = File('1999999 Info.pdf')
cat1 = Catalog('1999888')
file1.move_file()
file1 = File('1999999 SAP', '1999999')
file1.move_file()
t = 0