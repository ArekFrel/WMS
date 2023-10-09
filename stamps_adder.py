import os
import fitz
from stat import S_IWRITE


class File:

    def __init__(self, path):
        self.path = path
        self.catalog = self.path[:self.path.rfind('/')]
        self.full_name = self.path[self.path.rfind('/') + 1:]
        self.name = self.full_name.split('.')[0]
        self.bought = 'buy' in self.name.lower()
        self.extension = path.split('.')[-1].lower()
        if self.bought:
            self.name = ''.join(self.full_name.lower().split('buy'))


def stamper(file):
    stamp = 'C:/Dokumenty/Python_Project/stamp_adder/watermark.png'
    with fitz.open(file.path) as pdf_document:
        stamp_doc = open(stamp, "rb").read()
        pdf_document[0].insert_image(pdf_document[0].bound(), filename=stamp, overlay=False)
        pdf_document.save(os.path.join(file.catalog, file.name))
    os.chmod(file.path, S_IWRITE)
    os.rename(file.path, file.path)
    os.remove(file.path)


def main():

    file = File('C:/Dokumenty/Python_Project/stamp_adder/BUY1614342 1740018-7826.pdf')
    stamper(file=file)


if __name__ == '__main__':
    main()
