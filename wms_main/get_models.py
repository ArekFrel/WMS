import time
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

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
        self.drawings_path = None
        self.create_widgets()

    def create_widgets(self):

        self.button_1 = tk.Button(text='Wybierz ścieżkę modeli', command=self.choose_directory_models, width=22)
        self.button_1.grid(row=0, column=0, pady=10, sticky=tk.W)

        self.label_1 = tk.Label(text=self.model_path, font=('Arial', FONT_SIZE), height=2)
        self.label_1.grid(row=1, column=0, sticky=tk.W)

        self.button_2 = tk.Button(text='Wybierz ścieżkę docelową', command=self.choose_directory_drawings, width=22)
        self.button_2.grid(row=2, column=0, pady=10, sticky=tk.W)

        self.label_2 = tk.Label(text=self.drawings_path, font=('Arial', FONT_SIZE), height=2)
        self.label_2.grid(row=3, column=0, sticky=tk.W)
        self.create_button_3()

    def create_button_3(self, state=tk.DISABLED):
        self.button_3 = tk.Button(
            text='URUCHOM',
            command=self.launch,
            width=22,
            )
        self.button_3.config(state=state)
        self.button_3.grid(row=4, column=0, pady=10, sticky=tk.W)

    def choose_directory_models(self):
        folder_path = filedialog.askdirectory(initialdir="C:/VaultWork/Designs")
        if folder_path:
            self.model_path = folder_path
            self.enable_button()
            self.label_1.configure(text=folder_path)

    def choose_directory_drawings(self):
        folder_path = filedialog.askdirectory(initialdir="C:/__main__/gen_cat/get_drawings")
        if folder_path:
            self.drawings_path = folder_path
            self.enable_button()
            self.label_2.configure(text=folder_path)

    def enable_button(self):
        if self.drawings_path and self.model_path:
            self.create_button_3(state=tk.NORMAL)
        else:
            self.create_button_3()

    def launch(self):
        # model_path = input('Wprowadź ściżkę modeli: ')
        model_path = self.model_path
        # drawing_path = input('Wprowadź sciężkę rysunków: ')
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

def main():
    pass
    # # model_path = input('Wprowadź ściżkę modeli: ')
    # model_path = "C:\VaultWork\Designs\Products\\30 Chain Conveyors\\103 - Valio (WTS Module)"
    # # drawing_path = input('Wprowadź sciężkę rysunków: ')
    # drawing_path = "C:\__main__\gen_cat\get_drawings"
    #
    # drawings = [_[8:-4] for _ in os.listdir(drawing_path)]
    # model_files = [file for file in os.listdir(model_path) if file.endswith('.ipt')]
    # for model_file in model_files:
    #     model_name = main_name_getter(model_file)
    #     if model_name in drawings:
    #         try:
    #             shutil.copy(os.path.join(model_path, model_file), os.path.join(drawing_path, model_file))
    #             print(model_file)
    #         except FileNotFoundError:
    #             print(f'nie skopiowano pliku: {model_file}')



if __name__ == '__main__':

    root = tk.Tk()
    root.title("Przerzucanie modeli")
    # root.geometry("350x300")
    root.geometry("380x335")
    # root.iconbitmap(resource_path("utils/icon.ico"))
    Application(root)
    root.mainloop()
    # files_in_db()
