from wms_main.const import *
from pyodbc import Error, DataError, OperationalError
import inspect

def main():
    query =     f"SELECT DISTINCT [P.O.], " \
                f"case when pom.Planista is not null then pom.Planista " \
                f"else pot.Planista " \
                f"end as new_Planista " \
                f"FROM sap S " \
                f"LEFT JOIN Items I ON I.Prod_Order = S.[P.O.] " \
                f"LEFT JOIN prod_order_planist  pop ON pop.SO_or_PO = concat(s.[s.o.], '_', i.item) " \
                f"LEFT join prod_order_planist  pot ON CAST(pot.SO_or_PO AS VARCHAR) = CAST(s.[s.o.] AS VARCHAR) " \
                f"LEFT JOIN prod_order_planist pom on CAST(pom.SO_or_PO as Varchar) = cast(s.[P.O.] AS Varchar) " \
                f"WHERE [Planista 0] = '' ;"
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

    new_query = ''
    cntr = 0
    records = [[po, new_planner] for po, new_planner in records if new_planner is not None]
    for rec in records:
        po, new_planner = rec
        new_query = new_query + f"UPDATE SAP SET [Planista 0] = '{new_planner}' WHERE [P.O.] = '{po}'; "
        cntr += 1
        if cntr == 10:
            db_commit(new_query, inspect.currentframe())
            cntr = 0
            new_query = ''
    if new_query:
        db_commit(new_query, inspect.currentframe())


if __name__ == '__main__':
    main()

