import os
import fitz
from stat import S_IWRITE
from const import CURSOR, MERGED_MIN, MERGED_TIME_PERIOD, PRODUCTION, db_commit
from pyodbc import Error
from const import PRODUCTION


def get_orders_to_merge():
    query = f"SELECT po FROM OTM WHERE quantity >= {MERGED_MIN} AND merged = 0;"
    return get_data(query)


def get_drawings_to_merge(order):
    query = f"Select Plik from Technologia " \
            f"where PO = {order} " \
            f"AND (datediff(minute, kiedy, getdate())) < {MERGED_TIME_PERIOD} " \
            f"AND Rysunek NOT LIKE '%SAP%' And Rysunek NOT LIKE '%INFO%';"
    # print(query)
    # return [x[0:-4] for x in os.listdir(os.path.join(PRODUCTION, order)) if 'merged' not in x]
    return get_data(query)


def get_data(query):
    with CURSOR:
        try:
            CURSOR.execute(query)
            result = CURSOR.fetchall()

        except Error:
            print(f'Database Error in "merging"')
            return False

    return [str(_[0]) for _ in result]


def merged_name_available(path):
    num = len([_ for _ in os.listdir(path) if "merged" in _])
    # print(f'{num} --  merged name available')
    return f'merged.pdf' if num == 0 else f'merged_{num}.pdf'


def set_merged_pos(order):
    query = f'UPDATE OTM SET quantity = 0, merged = 1 WHERE PO = {order};'
    db_commit(query=query, func_name='set_merged_pos')


def merging():

    orders = get_orders_to_merge()
    for order in orders:
        count = 0
        drawings = [f'{drawing}.pdf' for drawing in get_drawings_to_merge(order)]
        # print(order, " -------- order")
        order_path = os.path.join(PRODUCTION, order)
        # print(order_path, " -------- order")
        merge_name = merged_name_available(order_path)
        # print(f'{merge_name} ------------ merge_name')

        for drawing in drawings:
            drawing_path = os.path.join(order_path, drawing)
            merged_doc = os.path.join(order_path, f'{order} {merge_name}')
            save_doc = os.path.join(order_path, 'merged_temp.pdf')
            with fitz.open(drawing_path) as doc:
                if f'{order} {merge_name}' not in os.listdir(order_path):
                    doc.save(merged_doc)
                    os.chmod(merged_doc, S_IWRITE)
                    count += 1
                else:
                    with fitz.open(merged_doc) as doc_merged:
                        doc_merged.insert_file(doc)
                        doc_merged.save(save_doc)
                        # print(merged_doc, 'save merging.pdf ')
                        os.chmod(save_doc, S_IWRITE)
                    os.remove(merged_doc)
                    os.rename(save_doc, merged_doc)
                    count += 1
        set_merged_pos(order=order)
        print(f'{order} order drawings has been maerged ')


def main():
    merging()


if __name__ == '__main__':
    main()


