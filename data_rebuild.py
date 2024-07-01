import pandas as pd

td = pd.read_csv('sheet_data.csv', usecols=['Order', 'Work center description'], encoding="utf-8")
td.rename({'Work center description': 'Work_center_description'}, axis=1, inplace=True)
td_1 = td.query('Work_center_description.str.contains("GRABKOWSKI")')
td_1.drop_duplicates(inplace=True)
td_1.to_csv('output.csv', index=False)