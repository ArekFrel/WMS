import tkinter as tk
import os
import time
from tkinter import ttk, messagebox
from const import *


class Application(tk.Frame):

    @staticmethod
    def filtered_list(orders, text):
        return [x for x in orders if text in x]

    @staticmethod
    def get_orders(param):
        match param:
            case 'bt':
                query = f'SELECT DISTINCT PO FROM [dbo].[Brak_technologii]();'
            case 'allpos':
                query = f'SELECT DISTINCT [P.O.] FROM Sap Order By [P.O.];'
            case _:
                return []

        CURSOR.execute(query)
        result = CURSOR.fetchall()
        return [str(x[0]) for x in result]

    @staticmethod
    def get_to_open(po):
        QUERY = f"Select Plik From Technologia Where [PO] = {str(po)} AND Status_Op = 6 Order by Rysunek DESC;"
        print(QUERY)
        CURSOR.execute(QUERY)
        result = CURSOR.fetchall()
        return [str(x[0]) for x in result]

    def reset_data(self):
        Application.BTD = Application.get_orders('bt')
        Application.ALLPOS = Application.get_orders('allpos')
        self.cb_func()

    def delete_files(self):
        pass

    def get_files_to_open(self):
        Application.FILES_TO_OPEN = Application.get_to_open(self.listbox.selection_get())
        self.create_button_3()
        self.open_files()

    BTD = get_orders('bt')
    ALLPOS = get_orders('allpos')
    ORDERS = ALLPOS
    FILES_TO_OPEN = []

    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.is_list = False
        self.check_var = False
        self.entry = None
        self.text_entered = ''
        self.label = None
        self.label_empty = None
        self.label_entry = None
        self.label2 = None
        self.listbox = None
        self.scrollbar = None
        self.button = None
        self.button_2 = None
        self.button_3 = None
        self.button_4 = None
        self.button_3_text = None
        self.check_button = None
        self.msgbox = None
        self.create_widgets()

    def create_widgets(self):
        self.create_entry()
        self.create_listbox(tk.Variable(value=Application.ORDERS))
        self.create_scrollbar()
        self.create_label()
        self.create_button_1()
        self.create_button_4()
        self.create_check_button()

    def create_entry(self):
        self.entry = tk.Entry()
        self.entry.grid(row=2, column=1, sticky=tk.W)
        self.entry.focus()
        self.entry.bind("<KeyRelease>", self.entry_func)

    def create_listbox(self, var):
        self.listbox = tk.Listbox(width=20, listvariable=var, height=10, selectmode=tk.SINGLE)
        self.listbox.grid(row=3, column=1, rowspan=2)
        self.listbox.bind('<<ListboxSelect>>', self.item_selected)
        self.is_list = True

    def entry_func(self, event):
        self.text_entered = self.entry.get()
        self.lb_data_update()

    def create_scrollbar(self):
        self.scrollbar = ttk.Scrollbar(orient='vertical', command=self.listbox.yview)
        self.listbox['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.grid(row=3, column=2, rowspan=2, sticky=tk.NS)

    def create_label(self):
        self.label_empty = tk.Label(text=' '*15, font=('Arial', 16), height=2)
        self.label_empty.grid(row=0, column=0, rowspan=1, columnspan=3)
        self.label_entry = tk.Label(text='           Nr zlecenia:')
        self.label_entry.grid(row=2, column=0)

    def create_button_1(self):
        self.button = tk.Button(text='Usuń puste', command=self.files_in_db, width=12)
        self.button.grid(row=5, column=1, sticky=tk.NS)

    def create_button_2(self):
        self.button_2 = tk.Button(text='Otwórz BT', command=self.get_files_to_open, width=12)
        self.button_2.grid(row=6, column=1, sticky=tk.NS)

    def create_button_3(self):
        self.button_3_text = self.listbox.selection_get()
        self.button_3 = tk.Button(text=f'Otwórz 10 z {self.button_3_text}',
                                  command=self.open_files,
                                  wraplength=80,
                                  height=1,
                                  width=12)
        self.button_3.grid(row=4, column=0, sticky=tk.NS)

    def create_button_4(self):
        self.button_3 = tk.Button(text=f'RESET',
                                  command=self.reset_data,
                                  height=1,
                                  width=12)
        self.button_3.grid(row=6, column=3, sticky=tk.NS)

    def lb_data_update(self):
        if len(self.text_entered) > 0:
            f_var = Application.filtered_list(Application.ORDERS, self.text_entered)  # filter var
            var = tk.Variable(value=f_var)
        else:
            var = tk.Variable(value=Application.ORDERS)
        self.listbox.configure(listvariable=var)

    def cb_func(self):
        if self.check_var.get():
            Application.ORDERS = Application.BTD
            self.create_button_2()
        else:
            Application.ORDERS = Application.ALLPOS
            self.button_2.grid_forget()
        self.lb_data_update()

    def create_check_button(self):
        self.check_var = tk.BooleanVar()
        self.check_button = tk.Checkbutton(
            text='Brak Technolgii',
            variable=self.check_var,
            onvalue=True,
            offvalue=False,
            command=self.cb_func)
        self.check_button.grid(row=3, column=0, sticky=tk.NE)

    def info_print(self):
        self.check_button.toggle()
        # print(Application.FILES_TO_OPEN.pop(0))

    def files_in_db(self):
        print('')
        order_number = self.listbox.selection_get()
        if os.path.exists(PRODUCTION):
            query = f'SELECT id, Plik FROM TECHNOLOGIA WHERE PO = {order_number};'
            result = CURSOR.execute(query)
            table_files = [(t[0], t[1]) for t in result]
            po_cat = os.path.join(PRODUCTION, order_number)
            try:
                cat_content = os.listdir(po_cat)
                if len(cat_content) > 0:
                    cat_content = [file[0:-4] for file in cat_content if file.lower().endswith('.pdf')]
            except FileNotFoundError:
                cat_content = []

            deleting_query = ''
            num = 0
            while table_files:
                db_id, drawing = table_files.pop()
                if drawing not in cat_content:
                    query = f'DELETE FROM TECHNOLOGIA WHERE id = {db_id}; \n'
                    deleting_query += query
                    num += 1
            with open('../result.txt', 'w', encoding='UTF-8') as rf:
                rf.write(f'{deleting_query}')
            if len(deleting_query) > 1:
                CURSOR.execute(deleting_query)
                CURSOR.commit()

            self.message_box_del_succes(msg=f'Usunięto {num} rekordów')

        else:
            self.message_box_del_succes(msg=f'Brak Ścieżki Production')

    def item_selected(self, event):
        selected_item = self.listbox.selection_get()
        if selected_item:
            self.label_empty.configure(text=selected_item)

    def open_files(self):
        t = 0
        warn = False
        while Application.FILES_TO_OPEN and t <= 10:
            the_file = Application.FILES_TO_OPEN.pop(0) + '.pdf'
            space_index = the_file.find(' ')
            the_file = PRODUCTION + the_file.strip()[0:space_index] + '/' + the_file.strip()
            try:
                os.startfile(the_file, 'open')
                time.sleep(0.15)
                t += 1
            except FileNotFoundError:
                print(f'nie otwarto pliku: {the_file}')
                if not warn:
                    self.message_box()
                    warn = True
                continue

        if not Application.FILES_TO_OPEN:
            self.button_3.grid_forget()

    def message_box(self, msg):
        self.msgbox = messagebox.showwarning(title='Brak ścieżki', message=msg)

    def message_box_del_error(self, msg):
        self.msgbox = messagebox.showwarning(title='Brak ścieżki', message=msg)

    def message_box_del_succes(self, msg):
        self.msgbox = messagebox.showwarning(title='Usunięto pliki', message=msg)


# def files_in_db():
#     print('')
#     source_cat = 'W:/!!__PRODUKCJA__!!/1__Rysunkij/'
#     # order_number = self.listbox.selection_get()
#     order_number = '1503248'
#     if os.path.exists(source_cat):
#         query = f'SELECT id, Plik FROM TECHNOLOGIA WHERE PO = {order_number};'
#         result = CURSOR.execute(query)
#         table_files = [(t[0], t[1]) for t in result]
#         po_cat = os.path.join(source_cat, order_number)
#         try:
#             cat_content = os.listdir(po_cat)
#             if len(cat_content) > 0:
#                 cat_content = [file[0:-4] for file in cat_content if file.lower().endswith('.pdf')]
#         except FileNotFoundError:
#             cat_content = []
#
#         deleting_query = ''
#         num = 0
#         while table_files:
#             db_id, drawing = table_files.pop()
#             if drawing not in cat_content:
#                 query = f'DELETE FROM TECHNOLOGIA WHERE id = {db_id}; \n'
#                 deleting_query += query
#                 num += 1
#         with open('result.txt', 'w', encoding='UTF-8') as rf:
#             rf.write(f'{deleting_query}')
#         if len(deleting_query) > 1:
#             CURSOR.execute(deleting_query)
#             CURSOR.commit()
#
#         # self.message_box_del_succes(msg=f'Usunięto {num} rekordów')
#         print(deleting_query)
#     else:
#         self.message_box_del_succes(msg=f'Brak Ścieżki Production')


def main():
    root = tk.Tk()
    root.title("WMS")
    root.geometry("350x300")
    Application(root)
    root.mainloop()
    # files_in_db()


if __name__ == '__main__':
    main()
