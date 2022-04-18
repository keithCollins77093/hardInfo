#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         model/LsBlk.py
#   Date Started:   March 23, 2022
#   Purpose:        Store and provide API for Linux lsblk command.
#   Development:
#       Arguments to include in the command line:
#           lsblk --json --all --zoned --output-all --paths
#

from enum import Enum
from subprocess import Popen, PIPE
from sys import stderr
from json import loads

from tkinter import Tk, messagebox, LabelFrame, BOTH, RAISED

from model.Installation import INSTALLATION_FOLDER
from view.Components import JsonTreeView

PROGRAM_TITLE = "lsblk API"
LSBLK_JSON_FILE = 'lsblk.json'


class Action(Enum):
    Generate    = 'Generate'
    Help        = "Help"
    Load        = 'Load'
    Store       = 'Store'
    Search      = 'Search'
    Update      = 'Update'
    Log         = 'Log'
    Exit        = 'Exit'

    def __str__(self):
        return self.value


class Dispatcher:

    def __init__(self):
        print("Lshw.Dispatcher does not instantiate")

    @staticmethod
    def do( action: Action):
        if action == Action.Generate:
            return Dispatcher.__generateLsBlkJsonFile()

    @staticmethod
    def __generateLsBlkJsonFile():
        #   lsblk --json --all --zoned --output-all --paths
        proc = Popen(['lsblk', '--json', '--all', '--zoned', '--output-all', '--paths'],
                     stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        jsonText = proc[0].decode('utf-8')
        errors = proc[1].decode('utf-8')
        if len(errors) > 0:
            print(errors, file=stderr)
        print("Saving output to:\t" + LSBLK_JSON_FILE)
        file = open(LSBLK_JSON_FILE, "w")
        file.write(jsonText)
        file.close()
        return jsonText


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("700x450+250+50")
    mainView.title(PROGRAM_TITLE)

    jsonText    = Dispatcher.do(Action.Generate)
    lsblkJson    = loads(jsonText)
    borderFrame = LabelFrame(mainView, text="Block Devices", border=5, relief=RAISED)
    jsonTreeView = JsonTreeView(borderFrame, lsblkJson, {"openBranches": True, "mode": "strict"})
    jsonTreeView.pack(expand=True, fill=BOTH)
    borderFrame.pack(expand=True, fill=BOTH)
    mainView.mainloop()
