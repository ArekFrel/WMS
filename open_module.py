import time
import os
import pyodbc


def countdown(t=1):
    while t >= 0:
        secs = t
        timer = f'The window closes in {secs:02d}s'
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def main():
    po = input('Podaj numer zlecenia: ')
    source_cat = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'
    server = 'SELUSQL16'
    database = 'PRODUKCJAWORKFLOW'
    conn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                          "Server=" + server + ";"
                          "Database=" + database + ";"
                          "Trusted_Connection=yes;")
    QUERY = f"Select Plik From Technologia Where [PO] = {str(po)} AND Status_Op = 6 Order by Rysunek DESC;"
    cursor = conn.cursor()
    result = cursor.execute(QUERY)

    number = 0
    reset = 0
    for row in result:
        plik = row.Plik
        if not plik.endswith('.pdf'):
            plik = plik + '.pdf'
        space_index = plik.find(' ')
        plik = source_cat + plik.strip()[0:space_index] + '/' + plik.strip()
        if reset == 10:
            go_on = input('Continue? If no type "N"')
            if go_on == "N":
                break
            reset = 0
        try:
            print(plik)
            os.startfile(plik, 'open')
            # shutil.copy(plik.strip(), destination) ' przenoszenie pliku
            number += 1
            reset += 1
            time.sleep(0.15)
        except FileNotFoundError:
            print(f'nie otwarto pliku: {plik}')
            continue


if __name__ == '__main__':
    close_app = "Y"
    while close_app == "Y":
        main()
        # close_app = input("Keep working? If yes type 'Y'       ")
    countdown()
