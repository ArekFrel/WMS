import shutil
from datetime import time
from utils.pump_block_tracker.pump_block_technology import PbTech
from wms_main.const import *
from pyodbc import Error, DataError, OperationalError


def copy_draw_file(draw, po, pb_id, pb):
    base_file = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw} {hash_id(pb_id)}.pdf')
    new_file = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw} {hash_id(pb)}.pdf')
    try:
        shutil.copyfile(base_file, new_file)
    except FileNotFoundError:
        print(f'Aint no such file {base_file}')
    return None


def drawing_multiplier(draw_id, draw, po, pcs, pb_id):
    query = ''
    pb = pb_id + 1
    for i in range(pcs - 1):
        now = str(datetime.fromtimestamp(time.time(), ))[0:-3]
        query = f"{query} INSERT INTO TECHNOLOGIA (RYSUNEK, PO, Sztuki, Materiał, OP_1, OP_2, OP_3, OP_4, OP_5, " \
            f"OP_6, OP_7, OP_8, OP_9, OP_10, OP0, OP1, Status_op, Stat, Liczba_Operacji, Plik, Kiedy) " \
            f"SELECT CONCAT('{draw}', ' {hash_id(pb)}'), PO, Sztuki, Materiał, OP_1, OP_2, OP_3, OP_4, " \
            f"OP_5, OP_6, OP_7, OP_8, OP_9, OP_10, OP0, OP1, Status_op, Stat, Liczba_Operacji, " \
            f"CONCAT('{po}', ' ', '{draw}', ' {hash_id(pb)}'), '{now}' " \
            f"FROM TECHNOLOGIA WHERE ID = {draw_id}"
        copy_draw_file(draw, po, pb_id, pb)
        pb = pb + 1
    db_commit(query=query, func_name='drawing_multiplier')


def pb_id_updater(num):
    db_commit(f'UPDATE pb_identifier set pb_id_val = pb_id_val + {num}', func_name='pb_id_updater')
    return None


def pb_main_draw_rename(draw, po, pb_id):
    old_name = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw}.pdf')
    new_name = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw} {hash_id(pb_id)}.pdf')
    try:
        os.rename(old_name, new_name)
    except FileNotFoundError:
        print(f'Aint no such file {old_name}')
    except PermissionError:
        print(f'File locked {old_name}')
    return None


def pb_main_draw_tech_setter(draw_id, pb_id):
    tech = PbTech()
    query = f"UPDATE TECHNOLOGIA SET " \
        f"Rysunek = CONCAT(Rysunek, ' {hash_id(pb_id)}'), " \
        f"Sztuki = 1, " \
        f"Materiał = 'duplex', " \
        f"OP0 = {tech.curr_op()}, " \
        f"OP1 = {tech.next_op()}, " \
        f"OP_1 = {tech.pb_pop()}, " \
        f"OP_2 = {tech.pb_pop()}, " \
        f"OP_3 = {tech.pb_pop()}, " \
        f"OP_4 = {tech.pb_pop()}, " \
        f"OP_5 = {tech.pb_pop()}, " \
        f"OP_6 = {tech.pb_pop()}, " \
        f"OP_7 = {tech.pb_pop()}, " \
        f"OP_8 = {tech.pb_pop()}, " \
        f"OP_9 = {tech.pb_pop()}, " \
        f"OP_10 = {tech.pb_pop()}, " \
        f"Status_Op = 1, " \
        f"Stat = 0, " \
        f"Liczba_Operacji = {tech.tech_len}, " \
        f"Plik = CONCAT(PO, ' ', Rysunek, ' {hash_id(pb_id)}')" \
        f"WHERE ID = {draw_id}"
    db_commit(query=query, func_name='pb_main_draw_tech_setter')


def po_drawing_multiplied_setter(arg):
    query = f"UPDATE pump_block_orders SET multiplied_tech = 1 " \
            f"WHERE PO = {arg}"
    db_commit(query, func_name='po_drawing_multiplied_setter')


def pumpblock_drawing_handler():
    po_drawings_data = pumpblock_info_getter('ORPHAN_DRAWINGS')  # wyszukiwanie nieobsłużonych rysunków pump blocków
    if not po_drawings_data:
        return
    pb_id = pumpblock_info_getter('ID')
    num = 0
    for draw_id, draw, po, pcs in po_drawings_data:
        pb_main_draw_tech_setter(draw_id, pb_id)
        pb_main_draw_rename(draw, po, pb_id)
        drawing_multiplier(draw_id, draw, po, pcs, pb_id)
        po_drawing_multiplied_setter(po)
        po_drawing_added_setter(po)
        pb_id = pb_id + pcs
        num = num + pcs
    pb_id_updater(num)


def hash_id(num: int):
    return f"#{num: 0>4}"


def po_drawing_added_setter(po):
    query = f"UPDATE pump_block_orders SET drawing_added = 1 " \
            f"WHERE PO = {po}"
    db_commit(query, func_name='po_drawing_added_setter')


def po_pumpblock_recorder():

    po_to_record = pumpblock_info_getter('new')  # Select new pumpblock orders
    for row in po_to_record:
        po, pcs, device = row
        query = f"INSERT INTO pump_block_orders VALUES ({po}, {pcs}, '{device}', 0, 0, 0, 0, 0, 0)"
        db_commit(query, func_name='po_pumpblock_recorder')


def pumpblock_info_getter(arg):
    single_val = ['ID']
    match arg:
        case 'ID':
            query = "SELECT pb_id_val FROM pb_identifier; " \

        case 'ORPHAN_DRAWINGS':
            query = "SELECT T.id, T.Rysunek, T.PO, P.pcs from TECHNOLOGIA T " \
                    "RIGHT JOIN ( " \
                    "SELECT PO, pcs FROM PUMP_BLOCK_ORDERS WHERE drawing_added = 0) P " \
                    "ON T.[PO] = P.PO " \
                    "WHERE T.Status_Op = 6 " \
                    "ORDER BY T.ID;"
        case 'new':
            query = 'SELECT * FROM dbo.new_pb_orders()'
        case 'PBT_ALL':
            query = "SELECT PO FROM PUMP_BLOCK_ORDERS"
        case 'PBT_DRAW':
            query = "SELECT PO FROM PUMP_BLOCK_ORDERS" \
                    "WHERE drawing_added IS FALSE "
        case 'PBT_MULTECH':
            query = "SELECT PO FROM PUMP_BLOCK_ORDERS" \
                    "WHERE multiplied_tech IS FALSE "
        case 'SAP':
            query = "SELECT DISTINCT [P.O.] FROM SAP" \
                    "WHERE [System Status] != 'TECO' "\
                    "AND [Urządzenie] LIKE '%pump block%'"
        case _:
            return None

    try:
        CURSOR.execute(query)
        if arg in single_val:
            result = CURSOR.fetchval()
            return result
        result = CURSOR.fetchall()
        if not result:
            return []
        if len(result[0]) > 1:
            return [val for val in result]
        elif len(result[0]) == 1:
            return [val[0] for val in result]

    except Error:
        print('Connection to database failed.')
        return []
    except OperationalError:
        print('Operatinal Error.')
        return []
    except DataError:
        print('Data Error.')
        return []


def main():
    po_pumpblock_recorder()   # pass
    pumpblock_drawing_handler()


if __name__ == '__main__':
    main()
