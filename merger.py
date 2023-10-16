import os
# import fitz
from stat import S_IWRITE
from const import CURSOR, MERGED_MIN
from pyodbc import Error
catalog = 'C:/Dokumenty/sat/1__Rysunki/'


def get_orders_to_merge():
    query = f"SELECT po FROM OTM WHERE quantity > {MERGED_MIN} AND merged = 0;"
    return get_data(query)


def get_drawings_to_merge(order):
    query = f"Select Rysunek from Technologia " \
            f"where PO = {order} " \
            f"AND (datediff(minute, kiedy, getdate())) < 30000 " \
            f"AND Rysunek NOT LIKE '%SAP%' And Rysunek NOT LIKE '%INFO%';"
    print(query)
    return get_data(query)


def get_data(query):
    with CURSOR:
        try:
            CURSOR.execute(query)
            result = CURSOR.fetchall()

        except Error:
            print(f'Database Error in "merging"')
            return False

    return [_[0] for _ in result]


def merged_name_available(path):
    num = len([_ for _ in os.listdir(path) if "merged" in _])
    print(f'{num} --  merged name available')
    return f'merged.pdf' if num == 0 else f'merged_{num}.pdf'


def merging():

    orders = get_orders_to_merge()
    for order in orders:
        drawings = get_drawings_to_merge(order)
        order_path = os.path.join(catalog, order)
        merge_name = merged_name_available(order_path)

        for drawing in drawings:
            drawing_path = os.path.join(order_path, drawing)
            merged_doc = os.path.join(order_path, f'{order} {merge_name}')
            save_doc = os.path.join(order_path, 'merged_temp.pdf')
            with fitz.open(drawing_path) as doc:
                if f'{order} {merge_name}' not in os.listdir(order_path):
                    doc.save(merged_doc)
                    os.chmod(merged_doc, S_IWRITE)
                else:
                    with fitz.open(merged_doc) as doc_merged:
                        doc_merged.insert_file(doc)
                        doc_merged.save(save_doc)
                        print(merged_doc, 'save mergind.pdf ')
                        os.chmod(save_doc, S_IWRITE)
                    os.remove(merged_doc)
                    os.rename(save_doc, merged_doc)


def main():
    a = get_orders_to_merge()
    for x in a:
        b = get_drawings_to_merge(x)
        for x in b:
            print(x)


if __name__ == '__main__':
    main()


