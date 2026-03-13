import os

import fitz
import shutil
from datetime import datetime, time, date

from sqlalchemy.testing.config import test_schema_2

from wms_main.const import *
from utils.cylinders_tracker.cylinders_data import *
from utils.cylinders_tracker.cylinders_technology import *
from utils.pump_block_tracker.pb_tracker import copy_draw_file
from pyodbc import Error, DataError, OperationalError

'''
TODO:
    -CYLINDER MAIN MERGINNG
    -CYLINDER MAIN MULTIPLYING
'''
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
            f"Plik = CONCAT(PO, ' ', Rysunek, '{hash_num}')" \
            f"WHERE ID = {draw_id}"
    db_commit(query=query, func_name='cylinder_tech_setter')

def cylinder_drawing_merger(po, new_name, draw):

    def get_file_path(drawing):
        return os.path.join(Paths.PRODUCTION, str(po), f'{str(po)} {drawing}.pdf')

    cyl_type = CylinderPartsNumber.main_draw_types.get(draw)
    tube_draw = CylinderPartsNumber.DICT_CYLINDER.get(f'{cyl_type}-tube')
    weld_draw = CylinderPartsNumber.DICT_CYLINDER.get(f'{cyl_type}-welding')
    doc_1 = get_file_path(tube_draw)
    doc_2 = get_file_path(weld_draw)
    temp_name = get_file_path('cyl_temp_file')

    # drawing merging:
    with fitz.open(doc_1) as doc:
        doc.insert_file(doc_2)
        doc.insert_file(new_name)
        doc.save(temp_name)
    for file in (doc_1, doc_2, new_name):
        os.remove(file)
    # files removing
    os.rename(temp_name, new_name)
    os.chmod(new_name, S_IWRITE)

    #deleting from database
    query = f"DELETE FROM TECHNOLOGIA WHERE po = {po} AND rysunek in ('{tube_draw}', '{weld_draw}')"
    db_commit(query=query, func_name='cylinder_drawing_merger')

    #deleting from otm
    for file in os.listdir(os.path.join(Paths.PRODUCTION, str(po))):
        if 'merged' in file:
            os.remove(os.path.join(Paths.PRODUCTION, str(po), file))


def po_cylinder_recorder():

    po_to_record = cylinder_info_getter('new')  # Select new cylinder orders
    for row in po_to_record:
        po, start_date, device, planner, pcs, status = row
        part = part_getter(device)
        cyl_type = type_getter(device)

        query = f"INSERT INTO cylinders_orders VALUES ({po}, {pcs}, '{part}', '{cyl_type}', '{device}', " \
                f" 0, 0, 0, 0); "   #technology_set, stocks_counted, multiplied, merged
        if db_commit(query, func_name='po_cylinders_recorder'):
            print(f"order {po} added.")

    po_cylinder_recounter()

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
                db_commit(query, func_name='po_cylinder_recounter')
                query = ""
    return None


def po_cylinder_multiplied_setter(arg):
    query = f"UPDATE cylinders_orders SET multiplied = 1 " \
            f"WHERE PO = {arg} ;" \
            f"UPDATE OTM SET merged = 1 WHERE PO = {arg};"# added
    db_commit(query, func_name='po_drawing_multiplied_setter')

def po_cylinder_tech_done_setter(arg):
    query = f"UPDATE cylinders_orders SET technology_set = 1 " \
            f"WHERE PO = {arg}"
    db_commit(query, func_name='po_drawing_tech_setter')

def cylinder_drawing_handler():
    drawings_data = cylinder_info_getter('ORPHAN_DRAWINGS_CYLINDER')  # wyszukiwanie nieobsłużonych rysunków cylindrów
    if not drawings_data:
        return
    cylinder_id = cylinder_info_getter('ID')
    num = 0
    for draw_id, draw, po, pcs in drawings_data:
        if CylinderPartsNumber.draw_cyinder.get(draw) in (
                'CYLINDER_TUBE','CYLINDERS_WELDING'):
            continue
        if CylinderPartsNumber.draw_cyinder.get(draw) == 'CYLINDER_MAIN':
            do_proceed, new_name = main_draw_rename(draw, po, cylinder_id)
            if do_proceed:
                cylinder_drawing_merger(po, new_name, draw)
            else:
                break
        cylinder_tech_setter(draw_id, draw, cylinder_id)
        if CylinderPartsNumber.draw_cyinder.get(draw) == 'CYLINDER_MAIN':
            drawing_multiplier(draw_id, draw, po, pcs, cylinder_id, 'cylinder_drawing_handler')
            lb_signer_auto(po, draw)
            cylinder_id = cylinder_id + pcs
            num = num + pcs
        po_cylinder_multiplied_setter(po)
        po_cylinder_tech_done_setter(po)

    if num:
        cylinder_id_updater(num)

def drawing_multiplier(draw_id, draw, po, pcs, item_id, func):

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

