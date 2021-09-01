import os
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from importlib.machinery import SourceFileLoader
path = '/multi_arinc/config.py'
module_name = 'config.py'
loader = SourceFileLoader(module_name, path)

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

root = Tk()

root.title("Multifunctional ARINC Parsing")
root.geometry('400x320')


def run1():
    win = Toplevel()
    win.wm_title("Инструкция")
    text = scrolledtext.ScrolledText(win)
    text.pack(expand=True, fill='both')
    with open('Инструкция.txt', 'r', encoding='utf-8') as log:
        file_log = log.readlines()
        text.delete(1.0, END)
        for element in file_log:
            text.insert(END, element)
    but = Button(win, text='Всё ясно', command=win.destroy, activebackground='salmon')
    but.pack()


def run2():
    os.system('python3 checking.py')


def run3():
    os.system('python3 sintez_parsing.py')
    messagebox.showinfo(title='SINTEZ: запросы и картография', message='Скрипт завершен')


def run4():
    os.system('python3 korinf_parsing.py')
    messagebox.showinfo(title='КОРИНФ для мест ЗКП - картография', message='Скрипт завершен')


def run5():
    os.system('python3 radar_screen_orl_parsing.py')
    messagebox.showinfo(title='ОРЛ-А - картография', message='Скрипт завершен')


btn1 = Button(root, text="ИНСТРУКЦИЯ", bg="light sky blue", fg="white", command=run1, height=3, width=100)
btn1.pack()

btn2 = Button(root, text="Проверка ARINC на ошибки", bg="steel blue", fg="white", command=run2, height=3, width=100)
btn2.pack()

btn3 = Button(root, text="SINTEZ: запросы и картография", bg="light sky blue", fg="white", command=run3, height=3,
              width=100)
btn3.pack()

btn4 = Button(root, text="КОРИНФ для мест ЗКП - картография", bg="steel blue", fg="white", command=run4, height=3,
              width=100)
btn4.pack()

btn5 = Button(root, text="ОРЛ-А - картография", bg="light sky blue", fg="white", command=run5, height=3, width=100)
btn5.pack()

root.mainloop()
