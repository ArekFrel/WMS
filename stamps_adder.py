import os
import fitz
from const import Paths


def stamper(file):
    with fitz.open(file.start_path) as pdf_document:
        if file.sub_bought:
            watermark = Paths.WATERMARK_SUB_BOUGHT
        if (file.bought_name | file.bought_cat) and ~file.sub_bought:
            watermark = Paths.WATERMARK_BOUGHT
        pdf_document[0].insert_image(
            pdf_document[0].bound(),
            filename=watermark,
            overlay=False,
            keep_proportion=True)
        pdf_document.save(file.dest_path)
        file.set_file_modifable()
    os.rename(file.start_path, file.start_path)
    os.remove(file.start_path)


def main():
    pass


if __name__ == '__main__':
    main()
