import os
import pandas as pd
import warnings
from wms_main.const import CONN, Paths

def main():
    with warnings.catch_warnings():
        ii_path = os.path.join(Paths.RAPORT_CATALOG, 'ITEM_INSERT.csv')
        id_path = os.path.join(Paths.RAPORT_CATALOG, 'ITEM_DELETE.csv')
        srd = pd.read_excel(Paths.IR_FILE, usecols=['Order', 'Sales order item'])
        srd = srd[srd['Sales order item'] != 0]
        warnings.simplefilter(
            "ignore",
            category=UserWarning
        )
        dbd = pd.read_sql("SELECT Item as 'Sales order item', Prod_Order as 'Order' FROM Items", CONN)
        dmall = srd.merge(dbd.dropna().drop_duplicates(),  how='left', indicator=True)
        item_insert = dmall[dmall['_merge'] == 'left_only']
        item_insert = item_insert.drop('_merge', axis=1)
        item_insert = item_insert.reindex(columns=['Order', 'Sales order item'])
        item_delete = dmall[dmall['_merge'] == 'right_only']
        item_delete = item_delete.drop('_merge', axis=1)
        item_delete = item_delete.reindex(columns=['Order', 'Sales order item'])
        try:
            item_insert.to_csv(ii_path, index=False, encoding='UTF-8', header=False)
            item_delete.to_csv(id_path, index=False, encoding='UTF-8', header=False)
            return True
        except PermissionError:
            return False


if __name__ == '__main__':
    main()
