import os
import pandas as pd
from wms_main.const import CONN, Paths

def main():
    ii_path = os.path.join(Paths.RAPORT_CATALOG, 'ITEM_INSERT.csv')
    id_path = os.path.join(Paths.RAPORT_CATALOG, 'ITEM_DELETE.csv')
    srd = pd.read_excel(Paths.IR_FILE, usecols=['Order', 'Sales order item'])
    srd = srd[srd['Sales order item'] != 0]
    dbd = pd.read_sql("SELECT Item as 'Sales order item', Prod_Order as 'Order' FROM Items", CONN)
    dmall = srd.merge(dbd.dropna().drop_duplicates(),  how='left', indicator=True)
    item_insert = dmall[dmall['_merge'] == 'left_only']
    item_insert = item_insert.drop('_merge', axis=1)
    item_delete = dmall[dmall['_merge'] == 'right_only']
    item_delete = item_delete.drop('_merge', axis=1)
    try:
        item_insert.to_csv(ii_path, index=False, encoding='UTF-8', header=False)
        item_delete.to_csv(id_path, index=False, encoding='UTF-8', header=False)
        return True
    except PermissionError:
        return False


if '__main__' == __name__:
    main()