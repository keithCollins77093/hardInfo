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
import os, platform
from collections import OrderedDict
import json

from tkinter import Tk, messagebox

from model.Tools import Tool, LinuxCommand, ToolSet
from service.StackInfo import showEnvironmentInfo, UNAME, LSHW
from model.Lshw import Computer, Configuration, Capabilities, Children, HardwareId, System


PROGRAM_TITLE = "hardInfo Command Line Interface"


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


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("600x400+100+50")
    mainView.title(PROGRAM_TITLE)

    #   TESTS:
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
