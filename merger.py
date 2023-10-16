import os
import fitz
from stat import S_IWRITE
catalog = 'C:/Dokumenty/sat/1__Rysunki/'


def get_orders_to_merge():
    return ['1586080']


def get_drawings_to_merge(cat):
    return os.listdir(cat)


def merged_name_available(path):
    num = len([_ for _ in os.listdir(path) if "merged" in _])
    print(f'{num} --  merged name available')
    return f'merged.pdf' if num == 0 else f'merged_{num}.pdf'


def merging():

    orders = get_orders_to_merge()
    for order in orders:
        drawings = get_drawings_to_merge(os.path.join(catalog, order))
        order_path = os.path.join(catalog, order)
        merge_name = merged_name_available(order_path)
        print(merge_name, '----merge-name')

        for drawing in drawings:
            drawing_path = os.path.join(order_path, drawing)
            # print(drawing_path, 'drawing path')
            merged_doc = os.path.join(order_path, f'{order} {merge_name}')
            save_doc = os.path.join(order_path, 'merged_temp.pdf')
            with fitz.open(drawing_path) as doc:
                if f'{order} {merge_name}' not in os.listdir(order_path):
                    doc.save(merged_doc)
                    print('saving   ', merged_doc )
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
    merging()
    # print(merged_name_available('C:/Dokumenty/sat/1__Rysunki/1586080'))


if __name__ == '__main__':
    main()


