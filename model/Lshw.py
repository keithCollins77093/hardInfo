#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         model/Lshw
#   Date Started:   March 19, 2022
#   Purpose:        Classes storing the contents of the output from an invocation of:   sudo lshw -json.
#   Development:
#       2022-03-19:
#           Need "comprehensive" getter methods
#               1.  list all instances of a particular class of hardware,
#                   include all locations in the hierarchy of hardware where they occur.
#               2.  find all instances of a particular class of hardware with a particular attribute name.
#               3.  find all instances of a particular class of hardware with a particular attribute name
#                   which attribute has a particular value.
#               4.  grep type searching of attributes:
#                       by attribute name or value
#                       by hardware instance type and attribute name or value,
#               5.  ...
#
#           Separate, or sub project idea:
#
#           This is a hierarchical database, so any search or filter method applicable to a hierarchical
#           database should be considered.
#           Attribute name indexes:
#               Scan hierarchy for all occurrences of a particular attribute name, as if it were a column.
#               Use hash table to record the attribute value as the key and the path to the location
#                   as the value, with a bucket for multiple instances of the same value.
#               Search for exact match is then just a hash table access.
#               Grep and fuzzy matching require a scan of the entire key set, so this is slower, O(n).
#
#           Security:
#               Although the attribute managing code in each class of hardware is repetitious and could be placed
#               in their common super class, System, it is better security to repeat the 25 or so common lines
#               of attribute management code in each hardware class.  Malware might be able to access all of
#               the subclass' individual attributes by cracking the base class only, otherwise.
#
#   2022-03-20:
#       man lshw:
#       __________________________________________________________________________________________________________
#        DESCRIPTION
#        lshw is a small tool to extract detailed information on the hardware configuration of the machine.
#        It can report exact memory  configuration,  firmware  version, mainboard configuration,
#        CPU version and speed, cache configuration, bus speed, etc. on DMI-capable
#        x86 or IA-64 systems and on some PowerPC machines (PowerMac G4 is known to work).
#
#        It currently supports DMI (x86 and IA-64 only), OpenFirmware device tree (PowerPC only),
#        PCI/AGP, CPUID (x86), IDE/ATA/ATAPI,  PCM‐CIA (only tested on x86), SCSI and USB.
#           ...
#        -json  Outputs the device tree as a JSON object (JavaScript Object Notation).
#           ...
#        -dump filename
#               Dump collected information into a file (SQLite database).
#       __________________________________________________________________________________________________________
#       I tested the -dump filename option and it failed showing the usage help output instead of doing what
#       the man page claims.  Fortunately, Linux comes with no warranty, or someone would be in trouble.
#       The 'organic' table layout would have a table for each class of hardware and therefore only one or a few
#           records in each table.  There are 26 classes of hardware and generally only one instance of each.
#           This is likely the reason this feature was discontinued, but there are more innovative database
#           design architectures that would work well on this information.
#       This does show that this feature was included at some point and perhaps still is in some Linux releases,
#       so it would be a good idea to produce a platform independent version of it in Python.
#
#       Requirements:
#           Redundancy through an encoded mirror.  If there is a record with exposed field names, there
#               should be a pickled BLOB with the same information and no field names visible.
#           Transparency through field / attribute / column naming standard identical to that in output.
#           There should be a master table with only those fields which all classes have in common and the
#               rest in a map / BLOB field.
#           For simplicity, there could be a monster table with all possible fields in it allowing those
#               classes without some to have blanks.
#           There could also be a table listing the different classes and containing a list BLOB of the
#               names of the attributes in each class.
#
from os.path import isfile
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
from sys import stderr, stdout
from collections import OrderedDict
from copy import deepcopy           #   Security: prevent passed in argument from being changed from outside.
from enum import Enum
from json import loads

from tkinter import Tk, messagebox, BOTH

from model.Installation import INSTALLATION_FOLDER
from view.Components import JsonTreeView


PROGRAM_TITLE = "lshw classes module"


class HardwareId(Enum):
    Core            = 'core'
    Firmware        = 'firmware'
    CPU             = 'cpu'
    Cache           = 'cache'       #   always followed by ':n' where n is a sequential index.
    Memory          = 'memory'
    Bank            = 'bank'        #   always followed by ':n' where n is a sequential index.
    PCI             = 'pci'         #   always followed by ':n' where n is a sequential index.
    Display         = 'display'
    Communication   = 'communication'
    USB             = 'usb'         #   always followed by ':n' where n is a sequential index.
    UsbHost         = 'usbhost'
    MultiMedia      = 'multimedia'
    Generic         = 'generic'     #   always followed by ':n' where n is a sequential index.
    FireWire        = "firewire"
    Network         = 'network'
    ISA             = 'isa'
    Storage         = 'storage'
    SCSI            = 'scsi'
    Disk            = 'disk'
    Volume          = 'volume'      #   always followed by ':n' where n is a sequential index.
    LogicalVolume   = 'logicalvolume'   #   always followed by ':n' where n is a sequential index.
    CD_ROM          = 'cdrom'
    Medium          = 'medium'
    Battery         = 'battery'

    def __str__(self):
        return self.value


