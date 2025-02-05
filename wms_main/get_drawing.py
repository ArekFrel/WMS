import time
import os
import shutil
import pyodbc


def countdown(t=3):
    while t >= 0:
        secs = t
        timer = f'The window closes in {secs:02d}s'
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def main():
    query = input('Podaj kwerendę: ')
    QUERY = f"{query}"

    source_cat = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'
    destination = 'C:/__main__/gen_cat/get_drawings/'
    server = 'SELUSQL16'
    database = 'PRODUKCJAWORKFLOW'
    conn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                          "Server=" + server + ";"
                          "Database=" + database + ";"
                          "Trusted_Connection=yes;")
    cursor = conn.cursor()
    result = cursor.execute(QUERY)
    table = list(result)
    number = 0
    reset = 0
    print(f'Records found : {len(table)}')
    c = input('Continue? Press any key.')
    for row in table:
        plik = row[1]
        if not plik.endswith('.pdf'):
            plik = plik + '.pdf'
        dest_plik = destination + plik
        space_index = plik.find(' ')
        plik = source_cat + plik.strip()[0:space_index] + '/' + plik.strip()
        try:

            shutil.copy(plik, dest_plik)  # kopiowanie pliku
            number += 1
            reset += 1
            time.sleep(0.15)
        except FileNotFoundError:
            print(f'nie skopiowano pliku: {plik}')
            continue


if __name__ == '__main__':
    close_app = "Y"
    while close_app == "Y":
        main()
        close_app = input("Keep working? If yes type 'Y'       ")
    countdown()
