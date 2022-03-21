#   Project:        File Volume Indexer
#   Author:         George Keith Watson
#   Date Started:   February 9, 2019
#   Copyright:      (c) Copyright 2019 George Keith Watson
#   Module:         StackInfo
#   Date Started:   Imported from LinuxLogForensics on March 18, 2022.
#   Purpose:        View for managing scans of volumes and sub volumes.
#   Development:
#       ALSO:
#           vpddecode(8)
#       man mem:
#           /dev/mem  is  a character device file that is an image of the main memory of the computer.
#           It may be used, for example, to examine
#           (and even patch) the system.
#           Byte addresses in /dev/mem are interpreted as physical memory addresses.
#           References to nonexistent locations cause  errors  to  be
#           returned.
#
#       man vpddecode:
#           vpddecode  prints  the  "vital  product data" information that can be found in almost all IBM and
#           Lenovo computers. Available items are:
#               · BIOS Build ID
#               · Box Serial Number
#               · Motherboard Serial Number
#               · Machine Type/Model
#               Some systems have these additional items:
#               · BIOS Release Date
#               · Default Flash Image File Name
#
#       man acpi:   (needed to be installed on my Ubuntu 18 partition)
#           acpi - Shows battery status and other ACPI information
#           acpi Shows information from the /proc or the /sys filesystem, such as battery status or
#           thermal information.
#
#

import platform, os
from collections import OrderedDict
from copy import deepcopy

from bios_pnp import pnp

from tkinter import Tk, messagebox, BOTH, SUNKEN

#   from view.PlatformInfo import PlatformInfo
from view.PropertySheet import PropertySheet

PROGRAM_TITLE = "Stack Info"


class UNAME:

    def __init__(self, unameOutput: OrderedDict ):
        """

        :param unameOutput:
        """
        if not isinstance(unameOutput, OrderedDict):
            raise Exception("UNAME constructor - Invalid unameOutput argument:  " + str(unameOutput))
        if 'kernel-name' in unameOutput:
            self.kernelName     = unameOutput['kernel-name'][0][0]
        else:
            self.kernelName = ''
        if 'nodename' in unameOutput:
            self.nodename     = unameOutput['nodename'][0][0]
        else:
            self.nodename = ''
        if 'kernel-release' in unameOutput:
            self.kernelRelease     = unameOutput['kernel-release'][0][0]
        else:
            self.kernelRelease = ''
        if 'kernel-version' in unameOutput:
            self.kernelVersion     = ' '.join(unameOutput['kernel-version'][0])
        else:
            self.kernelVersion = ''
        if 'machine' in unameOutput:
            self.machine     = unameOutput['machine'][0][0]
        else:
            self.machine = ''
        if 'processor' in unameOutput:
            self.processor     = unameOutput['processor'][0][0]
        else:
            self.processor = ''
        if 'hardware-platform' in unameOutput:
            self.hardwarePlatform     = unameOutput['hardware-platform'][0][0]
        else:
            self.hardwarePlatform = ''
        if 'operating-system' in unameOutput:
            self.operatingSystem     = unameOutput['operating-system'][0][0]
        else:
            self.operatingSystem = ''

    def getFiels(self):
        return OrderedDict({
            'kernel-name': self.kernelName,
            'nodenam': self.nodename,
            'kernel-release': self.kernelRelease,
            'kernel-version': self.kernelVersion,
            'machine': self.machine,
            'processor': self.processor,
            'hardware-platform': self.hardwarePlatform,
            'operating-system': self.operatingSystem
        })

    def list(self):
        print("\nuname output:")
        print("\tkernel-name:\t" + str(self.kernelName))
        print("\tnodename:\t" + str(self.nodename))
        print("\tkernel-release:\t" + str(self.kernelRelease))
        print("\tkernel-version:\t" + str(self.kernelVersion))
        print("\tmachine:\t" + str(self.machine))
        print("\tprocessor:\t" + str(self.processor))
        print("\thardware-platform:\t" + str(self.hardwarePlatform))
        print("\toperating-system:\t" + str(self.operatingSystem))

"""
def showPlatformInfo():
    #print("showPlatformInfo")
    platformInfo = PropertySheetTopLevel(None, "platformInfo", getPlatformInfo())
"""

def showOpSysInfo():
    print("showOpSysInfo")


def showDeviceInfo():
    print("showDeviceInfo")

"""
def showEnvironmentInfo():
    #print("showEnvironmentInfo")
    info = {}
    nameIndex = []
    for name, value in os.environ.items():
        print( name + ":\t" + str(value))
        info[name] = value
        nameIndex.append(name)
    nameIndex.sort()

    design = {  'toplevel': {
                    'config': { 'borderwidth': 5,'relief': 'raised'},
                    'geometry': { 'width': 750, 'height': 500, 'x': 600, 'y': 50 }
                }
            }
    platformInfo = PropertySheetTopLevel(None, "platformInfo", (info, nameIndex), design)
    platformInfo.mainloop()
"""

