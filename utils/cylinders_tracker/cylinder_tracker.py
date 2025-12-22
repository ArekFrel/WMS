import shutil
from datetime import datetime, time, date
from wms_main.const import *
from cylinders_data import *
from cylinders_technology import *
from utils.pump_block_tracker.pb_tracker import copy_draw_file
from pyodbc import Error, DataError, OperationalError


def cylinder_tech_setter(draw_id, draw, cylinder_id):

    tech_route = CylinderTechnology(draw)
    hash_num = hash_cyl_id(cylinder_id, tech_route.draw_type)
    query = f"UPDATE TECHNOLOGIA SET " \
            f"Rysunek = CONCAT(Rysunek, '{hash_num}'), " \
            f"Sztuki = 1, " \
            f"Materiał = '{tech_route.material}', " \
            f"Komentarz = '{tech_route.comment}', " \
            f"OP0 = {tech_route.curr_op()}, " \
            f"OP1 = {tech_route.next_op()}, " \
            f"OP_1 = {tech_route.cyl_pop()}, " \
            f"OP_2 = {tech_route.cyl_pop()}, " \
            f"OP_3 = {tech_route.cyl_pop()}, " \
            f"OP_4 = {tech_route.cyl_pop()}, " \
            f"OP_5 = {tech_route.cyl_pop()}, " \
            f"OP_6 = {tech_route.cyl_pop()}, " \
            f"OP_7 = {tech_route.cyl_pop()}, " \
            f"OP_8 = {tech_route.cyl_pop()}, " \
            f"OP_9 = {tech_route.cyl_pop()}, " \
            f"OP_10 = {tech_route.cyl_pop()}, " \
            f"Status_Op = 1, " \
            f"Stat = 0, " \
            f"Liczba_Operacji = {tech_route.tech_len}, " \
            f"Plik = CONCAT(PO, ' ', Rysunek, ' {hash_num}')" \
            f"WHERE ID = {draw_id}"
    db_commit(query=query, func_name='cylinder_tech_setter')

def po_cylinder_recorder():

    po_to_record = cylinder_info_getter('new')  # Select new cylinder orders
    for row in po_to_record:
        po, start_date, device, planner, pcs, status = row
        part, multiplied = part_getter(device)
        cyl_type = type_getter(device)

        query = f"INSERT INTO cylinders_orders VALUES ({po}, {pcs}, '{part}', '{cyl_type}', '{device}', " \
                f" 0, {multiplied}, 0); "
        db_commit(query, func_name='po_cylinders_recorder')
        print(f"order {po} added.")

def po_cylinder_recounter():

    records = cylinder_info_getter('recount')
    if records:
        query = ""
        for record in records:
            start_date, po, pcs, part, cyl_type, name = record

            if part in ('sleeve', 'flange'): # and status == 'TECO':
                query = f"UPDATE dbo.cylinders_stock SET {part}s_pcs = {part}s_pcs + {pcs} WHERE cylinder_type = '{cyl_type}'; " \
                        f"UPDATE dbo.cylinders_orders SET stocks_counted = 1 where po = {po}; "

            if part == 'cylinder':
                if int(start_date) <= 0:
                    query = f"UPDATE dbo.cylinders_stock SET sleeves_pcs = sleeves_pcs - {pcs}, " \
                            f"flanges_pcs =  flanges_pcs - {pcs} WHERE cylinder_type = '{cyl_type}'; " \
                            f"UPDATE dbo.cylinders_orders SET stocks_counted = 1 where po = {po}; "
            if query:
                db_commit(query, func_name='po_cylinder_recouter')
                query = ""
    return None


def po_cylinder_multiplied_setter(arg):
    query = f"UPDATE cylinders_orders SET multiplied = 1 " \
            f"WHERE PO = {arg}"
    db_commit(query, func_name='po_drawing_multiplied_setter')

def cylinder_drawing_handler():
    drawings_data = cylinder_info_getter('ORPHAN_DRAWINGS_CYLINDER')  # wyszukiwanie nieobsłużonych rysunków pump blocków
    if not drawings_data:
        return
    cylinder_id = cylinder_info_getter('ID')
    num = 0
    for draw_id, draw, po, pcs in drawings_data:
        if CylinderPartsNumber.draw_cyinder.get(draw) == 'CYLINDER_MAIN':
            try:
                main_draw_rename(draw, po, cylinder_id)
            except PermissionError:
                return
        cylinder_tech_setter(draw_id, draw, cylinder_id)
        drawing_multiplier(draw_id, draw, po, pcs, cylinder_id, 'cylinder_drawing_handler')
        po_cylinder_multiplied_setter(po)
        if CylinderPartsNumber.draw_cyinder.get(draw) == 'CYLINDER_MAIN':
            cylinder_id = cylinder_id + pcs
            num = num + pcs
    if num:
        cylinder_id_updater(num)

