import fitz
import shutil
from datetime import time
from wms_main.const import *
from utils.cylinders_tracker.cylinders_data import *
from utils.cylinders_tracker.cylinders_technology import *
from pyodbc import Error, DataError, OperationalError

from wms_main.teco_completer import print_red


def cylinder_drawing_handler():
    """
    Main function of the module.
    """
    drawings_data = cylinder_info_getter('ORPHAN_DRAWINGS_CYLINDER')  # wyszukiwanie nieobsłużonych rysunków cylindrów
    if not drawings_data:
        return

    for draw_id, draw, po, pcs in drawings_data:
        if CylinderPartsNumber.draw_cyinder.get(draw) in (
                'CYLINDER_TUBE','CYLINDERS_WELDING', 'CYLINDER_HONING'):
            continue
        if CylinderPartsNumber.draw_cyinder.get(draw) == 'CYLINDER_MAIN':
            new_name = None
            cyl_type = CylinderPartsNumber.main_draw_types.get(draw)
            lbs = lb_getter(cyl_type, pcs)
            if len(lbs) < pcs:
                print(f"Brak wolnych numerów LB!")
                continue
            try:
                lb = lbs.pop(0)
            except IndexError:
                print(f"Brak wolnych numerów LB!")
                return
            do_proceed, new_name, new_path = main_draw_rename(draw, po, lb)
            if do_proceed:
                cylinder_drawing_merger(po, new_path, draw)
                lb_signer_single(new_name)
            else:
                break
            cylinder_tech_setter(draw_id, draw, new_name)
            if pcs == 1:
                continue
            drawing_multiplier(draw_id, new_name, po, pcs, lbs)
        else:
            cylinder_tech_setter(draw_id=draw_id, draw=draw)

        po_cylinder_multiplied_setter(po)
        po_cylinder_tech_done_setter(po)


def copy_draw_file(draw, po, lb_dest):
    base_file = os.path.join(Paths.PRODUCTION, str(po), f'{draw}.pdf')
    new_file = os.path.join(Paths.PRODUCTION, str(po), f'{draw.split('__')[0]}__{lb_dest}.pdf')
    try:
        shutil.copyfile(base_file, new_file)
    except FileNotFoundError:
        print(f'Aint no such file {base_file}')
        return None
    return True

def cylinder_tech_setter(draw_id, draw, new_name=None):

    tech_route = CylinderTechnology(draw)
    if not new_name:
        new_name = draw
    else:
        new_name = new_name.split(' ')[1]
    # hash_num = hash_cyl_id(cylinder_id, tech_route.draw_type)
    query = f"UPDATE TECHNOLOGIA SET " \
            f"Rysunek = '{new_name}', " \
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
            f"Plik = CONCAT( PO, ' ', '{new_name}') " \
            f"WHERE ID = {draw_id};"
    db_commit(query=query, func_name='cylinder_tech_setter')

def cylinder_drawing_merger(po, new_name, draw):

    def get_file_path(drawing):
        return os.path.join(Paths.PRODUCTION, str(po), f'{str(po)} {drawing}.pdf')

    cyl_type = CylinderPartsNumber.main_draw_types.get(draw)
    tube_draw = CylinderPartsNumber.DICT_CYLINDER.get(f'{cyl_type}-tube')
    weld_draw = CylinderPartsNumber.DICT_CYLINDER.get(f'{cyl_type}-welding')
    hone_draw = CylinderPartsNumber.DICT_CYLINDER.get(f'{cyl_type}-honing')
    doc_1 = get_file_path(tube_draw)
    doc_2 = get_file_path(weld_draw)
    doc_3 = get_file_path(hone_draw)
    temp_name = get_file_path('cyl_temp_file')

    # drawing merging:
    with fitz.open(doc_1) as doc:
        doc.insert_file(doc_2)
        doc.insert_file(new_name)
        if os.path.exists(doc_3):
            doc.insert_file(doc_3)
        else:
            register(f'{draw} missing hone drawing {hone_draw}. - merge skipped')
        doc.save(temp_name)
    for file in (doc_1, doc_2, new_name, doc_3):
        try:
            os.remove(file)
        except FileNotFoundError:
            register(f'{file} missing - removal skipped')
    # files removing
    os.rename(temp_name, new_name)
    os.chmod(new_name, S_IWRITE)

    #deleting from database
    query = f"DELETE FROM TECHNOLOGIA WHERE po = {po} AND rysunek in ('{tube_draw}', '{weld_draw}', '{hone_draw}'); "
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
                f" 0, 0, 0); " \
                f"DELETE FROM OTM WHERE PO = {po}; " \
                f"INSERT INTO files_to_delete VALUES ('{os.path.join(Paths.PRODUCTION, str(po), f'{po} merged.pdf')}'); "
                #added - not tested

        if db_commit(query, func_name='po_cylinders_recorder'):
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

                try:
                    if int(start_date) <= 0:
                        query = f"UPDATE dbo.cylinders_stock SET sleeves_pcs = sleeves_pcs - {pcs}, " \
                                f"flanges_pcs =  flanges_pcs - {pcs} WHERE cylinder_type = '{cyl_type}'; " \
                                f"UPDATE dbo.cylinders_orders SET stocks_counted = 1 where po = {po}; "
                except TypeError:
                    register(f'TypeError: {datetime.now()}, {po}, {cyl_type}')
                    print_red("Error occured, loged in.")
                    continue
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