class Capabilities( OrderedDict ):

    def __init__(self, capabilities: dict):
        OrderedDict.__init__(self, capabilities)


class CPU_Capabilities( Capabilities ):

    def __init__(self, capabilities: dict):
        Capabilities.__init__(self, capabilities)

        #   "x86-64" : "64bits extensions (x86-64)",
        self.x86_64 = None
        self.fpu    = None
        self.fpu_exception  = None
        self.wp = None
        self.vme = None
        self.de = None
        self.pse = None
        self.tsc = None
        self.msr = None
        self.pae = None
        self.mce = None
        self.cx8 = None
        self.apic = None
        self.sep = None
        self.mtrr = None
        self.pge = None
        self.mca = None
        self.cmov = None
        self.pat = None
        self.pse36 = None
        self.clflush = None
        self.dts = None
        self.acpi = None
        self.mmx = None
        self.fxsr = None
        self.sse = None
        self.sse2 = None
        self.ss = None
        self.ht = None
        self.tm = None
        self.pbe = None
        self.syscall = None
        self.nx = None
        self.rdtscp = None
        self.constant_tsc = None
        self.arch_perfmon = None
        self.pebs = None
        self.bts = None
        self.rep_good = None
        self.nopl = None
        self.xtopology = None
        self.nonstop_tsc = None
        self.cpuid = None
        self.aperfmperf = None
        self.pni = None
        self.dtes64 = None
        self.monitor = None
        self.ds_cpl = None
        self.vmx = None
        self.est = None
        self.tm2 = None
        self.ssse3 = None
        self.cx16 = None
        self.xtpr = None
        self.pdcm = None
        self.pcid = None
        self.sse4_1 = None
        self.sse4_2 = None
        self.popcnt = None
        self.lahf_lm = None
        self.pti = None
        self.ssbd = None
        self.ibrs = None
        self.ibpb = None
        self.stibp = None
        self.tpr_shadow = None
        self.vnmi = None
        self.flexpriority = None
        self.ept = None
        self.vpid = None
        self.dtherm = None
        self.ida = None
        self.arat = None
        self.flush_l1d = None
        self.cpufreq = None

        for name, value in self.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                elif name == "x86-64":
                    self.__dict__["x86_64"] = value
                else:
                    self.__dict__[name] = value

    def getAttribute(self, name):
        if isinstance(name, str) and name in self:
            return self[name]
        return None

    def integrityCheck(self):
        errors = {}
        errorCount = 0
        for name, value in self.items():
            if value != self.__dict__[name]:
                errorCount += 1
                errors[name] = {
                    "value": value,
                    "__dict__ value": self.__dict__[name]
                }
        return errorCount, errors

    def list(self):
        print("\nCPU_Capabilities:")
        for name, value in self.__dict__.items():
            print("\t" + name + ":\t" + str(value))


class Configuration( OrderedDict ):

    def __init__(self, configuration: dict):
        OrderedDict.__init__(self, configuration)


