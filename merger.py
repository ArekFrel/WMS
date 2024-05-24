import os
import fitz
from stat import S_IWRITE
from const import CURSOR, MERGED_MIN, db_commit, IS_IT_TEST, TEST_RETURN_ORDERS, TEST_RETURN_NUM, TEST_RETURN_DRAWINGS
from pyodbc import Error, OperationalError
from const import Paths


def get_orders_to_merge():
    """Orders that should be merged are stored in table OTM in data base."""
    if IS_IT_TEST: # this one is turned off fo test
        return TEST_RETURN_ORDERS # this one is turned off fo test
    query = f"SELECT po FROM OTM WHERE quantity >= {MERGED_MIN} AND merged = 0;"
    return get_data(query)


def get_drawings_to_merge(order):
    if IS_IT_TEST:
        return TEST_RETURN_DRAWINGS
    num = how_many_drawings_to_merge(order)
    query = f"SELECT * FROM ("\
            f"Select TOP ({num}) Plik from Technologia " \
            f"where PO = {order} " \
            f"AND Rysunek NOT LIKE '%SAP%' And Rysunek NOT LIKE '%INFO%' " \
            f"ORDER BY Kiedy DESC) AS subquery " \
            f"ORDER BY Plik;"
    result = get_data(query)

    return result


def how_many_drawings_to_merge(order):
    if IS_IT_TEST:
        return TEST_RETURN_NUM
    query = f"SELECT quantity FROM OTM WHERE PO = {order}"
    return int(get_data(query)[0])


def get_data(query):
    try:
        with CURSOR:
            CURSOR.execute(query)
            result = CURSOR.fetchall()
    except Error:
        print(f'Database Error in "merging"')
        return []
    except OperationalError:
        print(f'Operational Error in merging')
        return []
    return [str(_[0]) for _ in result]


def merged_name_available(path):
    num = len([_ for _ in os.listdir(path) if "merged" in _])
    return f'merged.pdf' if num == 0 else f'merged_{num}.pdf'


def set_merged_true(order):
    query = f'UPDATE OTM SET quantity = 0, merged = 1 WHERE PO = {order};'
    db_commit(query=query, func_name='set_merged_pos')


def merging():
    for order in get_orders_to_merge():
        order_path = os.path.join(Paths.PRODUCTION, order)
        drawings = [f'{drawing}.pdf' for drawing in get_drawings_to_merge(order)]
        drawings = update_drawings_list(drawings, order)
        first_drawing_path = os.path.join(order_path, drawings[0])
        merge_name = merged_name_available(order_path)
        merged_doc = os.path.join(order_path, f'{order} {merge_name}')
        if not os.path.exists(first_drawing_path):
            continue
        with fitz.open(first_drawing_path) as doc:
            count = 1
            for index, drawing in enumerate(drawings):
                if index == 0:
                    continue
                drawing_path = os.path.join(order_path, drawing)
                if not os.path.isfile(drawing_path):
                    continue
                with fitz.open(drawing_path) as added_doc:
                    doc.insert_file(added_doc)
                    count += 1

            doc.save(merged_doc)
            os.chmod(merged_doc, S_IWRITE)

        set_merged_true(order=order)
        print(f'{count} drawings of {order} order has been merged.')


def update_drawings_list(drawings, order):
    # Return actual list of drawings
    # result = sorted(list(set(drawings).intersection(set(os.listdir(os.path.join(Paths.PRODUCTION, order))))))
    result = [drawing for drawing in drawings if drawing in os.listdir(os.path.join(Paths.PRODUCTION, order))]
    return sorted(result)


def main():
    if 'bought_script' not in os.listdir(Paths.START_CATALOG):
        merging()


if __name__ == '__main__':
    main()
