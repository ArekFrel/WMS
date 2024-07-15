import fitz  # PyMuPDF
import os
from const import Paths


def remove_watermark(drawing):

    order, draw_num = drawing.split(' ')
    pdf_document = os.path.join(Paths.PRODUCTION, order, order + ' ' + draw_num + '.pdf')
    doc = fitz.open(pdf_document)

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        image_list = page.get_images(full=True)
        for img in image_list:
            xref = img[0]
            page.delete_image(xref)

    try:
        doc.saveIncr()
    except RuntimeError:
        print(f'Zamknij rysunek {drawing}')
        return

    doc.close()
    print(f"Znak wodny usunięty, nowy plik zapisany jako {pdf_document}")


if __name__ == '__main__':
    arg = input('Wpisz nazwę pliku do usunięcia znaku wodnego ')
    remove_watermark(arg)


