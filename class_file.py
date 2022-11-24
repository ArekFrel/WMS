import os
import time
import shutil
from const import TIMEOUT_FOR_PLANERS, START_CATALOG, PRODUCTION


class File:

    bad_files = 0
    moved_files = 0
    refilled_files = 0
    replaced_files = 0

    def __init__(self, name, catalog=''):

        self.name = name
        self.file_name, self.extension = name.rsplit('.', 1)
        self.catalog_path = os.path.join(START_CATALOG, catalog)
        self.start_path = os.path.join(START_CATALOG, catalog, name)
        if catalog == '':
            self.loose = True
        else:
            self.loose = False
            self.proper_name = (catalog == name[0:7])
        self.catalog = name[0:7]
        self.dest_catalog = os.path.join(PRODUCTION, self.catalog)
        self.dest_path = os.path.join(PRODUCTION, self.catalog, name)
        self.new_name = self.file_name

    def __str__(self):
        return f'{self.start_path}'

    def base_and_number(self):

        """Return base name and order number if file in destination already exist"""

        return self.new_name.rsplit(sep='_', maxsplit=1)

    def move_file(self):

        """Moving file to a new location."""

        os.rename(self.start_path, self.start_path)
        shutil.move(self.start_path, self.dest_path)

    def name_if_exist_class(self):
        """Changes a new name of the file in new location, if current already exists."""

        if '_' in self.new_name[-8:-1]:
            base_name, ord_num = self.base_and_number()
            self.new_name = f'{base_name}_{int(ord_num) + 1}'
        else:
            self.new_name = f'{self.file_name}_1'
        self.dest_path = os.path.join(PRODUCTION, self.catalog, self.new_name + '.' + self.extension)

    @staticmethod
    def moved_files_counter():
        return File.moved_files

    @staticmethod
    def add_moved_file():
        File.moved_files += 1

    @staticmethod
    def bad_files_counter():
        return File.bad_files

    @staticmethod
    def add_bad_file():
        File.bad_files += 1

    @staticmethod
    def add_replaced_file():
        File.replaced_files += 1

    @staticmethod
    def add_refilled_file():
        File.refilled_files += 1

    @staticmethod
    def print_good_files():
        if File.moved_files > 0:
            if File.moved_files == 1:
                print(f'{File.moved_files} file moved to production and added to Database')
            else:
                print(f'{File.moved_files} files moved to production and added to Database')

    @staticmethod
    def print_bad_files():
        if File.bad_files > 0:
            if File.bad_files == 1:
                print('1 bad file.')
            else:
                print(f'{File.bad_files} bad files.')

    @staticmethod
    def print_replaced_files():
        if File.replaced_files > 0:
            if File.replaced_files == 1:
                print('1 file replaced.')
            else:
                print(f'{File.replaced_files} files replaced.')

    @staticmethod
    def print_refilled_files():
        if File.refilled_files > 0:
            if File.refilled_files == 1:
                print('1 file refilled.')
            else:
                print(f'{File.refilled_files} files refilled.')

    @staticmethod
    def print_counter_status():
        File.print_bad_files()
        File.print_good_files()
        File.print_refilled_files()
        File.print_replaced_files()

    @staticmethod
    def set_counter_zero():
        File.moved_files = 0
        File.bad_files = 0
        File.replaced_files = 0
        File.refilled_files = 0


class Catalog:

    def __init__(self, name):
        self.name = name
        self.catalog_path = os.path.join(START_CATALOG, name)
        self.age = time.time() - os.path.getctime(self.catalog_path)
        self.ready = (self.age > TIMEOUT_FOR_PLANERS)

    def __str__(self):
        return f'{self.name}'

    def catalog_content(self):
        return os.listdir(self.catalog_path)


def main():
    pass


if __name__ == '__main__':
    main()


