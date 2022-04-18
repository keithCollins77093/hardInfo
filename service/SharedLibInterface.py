#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         view/Help.py
#   Date Started:   March 21, 2022
#   Purpose:        Fully leverage the forensic capabilities built into linux making user configuration of
#                   shared library functions possible.
#                   In this application, a Tool is defined as a linux command or function for which
#                   particular arguments have been defined.
#                   With programmatic control, the arguments do not need to be constants, as would be
#                   the case if the textual command line arguments were simply recorded for each
#                   user variation on use of a command, but can also be variables set at runtime.
#                   The linux command 'locate [libname].h' can be used to find the library's header,
#                   which can be used as its manifest.
#
#   Development:
#       Argument Data Type Conversion Issue:
#           Authority:  Ankur Kumar Sharma
#                       Extending Python via Shared Libraries
#                       May 1, 2010
#                       OpenSource: www.opensourceforu.com/2010/05/extending-python-via-shared-libraries/?amp
#           Native Python types that can be directly passed to C standard library functions:
#               None, int, long, byte string, Unicode string.
#           Other types will generally crash the called function.
#           Construction of data objects is required for other types.
#           The Python ctypes module, ctypes, provides the following types for this purpose:
#               c_char, c_wchar, c_byte, c_short, c_ushort, c_int, c_uint, c_long, c_ulong,
#               c_float, c_double, etc. ...
#           As well as typed pointers:
#               c_char_p, c_wchar_p, c_void_p.
#           Instantiation form:     hw = c_char_p("Hello World").
#           hw can then be passed in to the c function.
#
#           Current Path on My Development Machine: (where the shared library must be located to use it using ctypes)
#               /home/keithcollins/.cargo/bin:
#               /home/keithcollins/.local/bin:
#               /usr/local/sbin:
#               /usr/local/bin:
#               /usr/sbin:
#               /usr/bin:
#               /sbin:/bin:
#               /usr/games:
#               /usr/local/games:
#               /snap/bin:
#               /usr/share/javadb/bin/:
#               /home/keithcollins/Java/JavaFX/openjfx-17.0.2_linux-x64_bin-sdk/javafx-sdk-17.0.2/lib
#
#           ldconfig -v produces a listing of shared object files (*.so) curently available.
#           I put an example in documentation/ldconfig.-v.output.2022-03-25.txt.
#
#       2022-03-26
#           Name of project at GitHub and PyPI: PyShare or pyshare.
#           Newly found (Last Night, late) Linux share library information gathering commands:
#               nm, ar, readelf.
#           nm:
#               Use locate to find the full path of the libraries listed by ldconfig -v.
#               Next: use the file [filePath] command to determine whether the file is in fact an ELF file.
#                   If the file command reports that the file is a symbolic link, follow the link, it
#                   may be the other file, with more specific version information in the name, in the pair
#                   returned by ldconfig -v.
#                   Parse the output of file [filePath] and store.
#               When nm reports "no symbols", use nm --dynamic and  nm --dynamic --with-symbol-versions
#           readelf:
#               To output top-level header information in ELF file:
#                   readelf -h [filePath]
#                   split ech line on ':' to get name:value pair of fields in header.
#               For sections of the process address space:
#                   readelf -S [filePath]
#               For symbols table:
#                   readelf -s [filePath]
#           Sample ouput:   consoleOutput/readelf/readelf.--all.output.2022-03-26.txt
#               command:    readelf --all /lib/x86_64-linux-gnu/libnss_myhostname.so.2 > readelf.--all.output.2022-03-26.txt
#
#           Command Identifiers:
#               For the raw output of each DLL information gathering command the database needs an identifier
#               for the command used and the subcommand argument or arguments used to gather the information.
#               This is a data source identifier, much like an URL is a data source identifier.
#               It should be structured hierarchically, with dot separated identifiers for each more
#               particular specifier, even if the sequence isn't representative of a perfectly hierarchical
#               tree structure.
#               Examples:
#                   ldconfig.-v
#                   readelf.--symbols.--string-dump
#                   ar.-v
#
#           nm: SEE ALSO:
#               ar, objdump, ranlib, and the Info entries for binutils.
#
#       2022-03-27: Use
#           To determine which linux commands and programs are dependent on which *.so dll dynamically loadable
#           libraries, usable in Python, use the Linux 'ldd' command with the program name as the argument.
#           ldd man page states:
#               "ldd  prints  the shared objects (shared libraries) required by each program or shared object
#               specified on the command line."
#           This tells tye Python programmer using the ctypes standard library module to interface with C, C++,
#           and Rust libraries (Crates), which libraries are used to implement the subject commands or other
#           (possibly static and therefore not usable with ctypes) libraries.
#           If all of the *.so DLLs in Linux were rewritten in carefully, securely coded Rust, and then the
#           software dependent on them rewritten in Python, Linux would be a much more secure operating system.
#           It would also be much easier to customize and build applications on.
#           The Linux 'dpkg-query' (can use the -l argument) command can be used to list installed packages,
#           including the programs themselves, that 'ldd' can be used to examine the dependencies of.
#           The only problem left is knowing the file system path to the executable file.
#           For command line executables, they need to be on the PATH.  echo $PATH.
#           The dpkg available packages database is at: /var/lib/dpkg/available, which is a read only text file.
#           According to the man page:
#               "Users of APT-based frontends should use apt-cache show package-name instead."
#           COmmon user program location:   /usr/bin
#           Caveat:
#               Output of:  ldd /usr/sbin/gparted
#                       is:	    not a dynamic executable
#               However, 'ar' will show the list of all of the statically linked archive (*.a) files in the
#               non dynamic libraries gparted depends on.
#               'ranlib' generates an index to an archive.
#
#           Rust:   The security of immutability and the lazieness of C and C++ prgorammers:
#               To C and C++ programmers living in their happy frolicking land:
#                   Read through a 1000-5000 line C program written by you and count al lof the variables that
#                   never actually change value once assigned.  You will usually find these in the deeper
#                   nesting levels.  They frequently require only one value for a variable once assigned for
#                   very specific and specialized tasks.
#
#       2022-03-37: Linux hypocrisy or fraud in security implementation:
#                       (From comment online found doing security research a few years ago.)
#           Example:    A read-only file, owned and controlled by the root user, which all of the configuration
#                       files and many other system information files are, can be loaded into a text editor
#                       or read using a Linux command, thereby producing a writable copy in memory.  With
#                       your text editor, select all and copy, using ctrl-c if there is no menu option in the
#                       standard Edit menu bar drop down menu.  Write the copy to a file which you own.
#                       You can now edit it and make as many copies as you like.  Without root access,
#                       the only use you are prevent from doing is writing it back to the original physical file.
#                       Malware of any kind can read all of the configuration files, along with many other
#                       critical system information files, and can execute access commands which so not require
#                       sudo or root privileges to run, obtaining the output of them.
#                       NO ROOT KIT IS REQUIRED FOR MALWARE TO FULLY EXPLORE YOUR COMPUTER.
#                       The malware is also free to 'exfiltrate' the information obtained in inconspicuous
#                       chunks over networks, including the ubiquitous Internet.
#                       The Windows security model also allows this violation of read-only protection.
#
#           This is criminally deliberate design, but none of the state governments and no branch of the
#           federal government, that I know of, has investigated it, attempted to prosecute it, or tried
#           to make a law requiring better security.
#           YOU ARE NAKED AND UNDER A MICROSCOPE FACILITATED BY YOUR GOVERNMENTS.
#

