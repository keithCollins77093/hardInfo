#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         hardInfo.py
#   Date Started:   March 18, 2022
#   Purpose:        Run Linux commands and collect output into usable Python objects.
#   Development:
#       2022-03-18:
#           Imported minimal set of GUI components from LinuxLogForensics and started removing unneeded
#           code from them.
#
#           The API should have a consistency such that all objects, which initially are just JSON structures
#           but will be classes, can be assembled into a single unified hardware and platform information
#           structure.
#           All information obtained will be store-able in timeStamped records in a table or tables so that
#           history can be reported if changes are made.  This also helps detect malware manipulating
#           the operating systems files or data bases storing the hardware information.
#           The OS collects hardware and other platform information on boot.
#           There needs to be a CLI along with the API.
#           A GUI using a property sheet component and a treeview component will also be required.
#           The Console can be included along with tool configuration, saving, and piping.
#           Piping between tools can then be done using Python classes and data dictionary maps and JSON
#           dict structures.
#
#       2022-03-19:  Git 'er done
#           Shell out to terminal for sudo.
#           Write classes for components in lshw json / dict.
#           Complete API on tools implemented so far.
#           Run history can be used for tool memory.
#           Save output to SQLite DB table.
#           CLI for tools and admin implemented so far.
#           GUI for tools and admin implemented so far.
#           Build and test:
#               Makable source archive
#               Wheel
#               Debian executable
#
#       2022-03-20:  Issues to include at GitHub
#           1.  List of Linux commands [possibly] to be included:
#               a.  uname
#               b.  lshw
#               c.  lscpu
#               d.  lsblk
#               e.  lsusb
#               f.  lspci
#               g.  lsscsi
#               h.  hdparm
#               i.  fdisk
#               j.  dmidecode
#               k.  free
#               l.  df, pydf
#               m.  dmesg
#               n.  biosdecode
#               o.  dig, host, ip, nmap, ping
#
#           2.  API documentation for initial lshw implementation.
#           3.  Explain import integrity checking.
#           4.  Planned CLI format, improvements over Linux versions where --json is available.
#           5.  Planned API capabilities, including those of hierarchical and relational databases.
#           6.  Possible application of text indexing.
#           7.  Planned GUI capabilities.
#           8.  Use of "less" for consistent formatting when piping input in, e.g. (see man pages):
#                   $: lscpu | less
#           9.  DB potential table potential for commands that have arguments that support the "list"
#                   argument, like lscpu.
#           10. see hardInfo.py header Development entry 2022-03-19 for more items.
#
#       2022-03-21: Command line features and arguments:
#           Generate:   Used to run the Linux command that generates the output that is input to this
#                           API builder and tool set.
#                       The result can be immediately saved to a file or to a database, or the user can
#                           run the API, CLI and GUI with the information in RAM only.
#                       Arguments:
#                           The data set identifier, which is the name of the linux command, preceded by a dash
#                               This is a flag which is either present or not.
#                               Absence means that the user wants all possible internal API object generation done.
#                               The user can also specify the particular ones to run in any order.
#           (See the Developer Documentation for a complete specification.)
#

import os, platform
import subprocess
from sys import stderr, stdout, stdin
from collections import OrderedDict
import json
from copy import deepcopy
from enum import Enum
from subprocess import Popen, PIPE
from datetime import datetime

from tkinter import Tk, messagebox

from model.Tools import Tool, LinuxCommand, ToolSet
#   from service.StackInfo import showEnvironmentInfo, UNAME, LSHW
from model.Lshw import Computer, Configuration, Capabilities, Children, HardwareId, System


PROGRAM_TITLE = "hardInfo Command Line Interface"


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


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


def lines_to_rows_parser(output: str):
    lines = output.split('\n')
    parsedLines = []
    for line in lines:
        parsedLines.append( line.split() )
    return parsedLines


def jsonText_to_map_parser( output: str ):
    #   print("\njsonText_to_map_parser:\t" + output)
    #   skip lines until the first '{' is found at the start of a line, excluding white space
    lines = output.split('\n')
    startIdx = 0
    while startIdx < len(lines) and not lines[startIdx].strip().startswith('{'):
        startIdx += 1
    if startIdx < len(lines):
        endIdx = startIdx + 1
        while endIdx < len(lines) and not lines[endIdx].strip().startswith('WARNING'):
            endIdx += 1
        if endIdx < len(lines):
            lines = lines[startIdx:endIdx]
            return json.loads('\n'.join(lines))
    return {}


