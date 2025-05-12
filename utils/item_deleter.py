import os
import os.path
from wms_main.const import CURSOR, Paths,db_commit


def delete_item():
    print('Item Delete started.')
    item_delete_file = os.path.join(Paths.RAPORT_CATALOG, "aaITEM_DELETE.csv")
    if not os.path.exists(item_delete_file):
        return True
    with open(item_delete_file, encoding='utf-8-sig') as file:
        i = 0
        prod_order_list = []
        for record in file:
            if len(record.strip()) == 0:
                continue
            prod_ord_no = record.strip().split(',')[0]
            prod_order_list.append(prod_ord_no)
    if prod_order_list:
        orders_text ='('
        for order in prod_order_list:
            orders_text += order + ', '
            i += 1
        orders_text = orders_text[:-2] + ')'
        query = f'DELETE FROM Items WHERE Prod_Order IN {orders_text};'
        if not db_commit(query=query, func_name='delete_item'):
            return False
    print(f'{i} Item Deleted')
    return True


def main():
    return delete_item()


if __name__ == '__main__':
    main()
