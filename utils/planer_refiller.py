from wms_main.const import *
from pyodbc import Error, DataError, OperationalError
import inspect

def main():
    t=0

    query = f"SELECT DISTINCT CONCAT(S.[s.o.], '_', I.Item) as SO_Item " \
            f",[S.O.]" \
            f",pop.Planista " \
            f"FROM sap S " \
            f"RIGHT JOIN Items I on I.Prod_Order = S.[P.O.] " \
            f"RIGHT join prod_order_planist  pop on CONCAT(S.[s.o.], '_', I.Item) = pop.SO_or_PO " \
            f"WHERE S.[Planista 0] != '' and [S.O.] != 0 " \
            f"GROUP BY " \
            f"S.[s.o.] " \
            f",I.Item " \
            f",pop.Planista;"


    try:
        CURSOR.execute(query)
        records = CURSOR.fetchall()
        if not records:
            return

    except Error:
        print('Connection to database failed.')
        return []
    except OperationalError:
        print('Operatinal Error.')
        return []
    except DataError:
        print('Data Error.')
        return []

    for rec in records:
        so_item, planista = rec
        so, item = so_item.split('_')
        new_query = f"UPDATE SAP SET [Planista 0] = '{planista}' WHERE [P.O.] in (" \
                    f"Select distinct [P.O.] from SAP LEFT jOIN Items ON SAP.[P.O.] = Items.Prod_Order " \
                    f"Where Sap.[S.O.] = {so} AND Items.Item = {item}) AND [Planista 0] = ''"
        db_commit(new_query, inspect.currentframe())


if __name__ == '__main__':
    main()

