import shutil
from datetime import datetime, time, date
from wms_main.const import *
from cylinders_data import *
from utils.pump_block_tracker.pb_tracker import copy_draw_file, hash_id, main_draw_rename, drawing_multiplier
from pyodbc import Error, DataError, OperationalError

def cylinder_tech_setter(draw_id, pb_id, type):
    pass

def new_po_cylinder_recorder():

    po_to_record = cylinder_info_getter('new')  # Select new pumpblock orders
    for row in po_to_record:
        po, start_date, device, planner, pcs, status = row
        part, multiplied = part_getter(device)
        cyl_type = type_getter(device)

        query = f"INSERT INTO cylinders_orders VALUES ({po}, '{start_date}',{pcs}, '{part}', '{cyl_type}', '{device}', " \
                f"'{status}', 0, {multiplied}); "
        db_commit(query, func_name='po_cylinders_recorder')
        print(f"order {po} added.")

def po_cylinder_recounter():

    records = cylinder_info_getter('recount')
    if records:
        query = ""
        for record in records:
            po, start_date ,pcs, part, cyl_type, status = record

            if part in ('sleeve', 'flange') and status == 'TECO':
                query = f"UPDATE dbo.cylinders_stock SET {part}s_pcs = {part}s_pcs + {pcs} WHERE cylinder_type = '{cyl_type}'; " \
                        f"UPDATE dbo.cylinders_orders SET stocks_counted = 1 where po = {po}; "

            if part == 'cylinder':
                if (date.today() - datetime.strptime(str(start_date), "%Y-%m-%d").date()).days >= 0:
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
    po_drawings_data = cylinder_info_getter('ORPHAN_DRAWINGS')  # wyszukiwanie nieobsłużonych rysunków pump blocków
    if not po_drawings_data:
        return
    cylinder_id = cylinder_info_getter('ID')
    num = 0
    for draw_id, draw, po, pcs in po_drawings_data:
        if not main_draw_rename(draw, po, cylinder_id):
            break
        cylinder_tech_setter(draw_id, cylinder_id)
        drawing_multiplier(draw_id, draw, po, pcs, cylinder_id, 'cylinder_drawing_handler')
        po_cylinder_multiplied_setter(po)
        cylinder_id = cylinder_id + pcs
        num = num + pcs
    if num:
        cylinder_id_updater(num)

def part_getter(device_name):
    if 'sleeve' in device_name.lower():
        return 'sleeve', 'NULL'
    elif 'flange' in device_name.lower():
        return 'flange', 'NULL'
    else:
        return 'cylinder', 0

def cylinder_id_updater(num):
    if not num:
        return
    db_commit(f'UPDATE pb_identifier set pb_id_val = pb_id_val + {num}', func_name='pb_id_updater')
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
            query = 'SELECT po, start_date, pcs, part, type, status FROM dbo.cylinders_orders where stocks_counted = 0;'
        case 'cyl_orders':
            query = "SELECT po, pcs FROM dbo.cylinders_orders where part = 'cylinder' ORDER BY start_date;"
        case 'ID':
            query = "SELECT cylinder_id_val FROM cylinders_identifier; "
        case 'ORPHAN_DRAWINGS_CYLINDER':
            query = "SELECT T.id, T.Rysunek, T.PO, P.pcs from TECHNOLOGIA T " \
                    "RIGHT JOIN ( " \
                    "SELECT PO, pcs FROM dbo.cylinders_orders WHERE (multiplied = 0 and part ='cylinder')) P " \
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

def start_stock():

    for cyl_type in CylindersData.cyl_types:
        query = f"INSERT INTO CYLINDERS_STOCK VALUES ('{cyl_type}', 0,0,0);"
        db_commit(query, func_name='start_stock')
        print(query)

def reset_cylinder_base():
    db_commit('DELETE FROM dbo.cylinders_orders; DELETE FROM dbo.cylinders_stock; ')
    start_stock()
    new_po_cylinder_recorder()
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
    cylinder_drawing_handler()

if __name__ == '__main__':
    reset_cylinder_base()
    main()
