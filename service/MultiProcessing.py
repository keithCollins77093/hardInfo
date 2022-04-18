#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         service/MultiProcessing.py
#   Date Started:   March 22, 2022
#   Purpose:        Manage initiation and communication between any number of independent processes launched
#                   in Python.
#   Development:
#       2022-03-22: (Experimenting with code examples from: www.tutorialspoint.com/multiprocessing-in-python)
#           Each module in this program is an independent tool that can communicate with other tools as needed.
#           If another tool is not present in the MultiProcessing registry, its features are simply not
#           available in the current tool set.  Tools / Python modules, can then be installed, configured,
#           and activated and deactivated dynamically, allowing easy upgrade from the free, non-commercial
#           version of an application the the commercial, paid-for version.
#

from multiprocessing import Process, JoinableQueue, Queue, cpu_count, Event

from tkinter import Tk, messagebox, BOTH

PROGRAM_TITLE = "MultiProcessing"


class ProcessRegistry:

    def __init__(self, applicationName: str, **keyWordArguments):
        #   keyWordArguments includes:
        #       'object':   An object of a class with particular methods included:
        #           messageReceiver( message: dict )
        #
        pass

    def registerProcess(self, processName: str, attributes: str):
        pass

    def startProcess(self, processName: str, arguments: dict):
        pass

    def stopProcess(self, processName: str):
        pass

    def configureProcesss(self, processName: str, confiuration: dict):
        pass

    def activateProcess(self, processName: str, arguments: dict):
        pass

    def deactivateProcess(self, processName: str, arguments: dict):
        pass


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        #   mainView.destroy()
        pass


#************************************* Multiple Windowing Processes Test Code *********************************

from os import environ
from view.PropertySheet import PropertySheet


def messageReceiver(message: dict):
    print("MultiProcessing.messageReceiver:\t" + str(message))


def theFullMonty(*args):
    print("Four score and seven years ago Marilyn Chambers sat on my face", end=" ")
    for arg in args:
        print(str(arg), end=' ')


from json import loads

from model.Installation import LSHW_JSON_FILE
from view.Components import JsonTreeView

ENV_PROCESS_TITLE = "Current Environment"
HWD_PROCESS_TITLE = "Current Hardware"


def showEnvironment(geoStr):

    def exitProcess():
        answer = messagebox.askyesno('Exit Process ', "Exit the " + ENV_PROCESS_TITLE + " process?")
        if answer:
            processView.destroy()

    processView = Tk()
    processView.protocol('WM_DELETE_WINDOW', exitProcess)
    processView.geometry(geoStr)
    processView.title(ENV_PROCESS_TITLE)
    info = {}
    nameIndex = []
    for name, value in environ.items():
        #   print( name + ":\t" + str(value))
        info[name] = value
        nameIndex.append(name)
    nameIndex.sort()
    propertySheet   = PropertySheet(processView, "Environment Variables", (info, nameIndex), listener=messageReceiver )
    propertySheet.pack(expand=True, fill=BOTH)
    processView.mainloop()


def showHardware(geoStr):
    def exitProcess():
        answer = messagebox.askyesno('Exit Process ', "Exit the " + HWD_PROCESS_TITLE + " process?")
        if answer:
            processView.destroy()

    processView = Tk()
    processView.protocol('WM_DELETE_WINDOW', exitProcess)
    processView.geometry(geoStr)
    processView.title(HWD_PROCESS_TITLE)

    lshwJsonFile = open(LSHW_JSON_FILE, "r")
    jsonText = lshwJsonFile.read()
    lshwJsonFile.close()
    propertyMap = loads(jsonText)
    jsonTreeView = JsonTreeView(processView, propertyMap, {"openBranches": True, "mode": "strict"})
    jsonTreeView.pack(expand=True, fill=BOTH)

    processView.mainloop()

#************************************* Communicating Multiple Processes Test Code *********************************

import time

class Tool(Process):

    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                #   Poison pill means shutdown
                print( '%s: Exiting' % proc_name )
                self.task_queue.task_done()
                break
            print( '%s: %s' % (proc_name, next_task))
            answer = next_task()
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return


class Task(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __call__(self, *args, **kwargs):
        time.sleep(0.1)     #   Simulated processing time
        return '%s * %s = %s' % (self.a, self.b, self.a * self.b)
    def __str__(self):
        return '%s * %s' % (self.a, self.b)

#********************************* Signaling Between Processes Test Code *********************************

def wait_for_event(event):
    """wait for the event to be set before doing anything"""
    print('wait_for_event: starting')
    event.wait()
    print('wait_for_event: event.is_set()-> ', event.is_set())

def wait_for_event_timeout(event, sec):
    """wait sec seconds and then timeout"""
    print('wait_for_event_timeout: starting')
    event.wait(sec)
    print('wait_for_event_timeout: event.is_set()-->', event.is_set())


if __name__ == '__main__':
    # ********************************* Signaling Between Processes Test Code *************************************
    event = Event()
    workerOne    = Process(name='block', target=wait_for_event, args=(event,))
    workerOne.start()
    workerTwo   = Process(name='non-block', target=wait_for_event_timeout, args=(event, 2))
    workerTwo.start()

    print('main: waiting before calling Event.set()')
    time.sleep(3)
    event.set()
    print('main: event is set')

    # ************************************* Communicating Multiple Processes Test Code *********************************
    """
    #   Establish communication queues
    tasks = JoinableQueue()
    results = Queue()

    #   Start Tools:
    num_tools = cpu_count() * 2
    print('Creating %d Tools' % num_tools)
    tools = [ Tool(tasks, results)  for i in range(num_tools) ]
    for tool in tools:
        tool.start()

    #   Enqueue jobs
    num_jobs = 10
    for i in range(num_jobs):
        tasks.put(Task(i, i))

    #   Add a poison pill for each Tool
    for i in range(num_tools):
        tasks.put(None)

    #   Wait for all of the tasks to finish
    tasks.join()

    #   Start printing results
    while num_jobs:
        result = results.get()
        print( 'Result:\t', result )
        num_jobs -= 1
    """

    # ********************************* Multiple Windowing Processes Test Code *********************************
    """
    georgeKeenan = Process(target=theFullMonty, args=("and wiggled", "rapidly gyrating", "her hips"))
    environmentDialog = Process(target=showEnvironment, args=("600x500+100+50",))
    hardwareDialog = Process(target=showHardware, args=("600x500+600+50",))

    georgeKeenan.start()
    environmentDialog.start()
    hardwareDialog.start()

    idx = 0
    while idx < 10:
        print(str(idx), end="\t")
        idx += 1

    georgeKeenan.join()
    environmentDialog.join()
    hardwareDialog.join()
    """
    """
    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("600x500+100+50")
    mainView.title(PROGRAM_TITLE)

    mainView.mainloop()
    """