def lb_signer_orphan():
    """
    Signing missing main_cylinders with lb_numbers
    """

    test_ids = cylinder_info_getter('cylinders_without_lb')
    for tech_id, drawing in test_ids:
        cyl_type = CylinderPartsNumber.main_draw_types.get(drawing.split(' ')[0])
        query_lb = f"SELECT TOP(1) ID FROM lb_nums_cylinders WHERE " \
                   f"cylinder_type = '{cyl_type}' AND used_in_tech IS NULL ORDER BY ID ASC"
        query_sign = f"UPDATE lb_nums_cylinders SET used_in_tech = {tech_id} " \
                     f"WHERE id = ({query_lb}) "
        db_commit(query_sign, func_name='lb_signer')
    return None


def lb_signer_auto(po, draw):
    """
    Launched during cylinder_drawing_handler() wchich is launched by adding_new_files_class().
    Normally takes po and drawing number as parameter.
    Combines free lb numbers with proper Cylinders added to production.
    """
    cyl_type = CylinderPartsNumber.main_draw_types.get(draw)
    query_po = f"SELECT id FROM TECHNOLOGIA WHERE PO = {po} AND Rysunek LIKE '%#%'"
    query_lb = f"SELECT TOP(1) ID FROM lb_nums_cylinders WHERE " \
                                  f"cylinder_type = '{cyl_type}' AND used_in_tech IS NULL ORDER BY ID ASC"
    count_query = f"SELECT count(ID) FROM lb_nums_cylinders WHERE cylinder_type = '{cyl_type}'" \
                  " AND used_in_tech IS NULL"

    free_lbs = db_commit_getval(count_query)
    ids = cylinder_info_getter(arg=query_po, query_arg=1)
    for i, tech_id in enumerate(ids, 1):
        if i > free_lbs:
            break
        query_sign = f"UPDATE lb_nums_cylinders SET used_in_tech = {tech_id} " \
                     f"WHERE id = ({query_lb}) "
        db_commit(query_sign, func_name='lb_signer')

def part_getter(device_name):
    if 'sleeve' in device_name.lower():
        return 'sleeve'
    elif 'flange' in device_name.lower():
        return 'flange'
    else:
        return 'cylinder'

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

def cylinder_info_getter(arg, query_arg=0):
    single_val = ['ID']
    if not query_arg:
        match arg:
            case 'new':
                query = 'SELECT * FROM dbo.new_cylinder_orders()'
            case 'orders_to_merge':
                query = 'SELECT * FROM cylinders_orders WHERE merged = 0;'
            case 'recount':
                query = "Select si.[S], co.po, co.pcs, co.part, co.type, co.name from dbo.cylinders_orders co " \
                        "left join SAP_Basic_Info() si on co.po = si.[p.o.] where co.stocks_counted = 0;"
            case 'cyl_orders':
                query = "SELECT po, pcs FROM dbo.cylinders_orders where part = 'cylinder' ORDER BY start_date;"
            case 'ID':
                query = "SELECT cylinder_id_val FROM cylinders_identifier; "
            case 'ORPHAN_DRAWINGS_CYLINDER':
                query = "SELECT T.id, T.Rysunek, T.PO, P.pcs FROM TECHNOLOGIA T " \
                        "RIGHT JOIN ( " \
                        "SELECT PO, pcs FROM dbo.cylinders_orders WHERE multiplied = 0 or technology_set = 0 ) P " \
                        "ON T.[PO] = P.PO " \
                        "WHERE T.Status_Op != 8 " \
                        "ORDER BY T.ID;"
            case 'cylinders_without_lb':
                query = f"SELECT T.id, T.Rysunek  " \
	                    f"FROM TECHNOLOGIA T " \
	                    f"RIGHT JOIN dbo.cylinders_orders P ON T.[PO] = p.PO " \
	                    f"LEFT JOIN lb_nums_cylinders LB ON T.id = LB.used_in_tech  " \
	                    f"WHERE t.Rysunek like '%#%' and T.id > 113745 " \
		                f"AND lb.ID IS NULL " \
		                f"AND T.Stat = 0 " \
	                    f"ORDER BY T.ID "


        # ---------------------------------------------
            case _:
                return None
    if query_arg:
        query = arg
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

def main_draw_rename(draw, po, item_id) -> tuple:
    old_name = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw}.pdf')
    new_name = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw}{hash_cyl_id(item_id, 'CYLINDER_MAIN')}.pdf')
    try:
        os.rename(old_name, new_name)
        # shutil.copyfile(old_name, new_name)
    except FileNotFoundError:
        print(f'Aint no such file {old_name}')
        return False, False
    except PermissionError:
        shutil.copyfile(old_name, new_name)
        query = f"INSERT INTO files_to_delete VALUES ('{old_name}')"
        db_commit(query, 'inserting into files_to_delete')
        print(f'File locked {old_name}')

    return True, new_name

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
    # po_cylinder_recorder()
    # po_cylinder_recounter()
    lb_signer_orphan()


if __name__ == '__main__':
    main()

