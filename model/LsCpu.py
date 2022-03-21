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
from os.path import isfile
from subprocess import Popen, PIPE, STDOUT
from json import loads
from collections import OrderedDict
from copy import deepcopy
from enum import Enum
from datetime import datetime

from tkinter import Tk, messagebox, BOTH

from view.Components import JsonTreeView


PROGRAM_TITLE = "lscpu Importer"
LSCPU_JSON_FILE = 'lscpu.json'


class CPU_Field:

    def __init__(self, field: dict):
        if not isinstance(field, dict) or 'field' not in field or 'data' not in field:
            raise Exception("CPU_Field constructor - Invalid field argument:  " + str(field))
        self.attributes = deepcopy(field)
        self.name = field['field']
        if self.name == "Flags:":
            self.data = field['data'].split()
        else:
            self.data = field['data']

    def getName(self):
        return self.name

    def getData(self):
        return self.data

    def getAttributes(self):
        return deepcopy(self.attributes)


class CPU_FieldSet:

    def __init__(self, lscpuJson: dict):
        if not isinstance(lscpuJson, dict) or not "lscpu" in lscpuJson:
            raise Exception("CPU_FieldSet constructor - Invalid lscpuJson argument:  " + str(lscpuJson))
        self.attributes = deepcopy(lscpuJson)
        self.cpuFields = OrderedDict()
        for fieldMap in lscpuJson["lscpu"]:
            if "field" not in fieldMap or "data" not in fieldMap:
                raise Exception("CPU_FieldSet constructor - Invalid fieldMap in lscpuJson argument:  " + str(fieldMap))
            self.cpuFields[fieldMap['field']] = CPU_Field(fieldMap)

    def getAttributes(self):
        return deepcopy(self.attributes)

    def getCPU_Field(self, name: str):
        if name in self.cpuFields:
            return deepcopy(self.cpuFields[name])
        return None


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
            return Dispatcher.__generateLscpuJsonFile()

    @staticmethod
    def __generateLscpuJsonFile():
        proc = Popen(['lscpu', '--json'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        jsonText = proc[0].decode('utf-8')
        print("Saving output to:\t" + LSCPU_JSON_FILE)
        file = open(LSCPU_JSON_FILE, "w")
        file.write(jsonText)
        file.close()
        return jsonText


class Conversation:

    userLog = OrderedDict()

    class LogEntry:
        def __init__(self, timeStamp: datetime, description: str, attributes: dict ):
            if not isinstance(timeStamp, datetime):
                raise Exception("Conversation.LogEntry constructor - Invalid timeStamp argument:  " + str(timeStamp))
            if not isinstance(description, str):
                raise Exception("Conversation.LogEntry constructor - Invalid description argument:  " + str(description))
            if not isinstance(attributes, dict):
                raise Exception("Conversation.LogEntry constructor - Invalid attributes argument:  " + str(attributes))
            self.timeStamp = deepcopy(timeStamp)
            self.description = description
            self.attributes = deepcopy(attributes)

        def storeLog(self):
            pass

    def __init__(self):
        print("Lshw.Conversation does not instantiate")

    @staticmethod
    def getAndProcessInput():
        jsonText = None

        if isfile(LSCPU_JSON_FILE):
            prompt = "lscpu json storage file already exists.  Would you like to update it? (y/Y or n/N)"
            print(prompt, end=":\t")
            response = input()
            if response in ('y', 'Y'):
                jsonText = Dispatcher.do(Action.Generate)
                #   print("Line Count:\t" + str(len(outputText.split('\n'))))
            else:
                lscpuJsonFile = open(LSCPU_JSON_FILE, "r")
                jsonText = lscpuJsonFile.read()
                lscpuJsonFile.close()
        else:
            jsonText = Dispatcher.do(Action.Generate)

        if jsonText is not None:
            lscpuJson = loads(jsonText)
            jsonText = None

            #   Construct the internal objects storing the output for API use.
            cpu_FieldSet = CPU_FieldSet(lscpuJson)

            prompt = "Would you line to see the lscpu output in a GUI Tree window? (y/Y or n/N)"
            print(prompt, end=":\t")
            response = input()
            if response in ('y', 'Y'):
                print('Generating view')
                jsonTreeView = JsonTreeView(mainView, lscpuJson, {"openBranches": True, "mode": "strict"})
                jsonTreeView.pack(expand=True, fill=BOTH)
                mainView.mainloop()


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("600x400+100+50")
    mainView.title(PROGRAM_TITLE)
    Conversation.getAndProcessInput()
