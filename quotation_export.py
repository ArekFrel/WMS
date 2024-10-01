import csv
from const import Paths, db_commit
import os
import pyodbc
from confidential import *


class Server:
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


class QuotationObj:

    FORBIDDEN_NAMES = [
        '0',
        '0.0'
    ]
    quot_cache = [] + FORBIDDEN_NAMES

    def __init__(self, name: str):
        self.drawing_number = name
        self.laser_pomoc = 0.0
        self.laser_ciecie = 0.0
        self.pily_ciecie = 0.0
        self.toczenie = 0.0
        self.frezowanie = 0.0
        self.gwintowanie = 0.0
        self.gotowanie_plastikow = 0.0
        self.ciecie_na_fisherze = 0.0
        self.ciecie_plyt_plastikowych = 0.0
        self.spawanie = 0.0
        self.przygotowanie_do_spawania = 0.0
        self.zgniatanie_spoin = 0.0
        self.spawanie_orbitalne = 0.0
        self.szlifowanie_reczne = 0.0
        self.wier_i_gwint_term = 0.0
        self.roztlaczanie_plaszczy = 0.0
        self.wyciaganie = 0.0
        self.organizacja = 0.0
        self.montaz = 0.0
        self.prostowanie = 0.0
        self.demontaz = 0.0
        self.wyoblanie = 0.0
        self.gilotyna_ciecie = 0.0
        self.walcowanie = 0.0
        self.giecie_pomoc = 0.0
        self.giecie_kraw = 0.0
        self.szlif_auto = 0.0
        self.spaw_auto = 0.0
        self.pisakowanie = 0.0
        self.szafy_elektryczne = 0.0
        self.okablowanie = 0.0
        self.bufor = 0.0
        self.quality_brig = 0.0
        self.testy = 0.0
        self.pakowanie = 0.0
        self.dokonczenie = 0.0

    @staticmethod
    def clear_cache():
        QuotationObj.quot_cache = [] + QuotationObj.FORBIDDEN_NAMES

    def add_to_cache(self):
        QuotationObj.quot_cache.append(self.drawing_number)

    def list_of_operations(self):
        op_list = [f"{attr}" for attr, val in self.__dict__.items() if isinstance(val, float) and val != 0]
        return "drawing_number, " + ','.join(op_list)

    def list_of_values(self):
        val_list = [f"{val}" for attr, val in self.__dict__.items() if isinstance(val, float) and val != 0]
        return f"'{self.drawing_number}', " + ','.join(val_list)

    def list_of_all_operations(self):
        op_list = [f"'{attr}'" for attr, val in self.__dict__.items() if isinstance(val, float)]
        return "drawing_number, " + ','.join(op_list)

    def all_ops(self):
        ops_list = [attr for attr, val in self.__dict__.items() if isinstance(val, float)]
        return ops_list

    def all_attr_reset(self):
        val_list = [
            f"{attr} = {QuotationObj.is_null(val)}" for attr, val in self.__dict__.items() if isinstance(val, float)
        ]
        return ' ,'.join(val_list) + ' '

    def query(self):
        query = f"IF NOT EXISTS (SELECT * FROM Quotation WHERE drawing_number = '{self.drawing_number}') " \
                f"BEGIN " \
                f"INSERT INTO Quotation ({self.list_of_operations()}) VALUES ({self.list_of_values()}) " \
                f"END " \
                f"ELSE " \
                f"BEGIN " \
                f"UPDATE Quotation " \
                f"SET {self.all_attr_reset()}" \
                f"WHERE drawing_number = '{self.drawing_number}' " \
                f"END; "
        return query

    def send_to_db(self):
        db_commit(self.query(), 'quotation_insert')
        print(self.drawing_number, '- added to quotation database')
        self.add_to_cache()

    @staticmethod
    def is_null(value):
        if value == 0:
            return 'NULL'
        else:
            return value


def send_to_db_by_csv():
    quot_files = [os.path.join(Paths.RAPORT_CATALOG, file) for file in os.listdir(Paths.RAPORT_CATALOG) if
                  file.startswith('SAP_QUOT')]
    for quot_file in quot_files:
        print(f'New file opened {quot_file}', 10 * '_')
        with open(quot_file) as file:
            remove_permission = True
            records = csv.reader(file)
            for index, record in enumerate(records, start=1):
                if index % 2 != 0 and record[0] not in QuotationObj.quot_cache:
                    obj = QuotationObj(record[0])
                    if obj.drawing_number == '':
                        remove_permission = False
                        break
                    vals = [val for val in record[6:]]
                    pairs = [(op, proper_val(val)) for op, val in zip(obj.all_ops(), vals) if not is_equal_zero(val)]
                    any_pairs = len(pairs)
                    while pairs:
                        op, val = pairs.pop(0)
                        try:
                            obj.__setattr__(op, float(val))
                        except ValueError:
                            print(f'Wrong value in "{quot_file}" drawing: {obj.drawing_number}')
                            any_pairs = -1
                            break
                    if any_pairs >= 1:
                        obj.send_to_db()
                    elif any_pairs == -1:
                        remove_permission = False
                        break
                    else:
                        continue
                else:
                    continue

        if remove_permission:
            try:
                os.remove(quot_file)
            except PermissionError:
                print(f'Nie usunięto pliku {quot_file}')
        else:
            try:
                os.rename(quot_file, new_failed_name_gen(quot_file))
            except PermissionError:
                print(f'nie usunięto zmieniono nazy pliku failed {quot_file}')

    QuotationObj.clear_cache()
    return True


def new_failed_name_gen(arg):
    new_path = f'{arg.split(".")[0].replace("SAP_QUOT", "SAP_failed_QUOT")}.csv'
    just_name, ext = new_path.split('/')[-1].split('.')
    full_name = '.'.join([just_name, ext])
    while full_name in os.listdir(Paths.RAPORT_CATALOG):
        name_list = just_name.split('QUOT_')
        if len(name_list) == 1:
            old_num = 0
            just_name = just_name.replace('QUOT', f'QUOT_{old_num + 1}')
            new_path = arg.replace('SAP_QUOT', just_name)
            full_name = '.'.join([just_name, ext])
        else:
            name_list = just_name.split('_')
            old_num = int(name_list[-1])
            just_name = f'{"_".join(name_list[0:-1])}_{old_num + 1}'
            quot_enum = arg.split('/')[-1].rstrip('.csv')
            new_path = f'{arg.replace(quot_enum, just_name)}'
            full_name = '.'.join([just_name, ext])
    return new_path


def proper_val(num):
    if num == '':
        return '0'
    else:
        return num


def is_equal_zero(num):
    if num in ('0', '', ' '):
        return True
    else:
        return False


def main():
    send_to_db_by_csv()


if __name__ == '__main__':
    main()
