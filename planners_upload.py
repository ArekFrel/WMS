import os
import pathlib
import shutil
import datetime
from pathlib import Path

HERE = pathlib.Path(__file__).parent
# PRODUCTION = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'
PRODUCTION = 'C:/Dokumenty/planners_drawings_upload/test_area'


def archive(file_name):
    with open('transfer_history.txt', 'a', encoding='utf-8') as history_file:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_file.write(f'{now}____{file_name} \n')


def file_name_validator(name: str):
    if name[:-4].endswith('_99'):
        return False
    if name[7] == ' ' and name[:6].isnumeric():
        return True
    else:
        return False


def name_if_exist(file: str, number: int):
    name, extension = file.rsplit('.', 1)
    if '_' in name[-3:-1]:
        base_name, ord_num = name.split(sep='_')
        new_name = f'{base_name}_{int(ord_num) + 1}.{extension}'
    else:
        new_name = f'{name}_{number}.{extension}'
    return new_name


def upload_drawings():
    here_list = os.listdir(HERE)
    for drawing in here_list:
        if str(drawing).endswith('.pdf'):
            if not file_name_validator(str(drawing)):
                continue
            prod_order = str(drawing)[:drawing.index(' ')]
            dest_cat = os.path.join(PRODUCTION, prod_order)
            dest_drawing = drawing
            dest_file = os.path.join(PRODUCTION, prod_order, dest_drawing)
            a = 1
            while os.path.exists(dest_file):
                dest_drawing = name_if_exist(dest_drawing, a)
                dest_file = os.path.join(PRODUCTION, prod_order, dest_drawing)
                a += 1

            if not os.path.exists(dest_cat):
                os.mkdir(dest_cat)

            file = os.path.join(HERE, drawing)
            try:
                shutil.move(file, dest_file)
                archive(file_name=f'{drawing}')

            except FileNotFoundError:
                archive(file_name=f'{drawing}__saving_error')


if __name__ == '__main__':
    upload_drawings()