import bz2
import ctypes
from os import remove
from sys import stderr
import sqlite3
from ctypes.util import find_library
from ctypes import cdll, c_char_p
from ctypes import CDLL
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
from os.path import isfile, isdir
from collections import OrderedDict
from json import dumps, loads
from enum import Enum

import simplejson

from tkinter import Tk, LabelFrame, Listbox, messagebox, \
                        RAISED, GROOVE, SINGLE, BOTH, END

from model.Installation import INSTALLATION_FOLDER, DATA_FOLDER

PROGRAM_TITLE = "Linux Shared Library Interface"

DLL_MAP_FILE    = INSTALLATION_FOLDER + 'consoleOutput/ldconfig/ldconfig.json'
DLL_TEXT_FILE   = INSTALLATION_FOLDER + 'consoleOutput/ldconfig/ldconfig.txt'
#   Including time stamps in the output file names can be included in an upgrade:
#   DLL_MAP_FILE    = INSTALLATION_FOLDER + 'consoleOutput/ldconfig/ldconfig.-v.2022-03-26.output.json'
#   DLL_TEXT_FILE   = INSTALLATION_FOLDER + 'consoleOutput/ldconfig/ldconfig.-v.2022-03-26.output.txt'

NM_VERB_JSON_FILE_NAME = 'nm.verbose.json'
NM_VERB_SC_JSON_FILE_NAME = 'nm.verbose.sc.json'

