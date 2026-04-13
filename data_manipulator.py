import wms_main.const
import csv

def main():
    with open('ppp.csv') as ppp:
        recs = csv.reader(ppp)
        query = ""
        for rec in recs:
            order, planner, when, who = rec
            query += f"INSERT INTO dbo.[prod_order_planist] ([SO_or_PO], [Planista], [Data_Dodania], [U_name]) "  \
                    f"VALUES ('{order}', '{planner}', '{when}', '{who}') ;\n"
    print(query)


if __name__ == '__main__':
    main()