class Children( list ):

    def __init__(self, children: list):
        self.children = children
        if children == None:
            list.__init__(self)
            return
        list.__init__(self, children)
        for object in self.children:
            if 'id' in object:
                idParts = object['id'].split(':')
                if 'configuration' in object:
                    configuration = Configuration(object['configuration'])
                else:
                    configuration = None
                if 'capabilities' in object:
                    if System.idMap[idParts[0]] == HardwareId.CPU:
                        capabilities = CPU_Capabilities(object['capabilities'])
                    else:
                        capabilities = Capabilities(object['capabilities'])
                else:
                    capabilities = None
                if 'children' in object:
                    children = object['children']
                else:
                    children = None

                if System.idMap[idParts[0]] == HardwareId.Core:
                    self.append(Core(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Firmware:
                    self.append(Firmware(object, configuration, capabilities, children))

                elif System.idMap[idParts[0]] == HardwareId.CPU:
                    self.append(CPU(object, configuration, capabilities, children))

                elif System.idMap[idParts[0]] == HardwareId.Cache:
                    self.append(Cache(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Memory:
                    self.append(Memory(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Bank:
                    self.append(Bank(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.PCI:
                    self.append(PCI(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Display:
                    self.append(Display(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Communication:
                    self.append(Communication(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.USB:
                    self.append(USB(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.UsbHost:
                    self.append(USBhost(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.MultiMedia:
                    self.append(Multimedia(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Generic:
                    self.append(Generic(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.FireWire:
                    self.append(Firmware(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Network:
                    self.append(Network(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.ISA:
                    self.append(ISA(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Storage:
                    self.append(Storage(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.SCSI:
                    self.append(SCSI(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Disk:
                    self.append(Disk(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Volume:
                    self.append(Volume(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.LogicalVolume:
                    self.append(LogicalVolume(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.CD_ROM:
                    self.append(CD_ROM(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Medium:
                    self.append(Medium(object, configuration, capabilities, children))
                elif System.idMap[idParts[0]] == HardwareId.Battery:
                    self.append(Battery(object, configuration, capabilities, children))


class System:

    idMap = {}
    idMap['core']      = HardwareId.Core
    idMap['firmware']      = HardwareId.Firmware
    idMap['cpu']      = HardwareId.CPU
    idMap['cache']      = HardwareId.Cache
    idMap['memory']      = HardwareId.Memory
    idMap['bank']      = HardwareId.Bank
    idMap['pci']      = HardwareId.PCI
    idMap['display']      = HardwareId.Display
    idMap['communication']      = HardwareId.Communication
    idMap['usb']      = HardwareId.USB
    idMap['usbhost']      = HardwareId.UsbHost
    idMap['multimedia']      = HardwareId.MultiMedia
    idMap['generic']      = HardwareId.Generic
    idMap['firewire']      = HardwareId.FireWire
    idMap['network']      = HardwareId.Network
    idMap['isa']      = HardwareId.ISA
    idMap['storage']      = HardwareId.Storage
    idMap['scsi']      = HardwareId.SCSI
    idMap['disk']      = HardwareId.Disk
    idMap['volume']      = HardwareId.Volume
    idMap['logicalvolume']      = HardwareId.LogicalVolume
    idMap['cdrom']      = HardwareId.CD_ROM
    idMap['medium']      = HardwareId.Medium
    idMap['battery']    = HardwareId.Battery

    def __init__(self, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.checkArguments(configuration, capabilities, children)
        self.configuration = configuration
        self.capabilities = capabilities
        self.children = children

    @staticmethod
    def checkArguments( configuration: Configuration, capabilities: Capabilities, children: Children):
        if configuration is not None and not isinstance(configuration, Configuration):
            raise Exception("System.checkArguments - Invalid configuration argument:  " + str(configuration))
        if capabilities is not None and not isinstance(capabilities, Capabilities):
            raise Exception("System.checkArguments - Invalid capabilities argument:  " + str(capabilities))
        if children is not None and not isinstance(children, Children):
            raise Exception("System.checkArguments - Invalid children argument:  " + str(children))
        return True

    #   This needs careful testing
    def integrityCheck(self):
        errors = {}
        errorCount = 0
        if "attributes" in self.__dict__:
            for name, value in self.__dict__['attributes'].items():
                if name != "children" and name != "logicalname":    #   lists, can't compare with '='
                    if name == "class":
                        name = "class_"
                    if value != self.__dict__[name]:
                        errorCount += 1
                        errors[name] = {
                            "value": value,
                            "__dict__ value": self.__dict__[name]
                        }
        return errorCount, errors


class Computer( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, children)
        #   This attribute set is based on a single run of lshw under sudo.
        #   I am not assuming that the information in it is complete or that the same set of the available
        #   attributes is returned every time.
        #   Make sure the apparent attributes exist in the argument before assigning value:
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.clained = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.serial = None
        self.width = None
        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nComputer constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)


    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tComputer:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Core( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.version = None
        self.serial = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nCore constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCPU:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Firmware( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.description = None
        self.vendor = None
        self.physid = None
        self.version = None
        self.date = None
        self.units = None
        self.size = None
        self.capacity = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nFirmware constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCPU:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class CPU( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.slot = None
        self.units = None
        self.size = None
        self.capacity = None
        self.width = None
        self.clock = None
        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nCPU constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCPU:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Cache( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.physid = None
        self.slot = None
        self.units = None
        self.size = None
        self.capacity = None
        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nCache constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))



class Bank(System):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.serial = None
        self.slot = None
        self.units = None
        self.size = None
        self.width = None
        self.clock = None
        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nBank constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class PCI( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nPCI constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Display( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))

        #   QUICK TEST:
        #   "description" : "VGA compatible controller"
        #   if "description" in attributes:
        #       print("Display description:\t" + attributes['description'], file=stderr)

        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nDisplay constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Communication( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nCommunication constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Network( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.logicalname = None
        self.version = None
        self.serial = None
        self.units = None
        self.capacity = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nNetwork constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class USB( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))

        #   QUICK TEXT:
        #   "product"
        #   if "product" in attributes:
        #       print("USB product:\t" + attributes["product"], file=stderr)

        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nUSB constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class USBhost( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.logicalname = None
        self.version = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nUSBhost constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Multimedia( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nMultimedia constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Generic( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nGeneric constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class FireWire( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nFireWiree constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Bridge( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nBridge:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class ISA( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nISA constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Memory( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.physid = None
        self.slot = None
        self.units = None
        self.size = None
        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nMemory constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Storage( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.version = None
        self.width = None
        self.clock = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nStorage constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class SCSI( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.physid = None
        self.logicalname = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nSCSIe constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Disk( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.logicalname = None
        self.dev = None
        self.version = None
        self.serial = None
        self.units = None
        self.size = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nDisk constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Volume( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.description = None
        self.physid = None
        self.businfo = None
        self.logicalname = None
        self.dev = None
        self.version = None
        self.serial = None
        self.size = None
        self.capacity = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nVolume constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class LogicalVolume( Volume, System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.description = None
        self.vendor = None
        self.physid = None
        self.logicalname = None
        self.dev = None
        self.version = None
        self.serial = None
        self.size = None
        self.capacity = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nLogicalVolume constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class CD_ROM( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.description = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.businfo = None
        self.logicalname = None
        self.dev = None
        self.version = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nCD_ROM constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Medium( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.physid = None
        self.logicalname = None
        self.dev = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nMedium constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Battery( System ):

    def __init__(self, attributes: dict, configuration: Configuration, capabilities: Capabilities, children: Children):
        System.__init__(self, configuration, capabilities, Children(children))
        self.attributes = deepcopy(attributes)
        self.id = None
        self.class_ = None
        self.claimed = None
        self.handle = None
        self.product = None
        self.vendor = None
        self.physid = None
        self.slot = None
        self.units = None
        self.capacity = None

        for name, value in self.attributes.items():
            if not isinstance(value, list) and not isinstance(value, tuple) and not isinstance(value, dict):
                if name == "class":
                    self.__dict__["class_"] = value
                else:
                    self.__dict__[name] = value

        self.errorCount, self.errors = self.integrityCheck()
        if self.errorCount > 0:
            print("\nBattery constructor errors found:", file=stderr)
            print("\tcount:\t" + str(self.errorCount), file=stderr)
            print("\terrors:", file=stderr)
            for name, value in self.errors.items():
                print("\t\t" + name + ":\t" + str(value), file=stderr)

    def getAttributes(self):
        return self.attributes

    def getAttribute(self, name: str):
        """
        Get the value of one of the attributes in the output.
        :param name: name of the attribute as listed in the lshw output.
        :return: The value of the attribute if the name is present in this object, None otherwise.
        """
        if isinstance(name, str) and name in self.attributes:
            return self.attributes[name]
        return None

    def list(self):
        print("Attributes of object of class:\tCache:")
        for key, value in self.__dict__.items():
            print("\t" + key + ":\t" + str(value))


class Dispatcher:

    def __init__(self):
        print("Lshw.Dispatcher does not instantiate")

    @staticmethod
    def generateJshwJsonFile():
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


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("800x500+100+50")
    mainView.title(PROGRAM_TITLE)

    LSHW_JSON_FILE = 'lshw.json'
    jsonText = None

    if isfile(LSHW_JSON_FILE):
        prompt = "lshw json storage file already exists.  Would you like to update it? (y/Y or n/N)"
        print(prompt, end=":\t")
        response = input()
        if response in ('y','Y'):
            jsonText = Dispatcher.generateJshwJsonFile()
        else:
            lshwJsonFile = open(LSHW_JSON_FILE, "r")
            jsonText = lshwJsonFile.read()
            lshwJsonFile.close()
    else:
        jsonText = Dispatcher.generateJshwJsonFile()

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
        computer = Computer(loads(jsonText), Configuration(configuration), Capabilities(capabilities),
                            Children(children))
        print("lshw API is available as \"computer\"")

        prompt = "Would you line to see the lshw output in a GUI Tree window? (y/Y or n/N)"
        print(prompt, end=":\t")
        response = input()
        if response in ('y', 'Y'):
            print('Generating view')
            lshwJson = loads(jsonText)
            jsonTreeView    = JsonTreeView( mainView, lshwJson, {"openBranches": True, "mode": "strict"})
            jsonTreeView.pack(expand=True, fill=BOTH)
            mainView.mainloop()
