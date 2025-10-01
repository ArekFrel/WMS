import os
import re
import time
import shutil
from stat import S_IWRITE
from wms_main.const import TimeConsts, Paths, Options
from wms_main.const import CURSOR, REFILL_CAT, CatalogType
from pyodbc import Error


class Catalog:

    def __init__(self, name, path=()):
        self.name = name
        self.path_tuple = path
        self.catalog_path = os.path.join(Paths.START_CATALOG, '/'.join(self.path_tuple), name)
        self.age = time.time() - os.path.getctime(self.catalog_path)
        self.ready = (self.age > TimeConsts.TIMEOUT_FOR_PLANERS)
        self.bought = self.is_bought()
        self.refill_cat = self.is_refill()
        self.laser_collaborate = self.is_laser_collaborate()
        self.catalog_type = ''
        self.catalog_category()

    def __str__(self):
        return f'{self.name}'

    def __bool__(self):
        return True

    def path_of_cat(self):
        if self.path_tuple:
            return f'{"/".join(self.path_tuple)}/{self.name}'
        else:
            return self.name

    def catalog_category(self):
        if self.is_refill() and self.is_bought():
            self.catalog_type = CatalogType.REFILL_BOUGHT
            return None
        if self.is_bought():
            self.catalog_type = CatalogType.BOUGHT
            return None
        if self.is_refill():
            self.catalog_type = CatalogType.REFILL
            return None
        if self.is_laser_collaborate():
            self.catalog_type = CatalogType.LASER_COL
            return None
        self.catalog_type = CatalogType.NORMAL
        return None

    def catalog_content(self):
        return os.listdir(self.catalog_path)

    def is_bought(self):
        for word in Options.BOUGHT_NAMES:
            if word == self.name.lower():
                return True
        if self.name.startswith('bought_script_'):
            return True
        return False

    def is_laser_collaborate(self):
        for word in Options.LASER_COL_NAMES:
            if word == self.name.lower():
                return True
        return False


    def is_refill(self):
        if self.name.upper() == REFILL_CAT or any(item in [REFILL_CAT, REFILL_CAT.lower()] for item in self.path_tuple):
            self.ready = (self.age > TimeConsts.TIME_REFILL_CAT)
            return True
        else:
            return False

    def quit_catalog(self):
        if self.ready:
            return False
        return True


