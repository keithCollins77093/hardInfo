"""
#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         model/HDparm.py
#   Date Started:   March 24, 2022
#   Purpose:        Store and provide API for Linux hdparm command.
#   Development:

    run with:   sudo dmidecode > output.txt
                    Must run as sudo.
                    See man page, included, for valid DMI Type values.

    man dmidecode:
       dmidecode is a tool for dumping a computer's DMI (some say SMBIOS) table contents in a human-readable
       format. This table contains a description of the system's hardware components, as well as other useful
       pieces of information such  as  serial  numbers  and  BIOS revision. Thanks to this table, you can
       retrieve this information without having to probe for the actual hardware.  While this is a
       good point in terms of report speed and safeness, this also makes the presented information
       possibly unreliable.

       The DMI table doesn't only describe what the system is currently made of, it also can report the
       possible evolutions (such  as  the fastest supported CPU or the maximal amount of memory supported).

       [Focusing the output:}
            -s, --string KEYWORD
                Only  display  the  value of the DMI string identified by KEYWORD.  KEYWORD must be a keyword
                from the following list: bios-vendor, bios-version, bios-release-date,  system-manufacturer,
                system-product-name,  system-version,  system-serial-number, system-uuid,  baseboard-manufacturer,
                baseboard-product-name,  baseboard-version, baseboard-serial-number, baseboard-asset-tag,
                chassis-manufacturer, chassis-type, chassis-version, chassis-serial-number, chassis-asset-tag,
                processor-family,  pro‐cessor-manufacturer,  processor-version, processor-frequency.
                Each keyword corresponds to a given DMI type and a given off‐set within this entry type.
                Not all strings may be meaningful or even defined on all systems. Some keywords may return more
                than  one  result  on some systems (e.g.  processor-version on a multi-processor system).
                If KEYWORD is not provided or not valid, a list of all valid keywords is printed and dmidecode
                exits with an error.  This option  cannot  be  used  more  than once.
#
#
"""

from tkinter import Tk, messagebox, LabelFrame, BOTH, RAISED


PROGRAM_TITLE = "DMI Decode API"


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

