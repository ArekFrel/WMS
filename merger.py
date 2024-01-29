import os
import fitz
from stat import S_IWRITE
from const import CURSOR, MERGED_MIN, db_commit
from pyodbc import Error, OperationalError
from const import PRODUCTION


def get_orders_to_merge():
    """Orders that should be merged are stored in table OTM in data base."""
    query = f"SELECT po FROM OTM WHERE quantity >= {MERGED_MIN} AND merged = 0;"
    return get_data(query)


def get_drawings_to_merge(order):
    num = how_many_drawings_to_merge(order)
    query = f"Select TOP ({num}) Plik from Technologia " \
            f"where PO = {order} " \
            f"AND Rysunek NOT LIKE '%SAP%' And Rysunek NOT LIKE '%INFO%' " \
            f"ORDER BY Kiedy DESC;"
    drawings = get_data(query)
    drawings.sort()
    return drawings


def how_many_drawings_to_merge(order):
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

    orders = get_orders_to_merge()
    for order in orders:
        count = 0
        order_path = os.path.join(PRODUCTION, order)
        drawings = [f'{drawing}.pdf' for drawing in get_drawings_to_merge(order)]
        first_drawing = drawings[0]
        first_drawing_path = os.path.join(order_path, first_drawing)
        drawings = enumerate(drawings)
        merge_name = merged_name_available(order_path)
        merged_doc = os.path.join(order_path, f'{order} {merge_name}')
        with fitz.open(first_drawing_path) as doc:
            count += 1
            for index, drawing in drawings:
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
        print(f'{count} drawings of {order} order drawings has been merged.')


def main():
    merging()


if __name__ == '__main__':
    main()