def getPlatformInfo(indexed: bool=True):
    info        = {}
    info['Architecture']           = platform.architecture()
    info['Architecture Bits']      = info['Architecture'][0]
    info['Architecture Linkage Format'] = info['Architecture'][1]
    info['Machine']                = platform.machine()
    info['Network Name']           = platform.node()
    info['Platform']               = platform.platform()
    info['Processor']              = platform.processor()
    info['Python Build']           = platform.python_build()
    info['Python Build Number']    = info['Python Build'][0]
    info['Python Build Date']      = info['Python Build'][1]
    info['Python Compiler']        = platform.python_compiler()
    info['Python Branch']          = platform.python_branch()
    info['Python Implementation']  = platform.python_implementation()
    info['Python Revision']        = platform.python_revision()
    info['Python Version']         = platform.python_version()
    info['Python Version Tuple']   = platform.python_version_tuple()
    info['System']                 = platform.system()
    info['Release']                = platform.release()
    info['Version']                = platform.version()
    info['System Alias']           = platform.system_alias(info['System'],info['Release'],info['Version'])
    info['U-Name']                 = platform.uname()
    info['Java Version']           = platform.java_ver()        #  Version interface for Jython
    info['Win32 Version']          = platform.win32_ver()
    info['Mac Version']            = platform.mac_ver()
    #       AttributeError: module 'platform' has no attribute 'linux_distribution'
    #   info['Linux Distribution']     = platform.linux_distribution()
    #   nameIndex.append('Linux Distribution')
    info['LibC Version']           = platform.libc_ver()
    if indexed:
        nameIndex   = []
        nameIndex.append('Architecture')
        nameIndex.append('Architecture Bits')
        nameIndex.append('Architecture Linkage Format')
        nameIndex.append('Machine')
        nameIndex.append('Network Name')
        nameIndex.append('Platform')
        nameIndex.append('Processor')
        nameIndex.append('Python Build')
        nameIndex.append('Python Build Number')
        nameIndex.append('Python Build Date')
        nameIndex.append('Python Compiler')
        nameIndex.append('Python Branch')
        nameIndex.append('Python Implementation')
        nameIndex.append('Python Revision')
        nameIndex.append('Python Version')
        nameIndex.append('Python Version Tuple')
        nameIndex.append('System')
        nameIndex.append('Release')
        nameIndex.append('Version')
        nameIndex.append('System Alias')
        nameIndex.append('U-Name')
        nameIndex.append('Java Version')
        nameIndex.append('Win32 Version')
        nameIndex.append('Mac Version')
        nameIndex.append('LibC Version')
        return info, nameIndex
    return info


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()

if __name__ == '__main__':
    deviceList = list(pnp.get_all_pnp_devices_from_sysfs())
    print("\nAll PNP Devices:")
    for device in deviceList:
        print("\t" + str(device))

    mainView = Tk()
    mainView.geometry("700x500+100+50")
    mainView.title(PROGRAM_TITLE)
    mainView.layout = "grid"
    mainView.protocol('WM_DELETE_WINDOW', lambda: ExitProgram())

    info, nameIndex = getPlatformInfo(True)
    nameIndex.sort()

    design = {  'toplevel': {
                    'config': { 'borderwidth': 5,'relief': 'raised'},
                    'geometry': { 'width': 750, 'height': 500, 'x': 600, 'y': 50 }
                },
                'frame': {'text': 'Platform Properties', 'border': 3, 'relief': SUNKEN,
                          'padx': 10, 'pady': 10
                },
                'components': {
                    'input': {
                        'fieldName': { 'type': 'input component type',
                                       'config': 'input component configuration',
                                       'default': 'default value',
                                       'validValues': ('one', 'two', '...'),
                                       'validator': "a validator method"
                                       },
                        'another fieldName': {
                                        'type': 'input component type',
                                       'config': 'input component configuration',
                                       'default': 'default value',
                                       'validValues': ('one', 'two', '...'),
                                       'validator': "a validator method"

                                    }
                    }
                }
            }

    def messageReceiver(message: dict):
        print("Global message receiver:\t" + str(message))
        if 'source' in message:
            if message['source'] == 'PropertySheet.mouseClicked':
                pass
            if message['source'] == "PropertySheet.mouseDoubleClicked":
                pass

    #   popupPanel = PopupPanel(mainView, "Popup Panel",
    #                           geometryDef=PropertySheet.DEFAULT_DESIGN['toplevel']['geometry'],
    #                           border=5, relief=RAISED)
    propertySheet   = PropertySheet(mainView, "Environment Variables", (info, nameIndex), design=design, listener=messageReceiver )
    propertySheet.pack(expand=True, fill=BOTH)
    mainView.mainloop()

