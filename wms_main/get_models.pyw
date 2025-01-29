import os
import shutil
import sys
import tkinter as tk
import pathlib
from tkinter import filedialog

FONT_SIZE = 10


def main_name_getter(text: str):

    if '.' not in text:
        return text

    if text.count('.') == 1:
        main_name, extension = text.split('.')
        return main_name

    for i in range(-1, -(len(text) + 1), -1):
        if text[i] == '.':
            return text[0: i]


if getattr(sys, 'frozen', False):
    application_path = str(pathlib.Path(os.path.abspath(sys.executable)).parent)
else:
    application_path = str(pathlib.Path(os.path.abspath(__file__)).parent)


class Application(tk.Frame):

    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.button_1 = None
        self.label_1 = None
        self.button_2 = None
        self.label_2 = None
        self.button_3 = None
        self.model_path = None
        self.drawings_path = application_path
        self.create_widgets()

    def create_widgets(self):

        self.button_1 = tk.Button(text='Wybierz ścieżkę modeli', command=self.choose_directory_models, width=22)
        self.button_1.grid(row=0, column=0, pady=10, padx=10,  sticky=tk.W)

        self.label_1 = tk.Label(text=self.model_path, font=('Arial', FONT_SIZE), height=2)
        self.label_1.grid(row=1, column=0, padx=20, sticky=tk.W)

        self.button_2 = tk.Button(text='Wybierz ścieżkę docelową', command=self.choose_directory_drawings, width=22)
        self.button_2.grid(row=2, column=0, pady=10, padx=10, sticky=tk.W)

        self.label_2 = tk.Label(text=application_path, font=('Arial', FONT_SIZE), height=2)
        self.label_2.grid(row=3, column=0, padx=20, sticky=tk.W)
        self.button_3 = tk.Button(
            text='URUCHOM',
            command=self.launch,
            width=22,
        )
        self.button_3.config(state=tk.DISABLED)
        self.button_3.grid(row=4, column=0, pady=10, padx=10, sticky=tk.W)

    def choose_directory_models(self):
        folder_path = filedialog.askdirectory(initialdir="C:/VaultWork/Designs")
        if folder_path:
            self.model_path = folder_path
            self.enable_button()
            self.label_1.configure(text=folder_path)

    def choose_directory_drawings(self):
        folder_path = filedialog.askdirectory(initialdir=application_path)
        if folder_path:
            self.drawings_path = folder_path
            self.enable_button()
            self.label_2.configure(text=folder_path)

    def enable_button(self):
        if self.drawings_path and self.model_path:
            self.button_3.config(state=tk.NORMAL)
        else:
            self.button_3.config(state=tk.DISABLED)

    def launch(self):
        model_path = self.model_path
        drawing_path = self.drawings_path

        drawings = [_[8:-4] for _ in os.listdir(drawing_path)]
        model_files = [file for file in os.listdir(model_path) if file.endswith('.ipt')]
        for model_file in model_files:
            model_name = main_name_getter(model_file)
            if model_name in drawings:
                try:
                    shutil.copy(os.path.join(model_path, model_file), os.path.join(drawing_path, model_file))
                    print(model_file)
                except FileNotFoundError:
                    print(f'nie skopiowano pliku: {model_file}')


def resource_path(relative_path):
    """ Funkcja do uzyskania ścieżki do plików w spakowanej aplikacji """
    try:
        # Ścieżka do katalogu tymczasowego (dla spakowanego pliku)
        base_path = sys._MEIPASS
    except AttributeError:
        # Ścieżka dla uruchamiania w trybie developerskim (nie spakowanym)
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():

    root = tk.Tk()
    root.title("Przerzucanie modeli")
    root.geometry("380x335")
    root.iconbitmap(resource_path("utils/icon.ico"))
    Application(root)
    root.mainloop()


if __name__ == '__main__':

    main()