DLL_DB_FILE     = DATA_FOLDER + 'dll.db'
TABLE_NAME_FOLDERS  = 'Folders'
TABLE_NAME_FILES    = 'Files'
TABLE_NAME_SYMBOLS  = 'Symbols'

LINE_LEN        = 100


class ELF_Section(Enum):
    FILE_HEADER         = 'file-header'
    SEGMENTS            = 'segments'
    SECTION_HEADERS     = 'section-headers'
    SECTION_GROUPS      = 'section-groups'
    SECTION_DETAILS     = 'section-details'
    SYMBOLS             = 'symbols'
    DYN_SYMS            = 'dyn-syms'
    HEADERS             = 'headers'
    NOTES               = 'notes'
    RELOCS              = 'relocs'
    UNWIND              = 'unwind'
    DYNAMIC             = 'dynamic'
    VERSION_INFO        = 'version-info'
    ARCH_SPECIFIC       = 'arch-specific'

    def __str__(self):
        return self.value


class ReadElfModifier(Enum):
    USE_DYNAMIC         = 'use-dynamic'
    HEX_DUMP            = 'hex-dump'
    RELOCATED_DUMP      = 'relocated-dump'
    STRING_DUMP         = 'string-dump'
    DECOMPRESS          = 'decompress'
    ARCHIVE_INDEX       = 'archive-index'
    HISTOGRAM           = 'histogram'
    WIDE                = 'wide'

    def __str__(self):
        return self.value


class ReadELFOther(Enum):
    VERSION     = 'version'
    HELP        = 'help'
    COPYRIGHT   = 'Copyright'

    def __str__(self):
        return self.value


