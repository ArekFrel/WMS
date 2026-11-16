import os
import pandas as pd
import numpy as np
from wms_main.const import Paths, db_get_with_query, db_commit, db_quick_commit, CURSOR


def update_obiekt(
        _regular = True,
        _do_update=False,
        _change_in_sap=False
):
    # Get data from sap_3 File
    df = pd.read_excel(
        os.path.join(Paths.RAPORT_CATALOG, 'sap3.xlsx'),
        usecols=['SO#', 'Final Customer name']
    )
    df['SO#'] = df['SO#'].astype(int)
    df.rename(columns={'SO#': 'SO', 'Final Customer name': 'Obiekt'}, inplace=True)
    df = df.drop_duplicates()

    # Get current SOs number from DataBase
    df_sql = db_get_with_query(
        query='SELECT DISTINCT [S.O.] FROM sap;',
        func_name='data_merger',
        type_get='int'
    )
    df_sql = pd.DataFrame(df_sql, columns=['S.O.'])
    df_sql.rename(columns={'S.O.': 'SO'}, inplace=True)
    df_sql['SO'] = df_sql['SO'].astype(int)

    # Get table SO_Obiekt saved ind DataBase
    df_saved = db_get_with_query(
        query='SELECT * FROM SO_OBIEKT;',
        func_name='data_merger',
        type_get='list'
    )
    if len(df_saved) > 0:
        df_saved = pd.DataFrame(np.array(df_saved), columns=['SO', 'Obiekt'])
        df_saved['SO'] = df_saved['SO'].astype(int)

    # Setting Target dataFrame - what data should be in SO_Obiekt table
    df_target = df_sql.merge(df, on='SO', how='left')

    #Joining data to get rows to remove from SO_Obiekt table.
    if len(df_saved) > 0:
        df_delete = df_saved.merge(df_target, on='SO', how='left', indicator=True)
        df_delete = df_delete.query('_merge == "left_only"')
        df_delete = df_delete.drop(columns=['Obiekt_x', 'Obiekt_y', '_merge'])
        df_update = df_target.merge(df_saved, on='SO', how='left', indicator=True)
        df_update = df_update.query('_merge == "left_only"')
        df_update = df_update.drop(columns=['Obiekt_y', '_merge'])
        df_update.rename(columns={'Obiekt_x': 'Obiekt'}, inplace=True)
    else:
        df_delete = []
        df_update = df_target

    if _do_update:
        query = 'DELETE FROM so_obiekt'
        db_commit(query, '_do_update')
        for index, row in df_target.iterrows():
            so, obiekt = row['SO'], row['Obiekt']
            if so == 0:
                continue
            query = f"INSERT INTO SO_OBIEKT (SO, OBIEKT) VALUES({so}, '{obiekt}'); "
            db_commit(query, 'obiekt_updater, inserting')
            print(query)
        return

    if _regular:
        for so in df_delete['SO']:
            query = f'DELETE FROM SO_OBIEKT WHERE SO = {so}; '
            db_commit(query, 'ubiekt_updater, deleter')
            print(f'SO: {so} has been deleted.')

        for index, row in df_update.iterrows():
            so, obiekt = row['SO'], row['Obiekt']
            if so == 0:
                continue
            query = f"MERGE INTO so_obiekt AS target " \
                    f"USING (VALUES ('{so}', '{obiekt}')) " \
                    f"AS SOURCE (SO, OBIEKT) " \
                    f"ON target.SO = source.SO " \
                    f"WHEN MARCHED THEN " \
                    f"UPDATE SET " \
                    f"target.SO = source.SO," \
                    f"target.Obiekt = source.Obiekt" \
                    f"WHEN NOT MATCHED BY TARGET THEN " \
                    f"INSERT (SO, OBIEKT)" \
                    f"VALUES (source.SO, source.OBIEKT);"
            db_commit(query, 'ubiekt_updater, updater')

    if _change_in_sap:
        # for index, row in df_target.iterrows():
        #     so, obiekt = row['SO'], row['Obiekt']
        #     if so == 0:
        #         continue
        #     query = f"UPDATE sap set Obiekt = '{obiekt}' WHERE [S.O.] = {so}; "
        #     db_commit(query, 'obiekt_updater, updater')
        #     print(query)

        with CURSOR:
            for index, row in df_target.iterrows():
                so, obiekt = row['SO'], row['Obiekt']
                if so == 0 :
                    continue
                query = f"UPDATE sap set Obiekt = '{obiekt}' WHERE [S.O.] = {so}; "
                print(query)
                db_quick_commit(
                    cursor=CURSOR,
                    query=query,
                    func_name='change_in_sap'
                )


def main():
    pass
    # update_obiekt(
    #     _regular=False,
    #     _do_update=False,
    #     _change_in_sap=False
    # )

if __name__ == '__main__':
    main()