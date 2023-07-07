import os
from const import *


def files_in_db():
    order_number = input('Podaj PO: ')
    print('')
    source_cat = PRODUCTION
    query = f'SELECT id, Plik FROM TECHNOLOGIA WHERE PO = {order_number};'
    result = CURSOR.execute(query)
    table_files = [(t[0], t[1]) for t in result]
    po_cat = os.path.join(source_cat, order_number)
    try:
        cat_content = [file[0:-4] for file in os.listdir(po_cat) if file.lower().endswith('.pdf')]
    except FileNotFoundError:
        print('Nie ma takiego folderu')
        cat_content = []

    deleting_query = ''
    while table_files:
        db_id, drawing = table_files.pop()
        if drawing not in cat_content:
            query = f'DELETE FROM TECHNOLOGIA WHERE id = {db_id}; \n'
            deleting_query += query
    with open('result.txt', 'w', encoding='UTF-8') as rf:
        rf.write(f'{deleting_query}')
    if len(deleting_query) > 1:
        CURSOR.execute(deleting_query)
        CURSOR.commit()
    print(deleting_query)


def rem(order):
    source_cat = PRODUCTION
    order = str(order)
    query = f'SELECT id, Plik FROM TECHNOLOGIA WHERE PO = {order};'
    result = CURSOR.execute(query)
    table_files = [(t[0], t[1]) for t in result]
    po_cat = os.path.join(source_cat, order)
    try:
        cat_content = [file[0:-4] for file in os.listdir(po_cat) if file.lower().endswith('.pdf')]
    except FileNotFoundError:
        print('Nie ma takiego folderu')
        cat_content = []

    deleting_query = ''
    while table_files:
        db_id, drawing = table_files.pop()
        if drawing not in cat_content:
            query = f'DELETE FROM TECHNOLOGIA WHERE id = {db_id}; \n'
            deleting_query += query
    with open('result.txt', 'a', encoding='UTF-8') as rf:
        rf.write(f'{deleting_query}')
    # CURSOR.execute(deleting_query)
    # CURSOR.commit()
    print(deleting_query)


def cleaning():
    query = f'SELECT DISTINCT [PO] FROM TECHNOLOGIA;'
    result = CURSOR.execute(query)
    order_list = [t[0] for t in result]
    for order in order_list:
        rem(order)


def main():
    # cleaning()
    files_in_db()


if __name__ == '__main__':
    main()

