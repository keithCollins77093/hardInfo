#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         model/LsUsb.py
#   Date Started:   March 23, 2022
#   Purpose:        Store and provide API for Linux lsusb command.
#   Development:
#       Arguments to include in the command line:
#           lsusb -v
#

from enum import Enum
from subprocess import Popen, PIPE
from sys import stderr
from json import loads, dumps
from datetime import datetime


from tkinter import Tk, messagebox, LabelFrame, BOTH, RAISED

from model.Installation import INSTALLATION_FOLDER
from view.Components import JsonTreeView

PROGRAM_TITLE = "lsblk API"
LSUSB_TEXT_FILE = 'lsusb.txt'


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


class LS_USB_OUTPUT_TEMPLATE:
    #   The list of USB devices initiall includes only a template as its single element.
    #   This is cloned and filled as instances are found during the line-by-line parse of the output.
    #   See:    lsusb.txt
    #   Attributes are occasionally missing and if so the template is included but left blank.
    #   Extra attributes not in the template are recorded.  This can be done bu including everything
    #   at the same indent level.
    LIST    = [
        {   "ID": None,
            "Bus": None,
            "Device": None,
            "attributes":    {
                "bLength": None,
                "bDescriptorType": None,
                "bcdUSB": None,
                "bDeviceClass": None,
                "bDeviceSubClass": None,
                "bDeviceProtocol": None,
                "bMaxPacketSize0": None,
                "idVendor": None,
                "idProduct": None,
                "bcdDevice": None,
                "iManufacturer": None,
                "iProduct": None,
                "iSerial": None,
                "bNumConfigurations": None,
                "Configuration Descriptor": {
                    "bLength": None,
                    "bDescriptorType": None,
                    "wTotalLength": None,
                    "bNumInterfaces": None,
                    "bConfigurationValue": None,
                    "iConfiguration": None,
                    "bmAttributes": None,
                    "bmAttrList": [],
                    "MaxPower": None,
                    "Interface Descriptor": {
                        "bLength": None,
                        "bDescriptorType": None,
                        "bInterfaceNumber": None,
                        "bAlternateSetting": None,
                        "bNumEndpoints": None,
                        "bInterfaceClass": None,
                        "bInterfaceSubClass": None,
                        "bInterfaceProtocol": None,
                        "iInterface": None,
                        "HID Device Descriptor":    {   #   This entire entity is missing in the second ont in the sample output
                            "bLength": None,
                            "bDescriptorType": None,
                            "bcdHID": None,
                            "bCountryCode": None,
                            "bNumDescriptors": None,
                            "bDescriptorType": None,
                            "wDescriptorLength": None,
                        },
                        "Report Descriptors":   {}, #   This entire entity is missing in the second ont in the sample output
                        "Endpoint Descriptor":  {
                            "bLength": None,
                            "bDescriptorType": None,
                            "bEndpointAddress": None,
                            "bmAttributes": None,
                            "bmAttrMap": {
                                "Transfer Type": None,
                                "Synch Type": None,
                                "Usage Type": None,
                            },
                            "wMaxPacketSize": None,
                            "bInterval": None,
                        },
                    }
                }
            }
        },
    ]


    """
    Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Device Descriptor:
      bLength                18
      bDescriptorType         1
      bcdUSB               2.00
      bDeviceClass            9 Hub
      bDeviceSubClass         0 Unused
      bDeviceProtocol         0 Full speed (or root) hub
      bMaxPacketSize0        64
      idVendor           0x1d6b Linux Foundation
      idProduct          0x0002 2.0 root hub
      bcdDevice            4.15
      iManufacturer           3
      iProduct                2
      iSerial                 1
      bNumConfigurations      1
      Configuration Descriptor:
        bLength                 9
        bDescriptorType         2
        wTotalLength           25
        bNumInterfaces          1
        bConfigurationValue     1
        iConfiguration          0
        bmAttributes         0xe0
          Self Powered
          Remote Wakeup
        MaxPower                0mA
        Interface Descriptor:
          bLength                 9
          bDescriptorType         4
          bInterfaceNumber        0
          bAlternateSetting       0
          bNumEndpoints           1
          bInterfaceClass         9 Hub
          bInterfaceSubClass      0 Unused
          bInterfaceProtocol      0 Full speed (or root) hub
          iInterface              0
          Endpoint Descriptor:
            bLength                 7
            bDescriptorType         5
            bEndpointAddress     0x81  EP 1 IN
            bmAttributes            3
              Transfer Type            Interrupt
              Synch Type               None
              Usage Type               Data
            wMaxPacketSize     0x0004  1x 4 bytes
            bInterval              12
    
    Bus 001 Device 002: ID 8087:0020 Intel Corp. Integrated Rate Matching Hub
    Device Descriptor:
      bLength                18
      bDescriptorType         1
      bcdUSB               2.00
      bDeviceClass            9 Hub
      bDeviceSubClass         0 Unused
      bDeviceProtocol         1 Single TT
      bMaxPacketSize0        64
      idVendor           0x8087 Intel Corp.
      idProduct          0x0020 Integrated Rate Matching Hub
      bcdDevice            0.00
      iManufacturer           0
      iProduct                0
      iSerial                 0
      bNumConfigurations      1
      Configuration Descriptor:
        bLength                 9
        bDescriptorType         2
        wTotalLength           25
        bNumInterfaces          1
        bConfigurationValue     1
        iConfiguration          0
        bmAttributes         0xe0
          Self Powered
          Remote Wakeup
        MaxPower                0mA
        Interface Descriptor:
          bLength                 9
          bDescriptorType         4
          bInterfaceNumber        0
          bAlternateSetting       0
          bNumEndpoints           1
          bInterfaceClass         9 Hub
          bInterfaceSubClass      0 Unused
          bInterfaceProtocol      0 Full speed (or root) hub
          iInterface              0
          Endpoint Descriptor:
            bLength                 7
            bDescriptorType         5
            bEndpointAddress     0x81  EP 1 IN
            bmAttributes            3
              Transfer Type            Interrupt
              Synch Type               None
              Usage Type               Data
            wMaxPacketSize     0x0001  1x 1 bytes
            bInterval              12
    
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Device Descriptor:
      bLength                18
      bDescriptorType         1
      bcdUSB               2.00
      bDeviceClass            9 Hub
      bDeviceSubClass         0 Unused
      bDeviceProtocol         0 Full speed (or root) hub
      bMaxPacketSize0        64
      idVendor           0x1d6b Linux Foundation
      idProduct          0x0002 2.0 root hub
      bcdDevice            4.15
      iManufacturer           3
      iProduct                2
      iSerial                 1
      bNumConfigurations      1
      Configuration Descriptor:
        bLength                 9
        bDescriptorType         2
        wTotalLength           25
        bNumInterfaces          1
        bConfigurationValue     1
        iConfiguration          0
        bmAttributes         0xe0
          Self Powered
          Remote Wakeup
        MaxPower                0mA
        Interface Descriptor:
          bLength                 9
          bDescriptorType         4
          bInterfaceNumber        0
          bAlternateSetting       0
          bNumEndpoints           1
          bInterfaceClass         9 Hub
          bInterfaceSubClass      0 Unused
          bInterfaceProtocol      0 Full speed (or root) hub
          iInterface              0
          Endpoint Descriptor:
            bLength                 7
            bDescriptorType         5
            bEndpointAddress     0x81  EP 1 IN
            bmAttributes            3
              Transfer Type            Interrupt
              Synch Type               None
              Usage Type               Data
            wMaxPacketSize     0x0004  1x 4 bytes
            bInterval              12
    
        """

    def __init__(self):
        pass


