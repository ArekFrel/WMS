from const import *


def main():
    query = "Select Confirmation, [System Status] From SAP Where [System Status] Like '% %';"
    result = CURSOR.execute(query)
    table = []

    for rec in result:
        table.append(rec)

    for rec in table:
        new_query = f"Update SAP Set [System Status] = '{rec[1].split(' ')[-1]}' Where Confirmation = {rec[0]};"
        with CURSOR:
            CURSOR.execute(new_query)
            CURSOR.commit()
        print(new_query)


if __name__ == '__main__':
    main()
