# hardInfo

The purpose of this project is to create a Python API for gethering personal computer hardware information and other platform information into usable objects insode a Python program.  The general method it employs is to safely run Linux commands from within Python and then parse the output.

Writing Python programs to run on any operating system on any hardware is not possible without being able to dynamically adapt to the stack of layers running beneath your program.  Although Python's library is very helpful in this regard, there are still problems adapting various functional categories of features for as complete of generality as possible.  This projects aims to solve that by collecting anything and everything relevant, thereby also providing a general interface to Linux commands usable in any Python program.