def drawing_multiplier(draw_id, draw, po, pcs, item_id, func):
    if CylinderPartsNumber.draw_cyinder.get(draw) != 'CYLINDER_MAIN':
        return None
    query = ''
    item = item_id + 1
    for i in range(pcs - 1):
        if not copy_draw_file(draw, po, item_id, item):
            break
        now = str(datetime.fromtimestamp(time.time(), ))[0:-3]
        query = f"{query} INSERT INTO TECHNOLOGIA (RYSUNEK, PO, Sztuki, Materiał, OP_1, OP_2, OP_3, OP_4, OP_5, " \
            f"OP_6, OP_7, OP_8, OP_9, OP_10, OP0, OP1, Status_op, Stat, Liczba_Operacji, Plik, Kiedy) " \
            f"SELECT CONCAT('{draw}', '{hash_cyl_id(item, 'CYLINDER_MAIN' )}'), PO, Sztuki, Materiał, OP_1, OP_2, OP_3, OP_4, " \
            f"OP_5, OP_6, OP_7, OP_8, OP_9, OP_10, OP0, OP1, Status_op, Stat, Liczba_Operacji, " \
            f"CONCAT('{po}', ' ', '{draw}', '{hash_cyl_id(item, 'CYLINDER_MAIN')}'), '{now}' " \
            f"FROM TECHNOLOGIA WHERE ID = {draw_id}"
        item = item + 1
    if query:
        db_commit(query=query, func_name=func)

def part_getter(device_name):
    if 'sleeve' in device_name.lower():
        return 'sleeve', 0
    elif 'flange' in device_name.lower():
        return 'flange', 0
    else:
        return 'cylinder', 0

def cylinder_id_updater(num):
    if not num:
        return
    db_commit(f'UPDATE cylinders_identifier set cylinder_id_val = cylinder_id_val + {num}', func_name='cyl_id_updater')
    return None

def type_getter(device_name):

    device_name = device_name.split('_')[-1]
    if 'CF500' == device_name:
        return 'CF500'
    if 'CF1000' == device_name:
        return 'CF1000'
    if device_name in ('CF2000', 'CF2-3000') :
        return 'CF2000'
    if 'CF3000' == device_name:
        return 'CF3000'
    if 'CF4000' == device_name:
        return 'CF4000'

def cylinder_info_getter(arg):
    single_val = ['ID']
    match arg:
        case 'new':
            query = 'SELECT * FROM dbo.new_cylinder_orders()'
        case 'recount':
            query = "Select si.[S], co.po, co.pcs, co.part, co.type, co.name from dbo.cylinders_orders co " \
                    "left join SAP_Basic_Info() si on co.po = si.[p.o.] where co.stocks_counted =0;"
        case 'cyl_orders':
            query = "SELECT po, pcs FROM dbo.cylinders_orders where part = 'cylinder' ORDER BY start_date;"
        case 'ID':
            query = "SELECT cylinder_id_val FROM cylinders_identifier; "
        case 'ORPHAN_DRAWINGS_CYLINDER':
            query = "SELECT T.id, T.Rysunek, T.PO, P.pcs from TECHNOLOGIA T " \
                    "RIGHT JOIN ( " \
                    "SELECT PO, pcs FROM dbo.cylinders_orders WHERE multiplied = 0 ) P " \
                    "ON T.[PO] = P.PO " \
                    "WHERE T.Status_Op = 6 " \
                    "ORDER BY T.ID;"
        # ---------------------------------------------

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

def hash_cyl_id(num: int, draw_type: str):
    if draw_type == 'CYLINDER_MAIN':
        return f" #{num:0>4}"
    else:
        return ''

def main_draw_rename(draw, po, item_id):
    old_name = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw}.pdf')
    new_name = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw}{hash_cyl_id(item_id, 'CYLINDER_MAIN')}.pdf')
    try:
        os.rename(old_name, new_name)
        # shutil.copyfile(old_name, new_name)
    except FileNotFoundError:
        print(f'Aint no such file {old_name}')
        return None
    except PermissionError:
        print(f'File locked {old_name}')
        return None
    return True

def start_stock():

    for cyl_type in CylindersData.cyl_types:
        query = f"INSERT INTO CYLINDERS_STOCK VALUES ('{cyl_type}', 0,0,0);"
        db_commit(query, func_name='start_stock')
        print(query)

def reset_cylinder_base():
    db_commit('DELETE FROM dbo.cylinders_orders; DELETE FROM dbo.cylinders_stock; ', func_name='reset_cylinder_base')
    start_stock()
    po_cylinder_recorder()
    po_cylinder_recounter()

def init_id():
    adder = 0
    pos = []
    query = "UPDATE dbo.cylinders_orders SET multiplied = 1 WHERE po in ("
    for po, pcs in cylinder_info_getter('cyl_orders'):
        pos.append(str(po))
        query += f"{po},"
        adder += int(pcs)
    query += f"{', '.join(pos)}); "
    query += f"UPDATE cylinders_identifier SET cylinder_id_val = {adder + 1};"
    db_commit(query, func_name='init_stock')

def main():
    po_cylinder_recounter()
    cylinder_drawing_handler()


if __name__ == '__main__':
    # reset_cylinder_base()
    main()