class LinuxDLLHelp:

    #   This was copied directly from the readelf command man page on 2022-03-26
    READ_ELF_HELP = {
        #   Sections:
        'file-header': 'Displays the information contained in the ELF header at the start of the file',
        'segments': 'Displays the information contained in the file\'s segment headers, if it has any',
        'section-headers': 'Displays the information contained in the file\'s section headers, if it has any',
        'section-groups': 'Displays the information contained in the file\'s section groups, if it has any',
        'section-details': 'Displays the detailed section information. Implies -S',
        'symbols': 'Displays the entries in symbol table section of the file, if it has one.  If a symbol has '
                   'version information associated with it then this is displayed as well.  The version string is '
                   'displayed as a suffix to the symbol name, preceeded by an @ character.  For example foo@VER_1.  '
                   'If the version is the default version to be used when resolving unversioned references to '
                   'the symbol then it is displayed as a suffix preceeded by two @ characters.  For example foo@@VER_2.',
        'dyn-syms': 'Displays the entries in dynamic symbol table section of the file, if it has one.  The output '
                    'format is the same as the format used by the --syms option.',
        'headers': 'Display all the headers in the file.  Equivalent to -h -l -S.',
        'notes': 'Displays the contents of the NOTE segments and/or sections, if any.',
        'relocs': 'Displays the contents of the file\'s relocation section, if it has one.',
        'unwind': 'Displays the contents of the file\'s unwind section, if it has one.  Only the unwind sections '
                  'for IA64 ELF files, as well as ARM unwind tables (".ARM.exidx" / ".ARM.extab") are currently '
                  'supported.',
        'dynamic': 'Displays the contents of the file\'s dynamic section, if it has one.',
        'version-info': 'Displays the contents of the version sections in the file, it they exist.',
        'arch-specific': 'Displays architecture-specific information in the file, if there is any.',

        #   Modifiers:
        'use-dynamic': 'When displaying symbols, this option makes readelf use the symbol hash tables in the '
                       'file\'s dynamic section, rather than the symbol table sections.\nWhen displaying relocations, '
                       'this option makes readelf display the dynamic relocations rather than the static relocations.',
        'hex-dump': 'Displays the contents of the indicated section as a hexadecimal bytes.  A number identifies '
                    'a particular section by index in the section table; any other string identifies all sections '
                    'with that name in the object file.',
        'relocated-dump': 'Displays the contents of the indicated section as a hexadecimal bytes.  A number '
                          'identifies a particular section by index in the section table; any other string '
                          'identifies all sections with that name in the object file.  The contents of the section '
                          'will be relocated before they are displayed.',
        'string-dump': 'Displays the contents of the indicated section as printable strings.  A number identifies '
                       'a particular section by index in the section table; any other string identifies all '
                       'sections with that name in the object file.',
        'decompress': 'Requests that the section(s) being dumped by x, R or p options are decompressed before '
                      'being displayed.  If the section(s) are not compressed then they are displayed as is.',
        'archive-index': 'Displays the file symbol index information contained in the header part of binary '
                         'archives.  Performs the same function as the t command to ar, but without using '
                         'the BFD library.',
        #   skipped debug-dump and its options
        'histogram': 'Display a histogram of bucket list lengths when displaying the contents of the symbol tables.',

        'wide': ' Don\'t break output lines to fit into 80 columns. By default readelf breaks section header '
                'and segment listing lines for 64-bit ELF files, so that they fit into 80 columns. This option '
                'causes readelf to print each section header resp. each segment one a single line, which is far '
                'more readable on terminals wider than 80 columns.',

        #   Other:
        'version': 'Display the version number of readelf.',
        'help': 'Display the command line options understood by readelf.',
        'Copyright': 'man page:\tFree Software Foundation\n'
                     'Permission is granted to copy, distribute and/or modify this document under the terms of the '
                     'GNU Free Documentation License, Version 1.3 or any later version published by the Free '
                     'Software Foundation; with no Invariant Sections, with no Front-Cover Texts, and with no '
                     'Back-Cover Texts.  A copy of the license is included in the section entitled "GNU Free '
                     'Documentation License".'
    }

    def __init__(self):
        pass

    @staticmethod
    def __textOut(text: str):
        idx = 0
        col = 0
        while idx < len(text):
            print(text[idx:idx + 1], end='')
            idx += 1
            col += 1
            if col % LINE_LEN == 0:
                while idx < len(text) and not text[idx:idx + 1].isspace():
                    print(text[idx:idx + 1], end='')
                    idx += 1
                if idx < len(text):
                    print(text[idx:idx + 1], end='')
                    idx += 1
                print('\n', end='')
                col = 0

    @staticmethod
    def printHelp(section: ELF_Section=None, modifier: ReadElfModifier=None, other: ReadELFOther=None):
        #   Using TTY mode for finding position for line breaks
        if section is not None:
            print("\nELF Section:\t" + section.value)
            LinuxDLLHelp.__textOut(LinuxDLLHelp.READ_ELF_HELP[section.value])
            print()
        if modifier is not None:
            print("\nreadelf Output Modifier:\t" + modifier.value)
            LinuxDLLHelp.__textOut(LinuxDLLHelp.READ_ELF_HELP[modifier.value])
            print()
        if other is not None:
            print("\nreadelf Output Other:\t" + other.value)
            LinuxDLLHelp.__textOut(LinuxDLLHelp.READ_ELF_HELP[other.value])
            print()

    @staticmethod
    def runMan(softwareName: str = None, toStdOut: bool=False, verbose: bool=False, debug: bool=False):
        if not isinstance(softwareName, str):
            return ()
        argv = ['man', softwareName]
        sub = Popen(argv, stdout=PIPE, stderr=STDOUT)
        lastCommandRunTime = str(datetime.now())
        output, error_message = sub.communicate()
        outputLines = tuple(output.decode('utf-8').split('\n'))
        return outputLines

    @staticmethod
    def buildDllManMap(verbose: bool=False, debug: bool=False):
        """
        Use output of ldconfig -v, which is a list of dll library names as keys to the list of files which
        implement different releases of the library names.  Run 'man' on each and look for the phrase
        "No manual entry ..." on the first 2 or so lines.
        To explore, look for it in all lines and print the largest line number that it occurs on.
        :return:
        """
        dllMap = None
        dllHelpMap = OrderedDict()
        if isfile(DLL_MAP_FILE):
            file = open(DLL_MAP_FILE, "r")
            dllMapText = file.read()
            file.close()
            dllMap = loads(dllMapText)
        elif isfile(DLL_TEXT_FILE):
            dllMap = LinuxCommands.ldconfig(textToMap=True)
        dllManPageCount = 0
        for folderPath, dllNameList in dllMap.items():
            for dllName in dllNameList:
                helpLines = LinuxDLLHelp.runMan(dllName)
                found = True
                for line in helpLines[:3]:
                    if "No manual entry" in line:
                        found = False
                if found:
                    dllManPageCount += 1
                    if verbose or debug:
                        print("Found a man page for:\t" + dllName)
                    dllHelpMap[dllName] = helpLines     #   This is a tuple for security.
        if verbose or debug:
            print("\tTotal number of dll man pages found:\t" + str(dllManPageCount))
        return dllHelpMap


