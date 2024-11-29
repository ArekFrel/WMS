import fitz  # PyMuPDF
import os
from wms_main.const import Paths
from stat import S_IWRITE


def remove_watermark(drawing):

    order, draw_num = drawing.split(' ')
    pdf_document = os.path.join(Paths.PRODUCTION, order, order + ' ' + draw_num + '.pdf')
    if os.path.exists(pdf_document):
        os.chmod(pdf_document, S_IWRITE)
    doc = fitz.open(pdf_document)

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        image_list = page.get_images(full=True)
        for img in image_list:
            xref = img[0]
            page.delete_image(xref)

    try:
        doc.saveIncr()
    except PermissionError:
        print(f'Zamknij rysunek {drawing}')
        return
    except FileNotFoundError:
        print(f'Nie odnaleziono {drawing}')
        return
    except RuntimeError:
        print(f'Przekroczono czas otwarcia {drawing}')
        return

    doc.close()
    print(f"Znak wodny usunięty, nowy plik zapisany jako {pdf_document}")


def loop():
    arg = input('Wpisz nazwę pliku do usunięcia znaku wodnego: ')
    if arg == 'quit':
        return False
    if arg == 'file':
        file = os.path.join(os.path.dirname(__file__), 'watermark_remover_list.txtpy')
        with open(file, 'r', encoding='utf-8') as lodtd:
            for line in lodtd:
                remove_watermark(line.strip().rstrip())
        return False
    remove_watermark(arg)
    return True


def main():

    while loop():
        pass


if __name__ == '__main__':
    main()