class Dispatcher:

    def __init__(self):
        print("Lshw.Dispatcher does not instantiate")

    @staticmethod
    def do( action: Action):
        if action == Action.Generate:
            return Dispatcher.__generateLsUsbTextFile()

    @staticmethod
    def __generateLsUsbTextFile():
        #   to make sure output is current, run first: udevadm settle
        proc = Popen(['udevadm', 'settle'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()

        proc = Popen(['lsusb', '-v'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        lineText = proc[0].decode('utf-8')
        errors = proc[1].decode('utf-8')
        if len(errors) > 0:
            print(errors, file=stderr)
        print("Saving output to:\t" + LSUSB_TEXT_FILE)
        file = open(LSUSB_TEXT_FILE, "w")
        file.write(lineText)
        file.close()
        return lineText


def lineParse(lineText: str, runTime: datetime):
    """
    Since the makers of Linux make absolutely no guarantees and disclaim all warranties possible,
    there is no guarantee that the output of the lscpu command will actually be tree structured in
    any parse-able way.
    Therefore, a attempt will be made with a line using line examination of spacing, format, and/or content
    to structure the information present in the output.
    It is possible that names of properties will not change, and that the names of their context branches
    will not change, so these could be used as a template.
    For quality and security, both line-by-line parsing should be attempted and use of a tree-structure-template,
    along with an integrity check and production of a discrepancy report to user and to developers.
    :param lineText:
    :param runTime:
    :return:
    """
    print("lineParse: converting to python map / json")
    json = {'Command': 'lsusb',
            'Run Time': runTime.ctime(),
            'lines': []
            }
    lines = lineText.split('\n')
    lineIdx = 0
    prevIndent = 0
    currMap = json
    prevMap = json
    prevName = None
    currName = None
    indent = 0
    for line in lines:
        if len(line.strip()) > 0:
            if len(line.split(':')) == 1:
                parts = line.split()
                if len(parts) == 1:
                    prevName = parts[0]
                else:
                    print(line)
                    if line.strip().endswith(':'):
                        parts = [line.strip(),]
                indent = 0
                while indent < len(line) and line[indent].isspace():
                    indent += 1
                if indent > prevIndent:
                    if len(parts) == 2:
                        if prevName is not None:
                            currMap[prevName] = {}
                            currMap[prevName][parts[0]] = parts[1]
                            currName = prevName
                            prevName = None
                        else:
                            #   Need to include the rest of parts[], not just the second element
                            currMap[currName][parts[0]] = parts[1]
                    elif len(parts) == 1:
                        pass
                elif indent == prevIndent:
                    if len(parts) == 2:
                        currMap[currName][parts[0]] = parts[1]
                    elif len(parts) == 1:
                        prevMap = currMap
                        currMap = currMap[currName]
                        prevName = currName
                        currName = parts[0]
                else:       #   moving back up, but how many levels?
                    break
                    pass
            else:   #   Add to current list
                currName = line.strip()
                currMap[currName] = {}

                json['lines'].append({})
                json['lines'][lineIdx ]['indent'] = indent
                json['lines'][lineIdx ]['text'] = line
                lineIdx += 1
            prevIndent = indent
    return json


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("700x450+250+50")
    mainView.title(PROGRAM_TITLE)

    runTimeStamp    = datetime.now()
    lineText    = Dispatcher.do(Action.Generate)
    lsusbJson   = lineParse(lineText, runTimeStamp)

    borderFrame = LabelFrame(mainView, text="Block Devices", border=5, relief=RAISED)
    jsonTreeView = JsonTreeView(borderFrame, lsusbJson, {"openBranches": True, "mode": "strict"})
    jsonTreeView.pack(expand=True, fill=BOTH)
    borderFrame.pack(expand=True, fill=BOTH)
    mainView.mainloop()
