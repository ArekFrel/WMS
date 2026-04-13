from wms_main.const import *


def main():
    query = f"Select id, PO, Plik, Rysunek From Technologia WHERE id = 87924"
    CURSOR.execute(query)
    result = CURSOR.fetchall()
    # my_data = [val for val in result]

    for record in result:
        idx, po, plik, rysunek = record
        new_plik = plik[0:-3] + str(int(plik[-3:]) + 5)
        new_rysunek = rysunek[0:-3] + str(int(plik[-3:]) + 5)
        chnging_query = f"Update Technologia Set Plik = '{new_plik}', Rysunek = '{new_rysunek}' WHERE id = {idx}; "
        old_file = os.path.join(Paths.PRODUCTION, str(po), plik + '.pdf')
        new_file = os.path.join(Paths.PRODUCTION, str(po), new_plik + '.pdf')
        try:
            # print(f'{old_file=}')
            # print(f'{new_file=}')
            os.rename(old_file, new_file)
        except PermissionError:
            print(f'no go on {rysunek}')
            return
        except FileNotFoundError:
            pass
        # print(f'{chnging_query=}')
        db_commit(chnging_query, func_name='youknowwhat')


def pomonice():
    query = f"Select DISTINCT Plik From Technologia WHERE po in (1676079, 1676058) and Plik not like '%SAP%';"
    CURSOR.execute(query)
    result = [x[0] for x in CURSOR.fetchall()]
    ids_to_delete = []

    for record in result:
        CURSOR.execute(f"Select COUNT(Plik) From Technologia WHERE PLIK = '{record}'")
        count = CURSOR.fetchval()
        if count < 2:
            continue
        CURSOR.execute(f"Select id From Technologia WHERE PLIK = '{record}' order by Kiedy DESC")
        ids = [int(x[0]) for x in CURSOR.fetchall()]
        # ids = list(ids)

        for i in range(count - 1):
            query_2 = f'DELETE FROM Technologia WHERE id = {ids.pop()}'
            print(query_2)
            # ids_to_delete.append(ids.pop())

    a = 0

if __name__ == '__main__':
    pomonice()
    # main()