class File:

    bad_files = 0
    moved_files = 0
    refilled_files = 0
    replaced_files = 0

    def __init__(self, name: str, catalog=None):
        self.name = name
        self.annotate = ""
        self.file_name, self.extension = name.rsplit('.', 1)
        self.bought = False
        self.catalog = ''
        self.refill = False
        self.new_name = self.name
        self.start_path_new_name = os.path.join(Paths.START_CATALOG, self.new_name)
        self.catalog_path = Paths.START_CATALOG
        self.laser_collaborate = False
        self.catalog_options(catalog)
        self.loose = not bool(self.catalog)
        self.sub_bought = False
        self.watermark = None
        self.file_categorize()
        self.check_watermarking()
        self.new_name_create()
        self.po = self.new_name[:7]
        self.start_path = os.path.join(self.catalog_path, self.name)
        self.proper_name = self.is_proper_name()
        self.dest_catalog = os.path.join(Paths.PRODUCTION, self.po)
        self.dest_path = os.path.join(self.dest_catalog, self.new_name)
        self.replace = self.refill and os.path.exists(self.dest_path)
        self.set_file_modifable()

    def __str__(self):
        return f'{self.start_path}'

    def catalog_options(self, catalog=None):
        if catalog:
            if catalog.bought:
                self.bought = True
            self.laser_collaborate = catalog.laser_collaborate
            self.catalog = '' if catalog.bought else catalog.name
            self.refill = catalog.refill_cat
            self.start_path_new_name = os.path.join(Paths.START_CATALOG, catalog.path_of_cat(), self.new_name)
            self.catalog_path = os.path.join(Paths.START_CATALOG, catalog.path_of_cat())

    def new_name_create(self):
        self.new_name = self.file_name.lower().replace(self.annotate, '')
        self.new_name = '.'.join([self.new_name.strip().rstrip(), self.extension])
        self.new_name = File.delete_double_space(self.new_name)
        self.file_name = self.new_name.rsplit('.', 1)[0]

    def file_categorize(self):
        if re.search(r"bu[^y]", self.name.lower()) is not None:
            self.sub_bought = True
            self.annotate = "bu"
            return
        if 'buy' in self.name.lower():
            self.bought = True
            self.annotate = "buy"
            return
        if re.search(r"kl", self.name.lower()) is not None:
            self.laser_collaborate = True
            self.annotate = "kl"
            return

    def check_watermarking(self):
        if not any ((self.sub_bought, self.laser_collaborate, self.bought)):
            return
        if self.laser_collaborate:
            self.watermark = Paths.WATERMARK_KL
            return
        if self.bought:
            self.watermark = Paths.WATERMARK_BOUGHT
            return
        if self.sub_bought:
            self.watermark = Paths.WATERMARK_SUB_BOUGHT
            return



    def un_read_only(self):
        os.chmod(self.start_path, S_IWRITE)

    def base_and_number(self):
        """Return base name and order number if file in destination already exist"""
        return self.file_name.rsplit(sep='_', maxsplit=1)

    def is_bought(self):
        for word in Options.BOUGHT_FILES_NAMES:
            if word in self.name.lower():
                return True
        return False

    def move_file(self):
        """Moving file to a new location."""
        os.rename(self.start_path, self.start_path)
        if self.refill:
            if os.path.exists(self.dest_path):
                os.remove(self.dest_path)
                self.replace = True
                shutil.move(self.start_path, self.dest_path)
                File.add_replaced_file()
            else:
                shutil.move(self.start_path, self.dest_path)
                File.add_refilled_file()
        else:
            shutil.move(self.start_path, self.dest_path)
            File.add_moved_file()

    def set_file_modifable(self):
        os.chmod(self.start_path, S_IWRITE)
        if os.path.exists(self.dest_path):
            os.chmod(self.dest_path, S_IWRITE)

    def create_catalog(self):
        # Creating po folder if not exists
        if not os.path.exists(self.dest_catalog) and not self.loose:
            os.mkdir(self.dest_catalog)
        # Creating po folder for loose file
        elif not os.path.exists(self.dest_catalog) and File.check_po_in_sap(self.po):
            os.mkdir(self.dest_catalog)

    def set_available_name(self):
        while os.path.exists(self.dest_path) and not self.refill:
            self.name_if_exist_class()

    def name_if_exist_class(self):
        """Changes a new name of the file in new location, if current already exists."""
        if '_' in self.new_name[-8:-1]:
            base_name, ord_num = self.base_and_number()
            self.new_name = f'{base_name}_{int(ord_num) + 1}.{self.extension}'
        else:
            self.new_name = f'{self.file_name}_1.{self.extension}'
        self.file_name = self.new_name.rsplit('.', 1)[0]
        self.dest_path = os.path.join(Paths.PRODUCTION, self.po, self.new_name)

    def is_proper_name(self):
        if any((self.refill, self.bought, self.laser_collaborate)):
            return True
        return (self.catalog == self.po) if not self.bought else True

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

    @staticmethod
    def check_po_in_sap(po_num):
        query = f"SELECT COUNT(Confirmation) FROM Sap WHERE [P.O.] = {po_num};"
        with CURSOR:
            try:
                CURSOR.execute(query)
                result = CURSOR.fetchone()

            except Error:
                print(f'Database Error in "'
                      f''
                      f'check_po_in_sap"')
                return False
        return result[0] > 0


def main():
    pass


if __name__ == '__main__':
    main()
