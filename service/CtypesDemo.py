#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         view/Help.py
#   Date Started:   March 21, 2022
#   Purpose:        Demo of ctypes uses and also an attempt to design a service to facilitate general parameterized
#                   dll function use.  User should be able to specify the library by name and the function to
#                   call and pass the arguments required receiving the return value back.
#   Development:

from ctypes import cdll, CDLL, \
                    c_wchar_p, c_int, c_wchar, c_void_p, c_char_p, c_char, c_int8, c_int16, c_int32, c_int64, \
                    c_bool, c_byte, c_long, c_uint, c_uint8, c_uint16, c_uint32, c_uint64, c_longlong, c_ubyte, \
                    c_float, c_short, c_ulong, c_ulonglong, c_buffer, c_ushort, c_double, c_longdouble, c_size_t, \
                    c_ssize_t, \
                    create_string_buffer, sizeof, byref

from tkinter import Tk, messagebox

from SharedLibInterface import LibFunctions
from SharedLibInterface import LinuxCommands

PROGRAM_TITLE = "Python ctypes interface to Linux Shared Libraries"


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        exit(0)
        #   mainView.destroy()


if __name__ == '__main__':
    print("CtypesDemo module is running")
    #   LinuxCommands.ldconfig()
    #   LinuxCommands.nm()
    #   LinuxCommands.readelf()

    #   Getting a function pointer using the symbol name.
    #   Symbol names are listed in nm output in file, nm,verbose.json, and dll.db table, Symbols.
    libc    = cdll.LoadLibrary("libc.so.6")
    accept = getattr(libc, "accept")
    print("\nlibc symbol accept:\t" + str(accept))
    printf = getattr(libc, "printf")
    print("\nlibc symbol printf:\t" + str(printf))
    libc.printf(b"\nMessage from C land:\tYour Doomed!\n")
    printf(b"\nHello, %S\n", "Ukraine!")

    #   Working with type equivalents:
    printf(b"%3.2f bottles of beer\n", c_double(42.5))
    i = c_int(42)
    print("\n\ti.value:\t" + str(i.value))
    i.value = 57
    print("\ti.value:\t" + str(i.value))

    s = "Hello ctypes"
    c_s = c_wchar_p(s)
    print("c_s.value:\t" + c_s.value)
    c_s.value = "Hello there"
    print("c_s.value:\t" + c_s.value)

    #   ctypes c_* types are immutable, meaning they cannot be changed by the receiving 'C' function.
    #   If mutability, like a reference, is required, use create_string_buffer().
    p = create_string_buffer(b"32 Byte Array", 32)    #   initialized a 64 byte array to nulls.
    print(sizeof(p), repr(p.raw))
    print(p.value[2])

    #   Using the argtypes list, available in ctypes function "pointers":
    printf.argtypes = [c_char_p, c_char_p, c_int, c_double]
    printf(b"String: '%s';\tInt: %d;\tDouble: %2.2f\n", b"ctypes", 76, 22.22)

    #   Casting return types:
    strchr = libc.strchr
    returnVal = strchr(b"abcdef", ord("d"))
    print("\nstrchr:\t" + str(returnVal))
    strchr.restype = c_char_p
    returnVal   = strchr(b"abcdef", ord("d")).decode('utf-8')
    print("\nstrchr:\t" + returnVal)
    #   Variation:
    strchr.argtypes = [c_char_p, c_char]
    returnVal   = strchr(b"abcdef", b"d").decode('utf-8')
    print("\nstrchr:\t" + returnVal)

    #   Pass by reference so that receiver can change content
    i = c_int()
    f = c_float()
    s = create_string_buffer(b'\000' * 32)
    print("i:\t" + str(i.value), "\tf:\t" + str(f.value), "\ts:\t" + str(repr(s.value)))
    sscanf = getattr(libc, "sscanf")
    sscanf(b"1 3.14 Hello", b"%d %f %s", byref(i), byref(f), s)
    print(i.value, f.value, repr(s.value))


    """
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("700x500+100+50")
    mainView.title(PROGRAM_TITLE)

    mainView.mainloop()
    """