def lb_getter(cyl_type, pcs):
    """Selects from lb_nums_cylinders anly passed and not used tubes"""

    if cyl_type == 'CF3000':
        cyl_type = 'CF2000'

    query = f"SELECT TOP({pcs}) lb_num FROM lb_nums_cylinders WHERE cylinder_type = '{cyl_type}' " \
            f" AND used_in_tech is NULL AND passed = 1 order by id;"
    lbs = cylinder_info_getter(arg=query, query_arg=1)
    return lbs

def drawing_multiplier(draw_id: int, draw: str, po:int, pcs: int, lbs):

    sent = 0 #used if number of cylinders is higher than free lb numbers
    if not lbs:
        return
    for lb in lbs:
        if not copy_draw_file(draw, po, lb):
            return sent
        po, draw_part = draw.split(' ')
        new_draw = draw_part.split('__')[0]
        now = str(datetime.fromtimestamp(time.time(), ))[0:-3]
        query = f"INSERT INTO TECHNOLOGIA (RYSUNEK, PO, Sztuki, Materiał, OP_1, OP_2, OP_3, OP_4, OP_5, " \
            f"OP_6, OP_7, OP_8, OP_9, OP_10, OP0, OP1, Status_op, Stat, Liczba_Operacji, Plik, Kiedy) " \
            f"SELECT CONCAT('{new_draw}', '__{lb}'), PO, Sztuki, Materiał, OP_1, OP_2, OP_3, OP_4, " \
            f"OP_5, OP_6, OP_7, OP_8, OP_9, OP_10, OP0, OP1, Status_op, Stat, Liczba_Operacji, " \
            f"CONCAT('{po}', ' ', '{new_draw}', '__{lb}'), '{now}' " \
            f"FROM TECHNOLOGIA WHERE ID = {draw_id};"
        db_commit(query=query, func_name='drawing multiplier')
        lb_signer_single(draw=f'{po} {new_draw}__{lb}')
        sent += 1
    return pcs - 1


def lb_signer_single(draw):
    """
    As a parameter received new name rysunek from Technologia, extract lb number and sing accordingly.
    Applied with version 1.13.
    """

    idquery = f"SELECT id FROM technologia WHERE plik = '{draw}'"
    # idquery - query for just created recrod in technologia (drawing__lb)
    lb = draw.split('__')[1]
    try:
        query_sign = f"UPDATE lb_nums_cylinders SET used_in_tech = ({idquery}) " \
                     f"WHERE lb_num = '{lb}'; "
        db_commit(query_sign, func_name='lb_signer')
    except IndexError:
        print("Niepoprawny parametr draw.")
    return True

def part_getter(device_name):
    if 'sleeve' in device_name.lower():
        return 'sleeve'
    elif 'flange' in device_name.lower():
        return 'flange'
    else:
        return 'cylinder'

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
    return ''

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

def main_draw_rename(draw, po, lb) -> tuple:
    old_name = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw}.pdf')
    new_name = os.path.join(Paths.PRODUCTION, str(po), f'{po} {draw}__{lb}.pdf')
    query = f"UPDATE Technologia SET rysunek = '{draw}__{lb}', plik = '{po} {draw}__{lb}'" \
            f"WHERE rysunek = '{draw}' AND po = {po};"
    try:
        os.rename(old_name, new_name)
        # shutil.copyfile(old_name, new_name)
    except FileNotFoundError:
        print(f'Aint no such file {old_name}, main_draw_name')
        return False, None, None
    except FileNotFoundError:
        print(f'Aint no such file {old_name}, main_draw_name')
        return False, None, None
    except FileExistsError:
        print(f'{new_name} already exists.')
    except PermissionError:
        shutil.copyfile(old_name, new_name)
        query = f"INSERT INTO files_to_delete VALUES ('{old_name}')"
        db_commit(query, 'inserting into files_to_delete')
        print(f'File locked {old_name}')

    db_commit(query, 'main_draw_rename')
    return True, f'{po} {draw}__{lb}', new_name

def start_stock():

    for cyl_type in CylindersData.cyl_types:
        query = f"INSERT INTO CYLINDERS_STOCK VALUES ('{cyl_type}', 0,0,0);"
        db_commit(query, func_name='start_stock')
        print(query)

def reset_cylinder_base():
    db_commit('DELETE FROM dbo.cylinders_stock; ', func_name='reset_cylinder_base')
    start_stock()
    # po_cylinder_recorder()
    po_cylinder_recounter()

"""Obsolete functions below:"""
def lb_signer_orphan():
    """
    Signing missing main_cylinders with lb_numbers
    In version 1.13 not used, to be verified if this is necessary.
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

def main():
    cylinder_drawing_handler()
    pass
if __name__ == '__main__':
    main()

