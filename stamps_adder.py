import os
import fitz
from stat import S_IWRITE
from const import WATERMARK_BOUGHT


def stamper(file):
    with fitz.open(file.start_path) as pdf_document:
        pdf_document[0].insert_image(
            pdf_document[0].bound(),
            filename=WATERMARK_BOUGHT,
            overlay=False,
            keep_proportion=True)
        pdf_document.save(file.start_path_new_name)
        os.chmod(file.start_path, S_IWRITE)
    os.rename(file.start_path, file.start_path)
    os.remove(file.start_path)


def main():
    pass


if __name__ == '__main__':
    main()