class LinuxCommands:

    def __init__(self):
        pass

    @staticmethod
    def nm(name: str=None, filePath: str=None, folderMap: OrderedDict=None, all: bool=True, save: tuple=None,
           read: str=None, verbosePrint: bool=False, debug: bool=False):

        def processFile(fileName):
            filePath = pathName + '/' + fileName
            if debug:
                print('\n' + filePath)
            argv = ['nm', '--format=posix', '--dynamic', '--debug-syms', '--portability', '--radix=d', '--synthetic',
                    '--with-symbol-versions', filePath]
            sub = Popen(argv, stdout=PIPE, stderr=STDOUT)
            lastCommandRunTime = str(datetime.now())
            output, error_message = sub.communicate()
            outputLines = output.decode('utf-8').split('\n')
            nmMap[filePath] = outputLines

            if "no symbols" not in outputLines[0]:
                #   print()
                if verbosePrint or debug:
                    print(str(fileIdx) + " of " + str(fileCount) + ":\tCollecting symbol names in:\t" + filePath)
                    if debug:
                        for line in outputLines:
                            print("\t" + line)
                symbolCounts[filePath] = len(outputLines)

        def parseSymbolDef(symbolDef: str):
            """
            Samples:
                "acl_get_fd T 0000000000033392 0000000000000022@@Base",
                "acl_get_file T 0000000000033424 0000000000000022@@Base",
                "acl_set_fd T 0000000000033456 0000000000000025@@Base",
                "acl_set_file T 0000000000033488 0000000000000025@@Base",
                "__bss_start B 0000000002148276 @@Base",
                "capset T 0000000000031280 0000000000000037@@Base",
                "chmod T 0000000000026432 0000000000000210@@Base",
                "chown T 0000000000025632 0000000000000185@@Base",
                "close T 0000000000028608 0000000000000101@@Base",
                "comm_sd D 0000000002148272 0000000000000004@@Base",
                "connect U         @GLIBC_2.2.5",
                "connect@plt T 0000000000019904 ",

            :param symbolDef:
            :return:
            """
            map = {}
            if isinstance(symbolDef, str) and len(symbolDef) > 0:
                parts = symbolDef.strip().split()
                map['name']     = parts[0]
                map['type']     = parts[1]
                map['value']    = ' '.join(parts[2:])
            return map

        def readFromFile():
            nmMap = None
            if isfile(NM_VERB_JSON_FILE_NAME):
                file = open(NM_VERB_JSON_FILE_NAME, "r")
                nmMap = loads(file.read())
                file.close()
            symbolCounts = None
            if isfile(NM_VERB_SC_JSON_FILE_NAME):
                file = open(NM_VERB_SC_JSON_FILE_NAME, "r")
                symbolCounts = loads(file.read())
                file.close()
            return nmMap, symbolCounts

        def constructDllDB(installing: bool=False):
            if installing:
                if not isdir(DATA_FOLDER):
                    #   Construct the data folder path for the installation.
                    #   User should be able to configure this.
                    pass
                if isfile(DLL_DB_FILE):
                    remove(DLL_DB_FILE)
                connection = None
                try:
                    connection = sqlite3.connect(DLL_DB_FILE)
                except Exception as err:
                    print(err, file=stderr)
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("""CREATE TABLE `Folders` 
                                ( `RowId` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `folderPath` TEXT )""")
                    cursor.execute("""CREATE TABLE "Files" 
                                    ( `RowId` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
                                    `folderId` INTEGER NOT NULL, 
                                    `fileName` TEXT NOT NULL, 
                                    FOREIGN KEY(`folderId`) REFERENCES `Folders`(`RowId`) )""")
                    cursor.execute("""CREATE TABLE "Symbols" 
                                    ( `RowId` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
                                    `fileId` INTEGER NOT NULL, 
                                    `name` TEXT NOT NULL, 
                                    `type` TEXT NOT NULL, 
                                    `value` TEXT NOT NULL, 
                                    FOREIGN KEY(`fileId`) REFERENCES `Files`(`RowId`) )""")
                    connection.commit()
                    cursor.close()
                    connection.close()

        def fileToDBTable(verbose: bool=False, debug: bool=False, destructive: bool=False):
            print("Copying dll symbol information from json file to database:\t" + DLL_DB_FILE)
            print("All current content of the tables written to will be deleted")
            print("Proceed? (y/n)")
            response = input()
            if not response.lower() in ('y', 'yes'):
                print("Aborting dll.db table overwrite", file=stderr)
                return False

            nmMap, symbolCounts = readFromFile()
            connection = None
            cursor = None
            if debug:
                print("Deleting all rows from dll.db tables: Symbols, File, and Folders")
            if destructive:
                constructDllDB(installing=True)
                connection = sqlite3.connect(DLL_DB_FILE)
                cursor = connection.cursor()
            else:
                connection = sqlite3.connect(DLL_DB_FILE)
                cursor = connection.cursor()
                #   The DB tables recording the nm generated symbol information are completely rewritten each time the
                #   storage text file contents are copied to them.
                #   WARNING:    This takes a LONG time for the symbol table since every record is marked as deleted.
                #               This also leaves all deleted records in the database making it very LARGE.
                #               However, destroying and rebuilding the database to remove the storage bloat
                #               might delete important history information.
                cursor.execute("DELETE FROM {tableName}".format(tableName="Symbols"))
                cursor.execute("DELETE FROM {tableName}".format(tableName="Files"))
                cursor.execute("DELETE FROM {tableName}".format(tableName="Folders"))
                connection.commit()

            currentFolderPath = None
            fileCount = 0
            folderRowId = 0
            if verbose or debug:
                print("Count of *.so dll files:\t" + str(len(nmMap)))
            for filePath, symbolList in nmMap.items():
                fileCount += 1
                if verbose or debug:
                    print(str(fileCount) + ":\tCopying symbol information in file:\t" + filePath)
                filePathParts = filePath.strip().split('/')
                fileName = filePathParts[len(filePathParts)-1]
                del(filePathParts[len(filePathParts)-1])
                folderPath = '/'.join(filePathParts)
                if currentFolderPath != folderPath:     #   new folder to table
                    if verbose or debug:
                        print("")
                    cursor.execute('''INSERT INTO Folders(folderPath) VALUES(?)''', (folderPath,))
                    cursor.execute('''SELECT RowId From Folders WHERE folderPath="{folderPath}"'''.format(folderPath=folderPath))
                    folderRowId = cursor.fetchone()[0]
                    currentFolderPath = folderPath
                cursor.execute('''INSERT INTO Files(folderId, fileName) VALUES(?, ?)''', (folderRowId, fileName))
                cursor.execute('''SELECT RowId From Files WHERE fileName="{fileName}"'''.format(fileName=fileName))
                fileRowId = cursor.fetchone()[0]
                connection.commit()
                for symbolText in symbolList:
                    if symbolText != '':
                        symbolDef = parseSymbolDef(symbolText)
                        cursor.execute('''INSERT INTO Symbols(fileId, name, type, value) VALUES(?, ?, ?, ?)''',
                                       (fileRowId, symbolDef['name'], symbolDef['type'], symbolDef['value']))
            connection.commit()
            cursor.close()
            connection.close()
            return True

        if read is not None:
            if read == 'file':
               return readFromFile()
            elif read == 'db':
                pass
        if save is not None and save[0] == "fileToDB":
            return fileToDBTable(verbose=True, debug=True, destructive=True)

        nmMap   = OrderedDict()
        symbolCounts = OrderedDict()
        fileCount = 0
        if verbosePrint or debug:
            for folder, files in folderMap.items():
                fileCount += len(files)
            print("DLL Count:\t" + str(fileCount))
        fileIdx = 0
        if all and isinstance(folderMap, OrderedDict):
            for pathName in folderMap:
                for libName, fileNames in folderMap[pathName].items():
                    fileIdx += 1
                    processFile(fileNames[0])
                    if fileNames[0] != fileNames[1]:
                        processFile(fileNames[1])

        if verbosePrint or debug:
            totalSymbols = 0
            for filePath, symbolCount in symbolCounts.items():
                totalSymbols += symbolCount
            print("\n\tTotal Symbols Found:\t" + str(totalSymbols))

        if save is not None and "file" in save:
            file = open(NM_VERB_JSON_FILE_NAME, "w")
            file.write(dumps(nmMap, indent=4))
            file.close()
            file = open(NM_VERB_SC_JSON_FILE_NAME, "w")
            file.write(dumps(symbolCounts, indent=4))
            file.close()
        if save is not None and "db" in save:
            for filePath, symbolList in nmMap.items():
                for symbolText in symbolList:
                    symbolDef = parseSymbolDef(symbolText)

        return nmMap, symbolCounts


    @staticmethod
    def readelf(*args):
        """
        Call readelf with the specified arguments using Popen() and return the results.
        :param args: This can contain at most one section identifier followed by at most one modifier.
        :return: The output text and the error text as a tuple.
        """
        pass

    @staticmethod
    def ldconfig(refreshStorage: bool=False, textAlso: bool=False, textToMap: bool=False,
                 verbose: bool=True, debug: bool=False):
        """
        This builds a library name -> files tuple map.
        Various options exist for adding each library's symbols, i.e. functions to the map.
        They can be scanned in here or added on a user-request basis.
        :return:
        """

        def runLdconfig():
            argv = ['ldconfig', '-v']
            sub = Popen(argv, stdout=PIPE, stderr=STDOUT)
            lastCommandRunTime = str(datetime.now())
            output, error_message = sub.communicate()
            outputLines = output.decode('utf-8').split('\n')
            return outputLines, output

        outputLines = ()
        output = ''
        if textToMap:
            if isfile(DLL_TEXT_FILE):
                outputLines, output = runLdconfig()
        else:
            if not refreshStorage and isfile(DLL_MAP_FILE):
                file = open(DLL_MAP_FILE, "r")
                mapText = file.read()
                file.close()
                #   This cold be immutable but Python provides no provision, other than named tuples.
                return OrderedDict(loads(mapText))

            outputLines, output = runLdconfig()
            if debug:
                print(outputLines)

        map = None
        folderMap   = OrderedDict()
        currentFolder = None

        inFolder = False
        #   Immutability for security:
        outputLines = tuple(outputLines)

        for line in outputLines:
            line = line.strip()
            if len(line) > 0:
                if not (isdir(line.strip()) or isdir(line.strip()[0:len(line)-1])):
                    if inFolder:
                        lineParts = line.strip().split()
                        if lineParts[1] == '->' and lineParts[0].startswith('lib') and '.so' in lineParts[0] and \
                                        lineParts[2].startswith('lib') and '.so' in lineParts[2]:

                            #   ['libnss_myhostname.so.2', '->', 'libnss_myhostname.so.2']
                            soPos = lineParts[0].index('.so')
                            libName = lineParts[0][3:soPos]
                            map[libName] = (lineParts[0], lineParts[2])
                            if debug:
                                print("\tLibrary files logged:\t" + str(map[libName]))
                else:   #   New folder found:
                    firstFolder = currentFolder == None
                    if map is not None and len(map) > 0 and not firstFolder:
                        folderMap[currentFolder] = map
                    if isdir(line.strip()):
                        currentFolder   = line.strip()
                    if verbose or debug:
                        print("Scanning folder:\t" + currentFolder)
                    elif isdir(line.strip()[0:len(line)-1]):
                        currentFolder = line.strip()[0:len(line)-1]
                    inFolder = True
                    map = OrderedDict()

        file    = open(DLL_MAP_FILE, "w")
        file.write(dumps(folderMap, indent=4))
        file.close()
        if textAlso:
            file = open(DLL_TEXT_FILE, "w")
            file.write(output.decode('utf-8'))
            file.close()
        return folderMap


