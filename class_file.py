import os
import re
import time
import shutil
from stat import S_IWRITE
from const import TimeConsts, Paths, Options


class File:

    bad_files = 0
    moved_files = 0
    refilled_files = 0
    replaced_files = 0

    def __init__(self, name, bought_cat=False, catalog=''):
        self.name = name
        self.file_name, self.extension = name.rsplit('.', 1)
        self.bought_cat = bought_cat
        self.catalog = '' if bought_cat else catalog
        self.loose = not bool(self.catalog)
        self.bought_name = False
        self.sub_bought = False
        self.new_name = self.name
        self.check_for_watermarking()
        self.new_name_create()
        self.start_path_new_name = os.path.join(Paths.START_CATALOG, catalog, self.new_name)
        self.po = self.new_name[:7]
        self.catalog_path = os.path.join(Paths.START_CATALOG, catalog)
        self.start_path = os.path.join(Paths.START_CATALOG, catalog, name)
        self.proper_name = (catalog == self.po) if not self.bought_cat else True
        self.dest_catalog = os.path.join(Paths.PRODUCTION, self.po)
        self.dest_path = os.path.join(self.dest_catalog, self.new_name)
        self.un_read_only()

    def __str__(self):
        return f'{self.start_path}'

    def new_name_create(self):
        annotate = 'bu' if self.sub_bought else 'buy'
        self.new_name = self.file_name.lower().replace(annotate, '')
        self.new_name = '.'.join([self.new_name.strip().rstrip(), self.extension])
        self.new_name = File.delete_double_space(self.new_name)
        self.file_name = self.new_name.rsplit('.', 1)[0]

    def check_for_watermarking(self):
        if re.search(r"bu[^y]", self.name.lower()) is not None:
            self.sub_bought = True
        elif 'buy' in self.name.lower():
            self.bought_name = True

    def un_read_only(self):
        os.chmod(self.start_path, S_IWRITE)

    def base_and_number(self):
        """Return base name and order number if file in destination already exist"""
        return self.file_name.rsplit(sep='_', maxsplit=1)

    def move_file(self):
        """Moving file to a new location."""
        os.rename(self.start_path, self.start_path)
        shutil.move(self.start_path, self.dest_path)

    def name_if_exist_class(self):
        """Changes a new name of the file in new location, if current already exists."""
        if '_' in self.new_name[-8:-1]:
            base_name, ord_num = self.base_and_number()
            self.new_name = f'{base_name}_{int(ord_num) + 1}.{self.extension}'
        else:
            self.new_name = f'{self.file_name}_1.{self.extension}'
        self.file_name = self.new_name.rsplit('.', 1)[0]
        self.dest_path = os.path.join(Paths.PRODUCTION, self.po, self.new_name)

    @staticmethod
    def delete_double_space(text):
        while '  ' in text:
            text = text.replace('  ', ' ')
        return text

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
                print(f'{File.moved_files} file moved to Production and added to Database')
            else:
                print(f'{File.moved_files} files moved to Production and added to Database')

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
        self.catalog_path = os.path.join(Paths.START_CATALOG, name)
        self.age = time.time() - os.path.getctime(self.catalog_path)
        self.ready = (self.age > TimeConsts.TIMEOUT_FOR_PLANERS)
        self.bought = self.is_bought()

    def __str__(self):
        return f'{self.name}'

    def catalog_content(self):
        return os.listdir(self.catalog_path)

    def is_bought(self):
        for word in Options.BOUGHT_NAMES:
            if word == self.name.lower():
                return True
        if self.name.startswith('bought_script_'):
            return True
        return False


def main():
    pass


if __name__ == '__main__':
    main()

