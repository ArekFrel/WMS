import time
import os
import pathlib
import pyodbc
import sys
import shutil
from stat import S_IWRITE


def countdown(t=3):
    while t >= 0:
        secs = t
        timer = f'The window closes in {secs:02d}s'
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

def resource_path():
    """ Funkcja do uzyskania ścieżki do plików w spakowanej aplikacji """
    if getattr(sys, 'frozen', False):
        application_path = str(pathlib.Path(os.path.abspath(sys.executable)).parent)
    else:
        application_path = str(pathlib.Path(os.path.abspath(__file__)).parent)

    return application_path


def main():
    # query = input('Opisz materiał "LIKE SQL": ')
    # QUERY = f"SELECT * FROM TECHNOLOGIA WHERE materiał LIKE '{query}';"
    QUERY = f"SELECT * FROM TECHNOLOGIA WHERE rysunek LIKE '175410%' and (OP_1 Like 'F%' OR OP_2 Like 'F%' OR OP_3 Like 'F%') AND Materiał not like '#%' and materiał not like 'fi%';"
    app_path = resource_path()
    source_cat = 'W:/!!__PRODUKCJA__!!/1__Rysunki/'
    destination = os.path.join(app_path, 'get_drawings')
    if not os.path.exists(destination):
        os.mkdir(destination)
    else:
        do_clear_catalog = 'y' == input("Czy usunąć poprzednie rysunki? (y/n)    ").lower()
        if do_clear_catalog:
            for file in os.listdir(destination):
                path_file = os.path.join(destination, file)
                try:
                    os.chmod(path_file, S_IWRITE)
                    os.remove(path_file)
                except PermissionError:
                    print(f'Permission Error {file}')


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
        dest_plik = destination + '\\' +plik
        space_index = plik.find(' ')
        plik = source_cat + plik.strip()[0:space_index] + '/' + plik.strip()
        try:
            shutil.copy(plik, dest_plik)  # kopiowanie pliku
            number += 1
            reset += 1
            # time.sleep(0.15)
        except FileNotFoundError:
            print(f'nie skopiowano pliku: {plik}')
            continue


if __name__ == '__main__':
    close_app = "Y"
    while close_app == "Y":
        main()
        close_app = input("Keep working? If yes type 'Y'       ")
    # countdown()
