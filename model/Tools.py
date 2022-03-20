#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         model.Tools
#   Date Started:   March 18, 2022
#   Purpose:        Store and make reusable linux command line parameter argument configurations.
#   Development:
#       This will fit as a model into a GUI component which is designed specifically for viewing, editing,
#       chaining, cloning, testing, etc., the users applications of standard Linux commands.
#

import subprocess
from sys import exc_info
from datetime import datetime
from enum import Enum
from copy import deepcopy
from collections import OrderedDict

from tkinter import Tk, messagebox

PROGRAM_TITLE = "Linux Toolbox"


class LinuxCommand(Enum):
    LS          = 'ls'

    UNAME       = 'uname'
    LSHW        = 'lshw'
    LSCPU       = 'lscpu'
    LSBLK       = 'lsblk'
    LSUSB       = 'lsusb'
    LSPCI       = 'lspci'
    LSSCSI      = 'lsscsi'
    HDPARM      = 'hdparm'
    FDISK       = 'fdisk'
    DMIDECODE   = 'dmidecode'
    BIOSDECODE  = 'biosdecode'
    ACPI        = 'acpi'

    def __str__(self):
        return self.value


class CommandRun:
    """
    stores the full command and the output text produced by it, including if it resulted in an error message.
    """
    def __init__(self, outputText: str, commandList: tuple):
        if not isinstance(outputText, str):
            raise Exception("CommandRun constructor - Invalid outputText argument:  " + str(outputText))
        if not isinstance(commandList, tuple):
            raise Exception("CommandRun constructor - Invalid commandList argument:  " + str(commandList))
        self.outputText = outputText
        self.commandList = commandList

    def getState(self):
        return self.commandList, self.outputText


class Tool:
    """
    This represents a single argument list applied to a particular linux terminal command.
    Each can have its own output format so each will potentially need to have its own output parsing
    method.
    """

    def __init__(self, commandName: LinuxCommand, argumentList: tuple, outputParser, logging: bool=True):
        Tool.checkArguments(commandName, argumentList, outputParser, logging)
        self.commandName    = commandName
        self.argumentList   = deepcopy(argumentList)
        self.outputParser   = outputParser
        self.outputText = None
        self.lastRunTime = None
        self.lastRunOutput = None
        self.logging = logging
        if self.logging:
            self.runlog = OrderedDict()
        else:
            self.runLog = None

    def run(self):
        self.content = None
        try:
            commandList = [str(self.commandName)]
            for argument in self.argumentList:
                commandList.append(argument)
            sub     = subprocess.Popen(commandList, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
            commandList = tuple(commandList)
            self.lastRunTime = datetime.now()
            output, error_message = sub.communicate()
            self.lastRunOutput = output.decode('utf-8')
            if self.logging:
                self.runlog[self.lastRunTime]   = CommandRun(self.lastRunOutput, commandList)
            return self.outputParser(self.lastRunOutput)
        except Exception:
            self.lastRunOutput = 'at:\t' + self.lastRunTime.ctime() + '\n'
            for line in exc_info():
                self.lastRunOutput += str(line) + '\n'
            return self.lastRunOutput

    @staticmethod
    def checkArguments(commandName: LinuxCommand, argumentList: tuple, outputParser, logging: bool):
        if not isinstance(commandName, LinuxCommand):
            raise Exception("Tool.checkArguments - Invalid commandName argument:  " + str(commandName))
        if not callable(outputParser):
            raise Exception("Tool.checkArguments - Invalid outputParser argument:  " + str(outputParser))
        if not isinstance(argumentList, tuple):
            raise Exception("Tool.checkArguments - Invalid argumentList argument:  " + str(argumentList))
        if not isinstance(logging, bool):
            raise Exception("Tool.checkArguments - Invalid logging argument:  " + str(logging))

    def list(self):
        print("\nTool:\t" + str(self.commandName))
        print("\targument list:\t" + str(self.argumentList))


class ToolSet:
    """
    Each instance of this class is a single Linux command.
    Each Tool in each instance is an instance of that command configured with a particular argument list.
    """
    def __init__(self, commandName: LinuxCommand):
        if not isinstance(commandName, LinuxCommand):
            raise Exception("ToolSet constructor - Invalid commandName argument:  " + str(commandName))
        self.commandName = commandName
        self.tools = OrderedDict()

    def addToolConfig(self, name: str, argumentList: tuple, outputParser, logging: bool=True):
        Tool.checkArguments(self.commandName, argumentList, outputParser, logging)
        if not isinstance(name, str):
            raise Exception("ToolSet.addToolConfig - Invalid name argument:  " + str(name))
        self.tools[name] = Tool(self.commandName, argumentList, outputParser, logging)

    def addTool(self, name: str, tool: Tool):
        if not isinstance(name, str):
            raise Exception("ToolSet.addTool - Invalid name argument:  " + str(name))
        if not isinstance(tool, Tool):
            raise Exception("ToolSet.addTool - Invalid tool argument:  " + str(tool))
        self.tools[name] = tool

    def removeTool(self, name: str):
        if name in self.tools:
            del (self.tools[name])

    def runTool(self, name: str):
        if not isinstance(name, str):
            raise Exception("ToolSet.addTool - Invalid name argument:  " + str(name))
        if name in self.tools:
            return self.tools[name].run()
        return None


class LinuxTools:
    """
    This is a collection of ToolSet(s).
    """
    def __init__(self, commandName: LinuxCommand):
        pass


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