class Help:

    commandList = ("help", "load", "store", "search", "update", "log", "exit")
    helpText = "\tFeatures:\t"
    helpMap = OrderedDict()
    for command in commandList:
        helpText += "\t" + command


class Dispatcher:
    """
    Coordinates invocation of the methods needed to respond to user commands.
    Arguments have three forms, and for the user's sake will always have only these three forms:
        1.  sub-command,
        2.  flag, i.e. a letter or word preceded by a dash, '-',
                which activates a particular feature or option, and
        3.  a flag plus an argument;
     If an argument is more than one word it will be quoted.
     Any command can have as many arguments as are required to unambiguously specify the program
        behavior desired.
    """

    CurrentAction = None

    def __init__(self):
        print("Lshw.Dispatcher does not instantiate")

    @staticmethod
    def do(action: Action, *args):
        Dispatcher.CurrentAction = action
        if action == Action.Generate:
            return Dispatcher.__generate(args)
        if action == Action.Help:
            return Dispatcher.__help(args)
        if action == Action.Load:
            return Dispatcher.__load(args)
        if action == Action.Store:
            return Dispatcher.__store(args)
        if action == Action.Search:
            return Dispatcher.__search(args)
        if action == Action.Update:
            return Dispatcher.__update(args)
        if action == Action.Log:
            return Dispatcher.__log(args)
        if action == Action.Exit:
            return Dispatcher.__exit(args)

    @staticmethod
    def __generate(*args):
        print("Dispatcher:\t" + str(Dispatcher.CurrentAction))
        return None

    @staticmethod
    def __help(*args):
        print("Dispatcher:\t" + str(Dispatcher.CurrentAction))
        print(Help.helpText)

    @staticmethod
    def __load(*args):
        print("Dispatcher:\t" + str(Dispatcher.CurrentAction))
        return None

    @staticmethod
    def __store(*args):
        print("Dispatcher:\t" + str(Dispatcher.CurrentAction))
        return None

    @staticmethod
    def __search(*args):
        print("Dispatcher:\t" + str(Dispatcher.CurrentAction))
        return None

    @staticmethod
    def __update(*args):
        print("Dispatcher:\t" + str(Dispatcher.CurrentAction))
        return None

    @staticmethod
    def __log(*args):
        print("Dispatcher:\t" + str(Dispatcher.CurrentAction))
        return None

    @staticmethod
    def __exit(*args):
        print("Dispatcher:\t" + str(Dispatcher.CurrentAction))
        print("Exiting hardInfo", file=stderr)
        exit(0)


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
    def getAndProcessInput(*args):
        print("Hardware Inventory Command Line running:")
        prompt = ""
        for arg in args:
            prompt += arg + '\t'
        print(prompt)
        prompt = 'hardInfo $'
        while True:
            print(prompt, end=":\t")
            command = tuple(input().split())
            if len(command) > 1:
                args = tuple(command[1:])
            else:
                args = ()
            print(command)
            if command[0] == 'exit':
                Dispatcher.do(Action.Exit, args)
            if command[0] == 'help':
                Dispatcher.do(Action.Help, args)
            if command[0] == 'load':
                Dispatcher.do(Action.Load, args)
            if command[0] == 'store':
                Dispatcher.do(Action.Store, args)
            if command[0] == 'search':
                Dispatcher.do(Action.Search, args)
            if command[0] == 'update':
                Dispatcher.do(Action.Update, args)
            if command[0] == 'log':
                Dispatcher.do(Action.Log, args)


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("600x400+100+50")
    mainView.title(PROGRAM_TITLE)

    args = []
    for command in Help.commandList:
        args.append(command)

    Conversation.getAndProcessInput("\tFeatures:\t", *args)


