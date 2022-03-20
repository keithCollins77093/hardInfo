#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         model/LsCpu.py
#   Date Started:   March 20, 2022
#   Purpose:        Run Linux commands and collect output into usable Python objects.
#   Development:
#       Sample / Test data file:
#           Name:       sampleOutput/lscpu/lscpu.output.2022_03_20.txt
#           Tool used:  scpu -a --json --extended > lscpu.output.2022_03_20.txt
#


from tkinter import Tk, messagebox


PROGRAM_TITLE = "lscpu Importer"


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("600x400+100+50")
    mainView.title(PROGRAM_TITLE)

    mainView.mainloop()