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
        val_list = [f"{attr} = {QuotationObj.is_null(val)}" for attr, val in self.__dict__.items() if isinstance(val, float)]
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
        with open(quot_file) as file:
            records = csv.reader(file)
            for index, record in enumerate(records, start=1):
                if record[1] == 'Sprzedane':
                    continue    # ommiting bought parts
                if index % 2 != 0:
                    obj = QuotationObj(record[0])
                    vals = [val for val in record[6:]]
                    pairs = [(op, proper_val(val)) for op, val in zip(obj.all_ops(), vals) if not is_equal_zero(val)]
                    while pairs:
                        op, val = pairs.pop(0)
                        obj.__setattr__(op, float(val))
                else:
                    continue
                obj.send_to_db()
        os.remove(quot_file)
    return True


def proper_val(num):
    if num == '':
        return '0'
    else:
        return num


def is_equal_zero(num):
    if num in ('0', ''):
        return True
    else:
        return False


def main():
    send_to_db_by_csv()


if __name__ == '__main__':
    main()