#   **********************************************************************************************************
#   TEST CODE RUN IN __main__ DURING DEVELOPMENT OF THIS MODULE:
    """
    lsLongTool = Tool(LinuxCommand.LS, ('-l',), lines_2_rows_parser)
    output = lsLongTool.run()
    print("output:")
    for outputRow in output:
        print(str(outputRow))
    """

    """
    Usage: uname [OPTION]...
    Print certain system information.  With no OPTION, same as -s.

  -a, --all                print all information, in the following order,
                             except omit -p and -i if unknown:
  -s, --kernel-name        print the kernel name
  -n, --nodename           print the network node hostname
  -r, --kernel-release     print the kernel release
  -v, --kernel-version     print the kernel version
  -m, --machine            print the machine hardware name
  -p, --processor          print the processor type (non-portable)
  -i, --hardware-platform  print the hardware platform (non-portable)
  -o, --operating-system   print the operating system
      --help     display this help and exit
      --version  output version information and exit

    """

    """
    unameToolSet = ToolSet(LinuxCommand.UNAME)
    unameToolSet.addTool("kernel-name", Tool(LinuxCommand.UNAME, ('-s',), lines_2_rows_parser))
    unameToolSet.addTool("nodename", Tool(LinuxCommand.UNAME, ('-n',), lines_2_rows_parser))
    unameToolSet.addTool("kernel-release", Tool(LinuxCommand.UNAME, ('-r',), lines_2_rows_parser))
    unameToolSet.addTool("kernel-version", Tool(LinuxCommand.UNAME, ('-v',), lines_2_rows_parser))
    unameToolSet.addTool("machine", Tool(LinuxCommand.UNAME, ('-m',), lines_2_rows_parser))
    unameToolSet.addTool("processor", Tool(LinuxCommand.UNAME, ('-p',), lines_2_rows_parser))
    unameToolSet.addTool("hardware-platform", Tool(LinuxCommand.UNAME, ('-i',), lines_2_rows_parser))
    unameToolSet.addTool("operating-system", Tool(LinuxCommand.UNAME, ('-o',), lines_2_rows_parser))
    unameToolSet.addTool("uname help", Tool(LinuxCommand.UNAME, ('--help',), lines_2_rows_parser))
    unameToolSet.addTool("uname version", Tool(LinuxCommand.UNAME, ('--version',), lines_2_rows_parser))

    unameOutput = OrderedDict()
    unameOutput['kernel-name']     = unameToolSet.runTool('kernel-name')
    unameOutput['nodename']     = unameToolSet.runTool('nodename')
    unameOutput['kernel-release']     = unameToolSet.runTool('kernel-release')
    unameOutput['kernel-version']     = unameToolSet.runTool('kernel-version')
    unameOutput['machine']     = unameToolSet.runTool('machine')
    unameOutput['processor']     = unameToolSet.runTool('processor')
    unameOutput['hardware-platform']     = unameToolSet.runTool('hardware-platform')
    unameOutput['operating-system']     = unameToolSet.runTool('operating-system')

    uname = UNAME(unameOutput)
    unameOutputFields = uname.getFiels()
    print()
    for name, value in unameOutputFields.items():
        print('\t' + name + ':\t' + str(value))
    print("uname command run finished")
    """

    """
    print("HardwareId.strMap['battery'].value:\t" + str(System.idMap['battery']))

    #   lshw -json
    lshwToolSet = ToolSet(LinuxCommand.LSHW)
    lshwToolSet.addTool('json', Tool(LinuxCommand.LSHW, ('-json', ), jsonText_to_map_parser))
    output = lshwToolSet.runTool('json')
    lshw = LSHW(output)
    lshw.list()
    print("\nLSHW Doc String:\n")
    print(LSHW.__doc__)

    configuration = {}
    if 'configuration' in lshw.getPropertyMap():
        for name, value in lshw.getPropertyMap()['configuration'].items():
            if not (isinstance(value, list) or isinstance(value, tuple) or isinstance(value, dict)):
                configuration[name] = value
    capabilities = {}
    if 'capabilities' in lshw.getPropertyMap():
        for name, value in lshw.getPropertyMap()['capabilities'].items():
            if not (isinstance(value, list) or isinstance(value, tuple) or isinstance(value, dict)):
                capabilities[name] = value


    children = {}

    if 'children' in lshw.getPropertyMap():
        children = lshw.getPropertyMap()['children']

    computer = Computer( lshw.getPropertyMap(), Configuration(configuration), Capabilities(capabilities),
                         Children(children))

    #   showEnvironmentInfo()
    #   mainView.mainloop()

    os_uname = os.uname()
    print("\nos.uname():" + "\n" + str(os.uname()))
    print("\nType of return value of os.uname():" + "\n" + str(type(os.uname())))
    print("\tos.uname().machine:\t" + str(os_uname.machine))

    print("\nplatform library module:   platform.platform():")
    print(str(platform.platform()))
    """

    """
    shellScriptCommand = '/home/keith/PycharmProjects/hardInfo/lshw_to_json_file.sh'
    print('RUNNING IN TERMINAL shellScriptCommand:\t' + shellScriptCommand)
    #   Runs: sudo lshw --json > lshw.json
    argv = ['gnome-terminal', '--', shellScriptCommand]
    sub = Popen(argv, stdout=PIPE, stderr=STDOUT)
    lastCommandRunTime = str(datetime.now())
    output, error_message = sub.communicate()
    print('output:\t' + output.decode('utf-8'))
    """
