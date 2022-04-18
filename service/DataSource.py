#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         service/DataSource.py
#   Date Started:   March 21, 2022
#   Purpose:        Interface with the Linux data sources needed for API construction, generally by running
#                   its commands using subprocess.Popen().
#   Development:
#

from subprocess import Popen, PIPE
from os.path import isfile
from json import loads

from tkinter import Tk, messagebox, BOTH

from model.Installation import INSTALLATION_FOLDER, LSHW_JSON_FILE
from view.Components import JsonTreeView

PROGRAM_TITLE = "Data Source Adapter"


class Hardware:

    def __init__(self):
        pass

    @staticmethod
    def generateLshwJsonFile():
        print("Enter your password to run lshw as super user", end=":\t")
        interface = input()
        argument = "{input}\n"
        bytestr = bytes(argument.format(input=interface).encode('utf-8'))
        proc = Popen(['sudo', '-S', 'lshw', '-json'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(input=bytestr)
        jsonText = proc[0].decode('utf-8')
        print("Saving output to:\t" + LSHW_JSON_FILE)
        file = open(LSHW_JSON_FILE, "w")
        file.write(jsonText)
        file.close()
        #   print("Line Count:\t" + str(len(outputText.split('\n'))))
        return jsonText

    @staticmethod
    def getLshw(listener, mainView):
        computer = None
        if listener is not None and not callable(listener):
            raise Exception("Hardware.getLshw - Invalid listener argument:  " + str(listener))
        jsonText = None

        if isfile(LSHW_JSON_FILE):
            prompt = "lshw json storage file already exists.  Would you like to update it? (y/Y or n/N)"
            print(prompt, end=":\t")
            response = input()
            if response in ('y', 'Y'):
                jsonText = Hardware.generateLshwJsonFile()
            else:
                lshwJsonFile = open(LSHW_JSON_FILE, "r")
                jsonText = lshwJsonFile.read()
                lshwJsonFile.close()
        else:
            jsonText = Hardware.generateLshwJsonFile()

        if jsonText is not None:
            #   Construct the internal objects storing the output for API use.
            propertyMap = loads(jsonText)

            configuration = {}
            if 'configuration' in propertyMap:
                for name, value in propertyMap['configuration'].items():
                    if not (isinstance(value, list) or isinstance(value, tuple) or isinstance(value, dict)):
                        configuration[name] = value
            capabilities = {}
            if 'capabilities' in propertyMap:
                for name, value in propertyMap['capabilities'].items():
                    if not (isinstance(value, list) or isinstance(value, tuple) or isinstance(value, dict)):
                        capabilities[name] = value
            children = {}
            if 'children' in propertyMap:
                children = propertyMap['children']

            #   Build the API.
            #   The type of computer is model.Lshw.Computer.
            computer = listener({'source': 'Hardware.getLshw',      'jsonDB': propertyMap,
                                'configuration': configuration,     'capabilities': capabilities,
                                'children': children})

            print("lshw API is available as \"computer\"")

            prompt = "Would you line to see the lshw output in a GUI Tree window? (y/Y or n/N)"
            print(prompt, end=":\t")
            response = input()
            if response in ('y', 'Y'):
                print('Generating view')
                jsonTreeView = JsonTreeView(mainView, propertyMap, {"openBranches": True, "mode": "strict"})
                jsonTreeView.pack(expand=True, fill=BOTH)
                mainView.mainloop()
        return computer


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("700x500+300+50")
    mainView.title(PROGRAM_TITLE)

    mainView.mainloop()