class LibFunctions:
    """
    Instances of this class will provide a controlled subset of library services which are tailored to a
    particular application or system utility context.  The functional limitation accomplishes a minimal
    level of anti-viral security while forcing the developer to plan the application of the selected
     library or libraries before writing it.
    """

    def __init__(self):
        pass

    @staticmethod
    def miscellaneousTest():

        #   importing the C standard library:
        libc = CDLL('libc.so.6')
        libc.printf(c_char_p(b"Hello C from Python!\n"))

        #   From reference: The GNU C Library Reference Manual
        #                   Appendix B: Summary of Library Facilities
        #   Value:  Programming using the standard C library in Python.
        uid = libc.getuid()
        #   This returns a pointer to a null terminated string, need to translate:
        workingDirectory = libc.getcwd()

        #   Equivalent of Python's datetime.now():
        dateTime = datetime.fromtimestamp(libc.time(None))
        print("The time is:\t" + dateTime.ctime())

        regex = CDLL(find_library('gnunetregex'))
        parted = CDLL("libparted.so.2")

        absValue = libc.abs(-7)
        print("\nlibc.abs(-7):\t" + str(absValue))
        print()

        LibFunctions.listLibraryDocs("c", libc)
        LibFunctions.listLibraryDocs("gnunetregex", regex)
        LibFunctions.listLibraryDocs("parted", parted)

        #   Which is faster, the Linux bz2 library or the Python lib/bz2.py?
        #   This needs to be tested for hashing significant content and encryption as well.
        libbz2 = CDLL(find_library('bz2'))
        LibFunctions.listLibraryDocs("bz2", libbz2)

        mhash = CDLL(find_library('mhash'))
        LibFunctions.listLibraryDocs("mhash", mhash)

        mcrypt = CDLL(find_library('mcrypt'))
        LibFunctions.listLibraryDocs("mcrypt", mcrypt)

        #   Qt, the GUI engine is installed here:
        qt5opengl = CDLL(find_library('Qt5OpenGL'))
        LibFunctions.listLibraryDocs("Qt5OpenGL", qt5opengl)

        print("parted.__str__():\t" + parted.__str__())
        print("\nparted.__doc__:\n" + parted.__doc__)
        print("parted.__dict__:\t" + str(parted.__dict__))

    @staticmethod
    def listLibraryDocs(name: str, lib):
        print("listLibraryDocs\t" + name )
        print(name + ".__str__():\t" + lib.__str__())
        print("\n" + name + ".__doc__:\n" + str(lib.__doc__))
        print(name + ".__dict__:\t" + str(lib.__dict__))


