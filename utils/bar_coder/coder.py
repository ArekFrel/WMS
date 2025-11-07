import os
import fitz
import barcode

def coder(file):
    if file.replace:
        try:
            os.remove(file.dest_path)
        except PermissionError:
            print(f'Cannot replace "{file.name}" and add barcode.')
            return
    # create bar code graphics and save as temporary file
    writer_options = {
        'module_width': 0.1,  # szerokość kreski
        'module_height': 5.25,  # wysokość kreski
        'font_size': 3.0,
        'text_distance': 1.0,  # odległość tekstu od kodu
        'quiet_zone': 1.0,  # margines zewnętrzny
        'write_text': True  # wyłącz tekst pod kodem
    }
    code_path = os.path.join(file.dest_catalog, f'{file.po}_barcode')
    code = barcode.get_barcode_class('code128')(file.po)
    # temporary file of bar code
    code.save(code_path, options=writer_options)
    code_path = f'{code_path}.svg'
    # adding code to sap card
    with fitz.open(file.start_path) as pdf_doc:
        with fitz.open(code_path) as svg_doc:
            pdf_bytes = svg_doc.convert_to_pdf()
        image_pdf = fitz.open("pdf", pdf_bytes)
        page = pdf_doc[0]
        page_width, page_height = page.rect.width, page.rect.height
        img_width, img_height = 180, 42
        offset_x, offset_y = 397.0, 65 #wsztrzelenie się w tabelkę
        rect = fitz.Rect(
            page_width - img_width - offset_x,
            offset_y,
            page_width - offset_x,
            offset_y + img_height
        )
        page.show_pdf_page(rect, image_pdf, 0)

        pdf_doc.save(file.dest_path)
    os.remove(f'{code_path}')
    # os.remove(file.start_path)

def main():
    pass



if __name__ == '__main__':
    main()