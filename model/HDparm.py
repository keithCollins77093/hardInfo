"""
#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         model/HDparm.py
#   Date Started:   March 24, 2022
#   Purpose:        Store and provide API for Linux hdparm command.
#   Development:
#       run with:   sudo hdparm -aAbBcCdgHiIkmMNQurRW /dev/sda [or sda n]
#       and:        sudo hdparm -I /dev/sda [or sda n]
#
#       man hdparm:
#
#             When no options are given, -acdgkmur is assumed.  For "Get/set" options, a query without the
#             optional  parameter  (e.g.  -d)  will query (get) the device state, and with a parameter
#             (e.g., -d0) will set the device state.
#
#
#       [Security Hardening:]
#             --dco-freeze
#               DCO stands for Device Configuration Overlay, a way for vendors to selectively disable certain
#               features  of  a  drive.   The --dco-freeze option will freeze/lock the current drive configuration,
#               thereby preventing software (or malware) from changing any DCO settings until after the next
#               power-on reset.
#
#             --dco-identify
#               Query and dump information regarding drive configuration settings which can be disabled by
#               the  vendor  or  OEM  installer.  These settings show capabilities of the drive which might
#               be disabled by the vendor for "enhanced compatibility".  When disabled, they are otherwise
#               hidden and will not show in the -I identify output.  For example, system vendors sometimes
#               disable 48_bit  addressing  on  large  drives, for compatibility (and loss of capacity) with
#               a specific BIOS.  In such cases, --dco-identify will show that the drive is 48_bit capable,
#               but -I will not show it, and nor will the drive accept 48_bit commands.
#
#       [Linux Disk I/O Performance:]
#              -J     Get/set  the  Western Digital (WD) Green Drive's "idle3" timeout value.  This timeout
#               controls how often the drive parks its heads and enters a low power consumption state.  The
#               factory default is eight (8) seconds, which is a very poor choice for use  with  Linux.
#               Leaving it at the default will result in hundreds of thousands of head load/unload cycles
#               in a very short period of time.  The drive mechanism is only rated for 300,000 to 1,000,000
#               cycles, so leaving it at the default could result in premature failure, not to mention the
#               performance impact of the drive often having to wake-up before doing routine I/O.
#
#               WD supply a WDIDLE3.EXE DOS utility for tweaking this setting, and you should use that program
#               instead of hdparm if  at  all possible.   The reverse-engineered implementation in hdparm is
#               not as complete as the original official program, even though it does seem to work on at a
#               least a few drives.  A full power cycle is required for any change in setting to  take  effect,
#               regardless of which program is used to tweak things.
#
#               A setting of 30 seconds is recommended for Linux use.  Permitted values are from 8 to 12 seconds,
#               and from 30 to 300 seconds in 30-second increments.  Specify a value of zero (0) to disable the
#               WD idle3 timer completely (NOT RECOMMENDED!).
#
#              --verbose
#               Display extra diagnostics from some commands.
#
#
"""

from tkinter import Tk, messagebox, LabelFrame, BOTH, RAISED


PROGRAM_TITLE = "hdparm API"


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("700x450+250+50")
    mainView.title(PROGRAM_TITLE)

    #   runTimeStamp    = datetime.now()
    #   lineText    = Dispatcher.do(Action.Generate)
    #   lsusbJson   = lineParse(lineText, runTimeStamp)

    #   borderFrame = LabelFrame(mainView, text="Block Devices", border=5, relief=RAISED)
    #   jsonTreeView = JsonTreeView(borderFrame, lsusbJson, {"openBranches": True, "mode": "strict"})
    #   jsonTreeView.pack(expand=True, fill=BOTH)
    #   borderFrame.pack(expand=True, fill=BOTH)

    print(__doc__)
    mainView.mainloop()