class LibView(LabelFrame):

    def __init__(self, container, folderMap: OrderedDict, **keyWordArguments):

        LabelFrame.__init__(self, container, keyWordArguments)

        folderNames = list(folderMap.keys())
        libNames = []
        for folderName in folderNames:
            for libName in folderMap[folderName]:
                libNames.append(libName)
        libNames.sort()

        listViewLibraries = Listbox(self, border=4, relief=GROOVE, selectmode=SINGLE, height=35)

        listViewLibraries.insert(END, *libNames)
        listViewLibraries.bind('<<ListboxSelect>>', self.listItemSelected)
        listViewLibraries.bind('<Button-3>', self.listItemRightClick)
        listViewLibraries.bind('<Double-Button-1>', self.listItemDoubleClick)
        listViewLibraries.bind('<Key>', self.listItemKeyEvent)
        listViewLibraries.bind('<Enter>', self.listItemEvent)
        listViewLibraries.bind('<Leave>', self.listItemEvent)
        listViewLibraries.bind('<FocusIn>', self.listItemEvent)
        listViewLibraries.bind('<FocusOut>', self.listItemEvent)
        listViewLibraries.pack(expand=True, fill=BOTH)

    def listItemSelected(self, event):
        print("listItemSelected")

    def listItemRightClick(self, event):
        print("listItemRightClick")

    def listItemDoubleClick(self, event):
        print("listItemDoubleClick")

    def listItemKeyEvent(self, event):
        print("listItemKeyEvent")

    def listItemEvent(self, event):
        print("listItemEvent")


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        #   mainView.destroy()
        pass


