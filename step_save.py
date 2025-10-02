import win32com.client
import os
from pathlib import Path


def step_saver(file):
    inventor = win32com.client.Dispatch("Inventor.Application")
    inventor.Visible = True
    doc = inventor.Documents.Open(file)
    location = Path(file).parent
    new_file = file[len(str(location)) + 1:].split('.')[0] + '.x_t'
    new_file = os.path.join(location, new_file)
    doc.SaveAs(new_file, True)
    doc.Close()
    return None
    # inventor.Visible = True  # Opcjonalnie pokaż okno aplikacji


def main():
    path = input('podaj ścieżkę: ')
    for model in [x for x in os.listdir(path) if x.endswith('.ipt') or x.endswith('.stp')]:
        step_saver(os.path.join(path, model))


if __name__ == '__main__':
    main()