if __name__ == '__main__':

    LinuxDLLHelp.buildDllManMap(verbose=True)
    #   LinuxDLLHelp.printHelp(section=ELF_Section.SYMBOLS, modifier=ReadElfModifier.STRING_DUMP, other=ReadELFOther.COPYRIGHT)
    #   folderMap = LinuxCommands.ldconfig(refreshStorage=True, textAlso=True)

    #   verbosePrint provides ongoing progress information

    #   To Generate Files and DB Tables:
    #   nmMap, symbolCounts   = LinuxCommands.nm(folderMap=folderMap, verbosePrint=True, save=('file', 'db'))

    #   To Generate DB Table from File:
    #   success   = LinuxCommands.nm(folderMap=folderMap, verbosePrint=True, save=('fileToDB', ))

    #   To read from existing files or db tables:
    #   nmMap, symbolCounts   = LinuxCommands.nm(folderMap=folderMap, verbosePrint=True, read=('file'))
    #   print(symbolCounts)

    """
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("400x600+100+50")
    mainView.title(PROGRAM_TITLE)

    #   memusage = cdll.LoadLibrary("libmemusage.so")
    #   print("memusage:\t" + str(memusage))
    memusage = CDLL("libmemusage.so")

    libListFrame = LibView(mainView, folderMap, text="Linux Shared Libraries", border=5, relief=RAISED)

    libListFrame.pack(expand=True, fill=BOTH)
    mainView.mainloop()
    """

    #   /lib/x86_64-linux-gnu/libnss_myhostname.so.2