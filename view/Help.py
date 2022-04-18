#   Project:        hardInfo
#   Author:         George Keith Watson
#   Date Started:   March 18, 2022
#   Copyright:      (c) Copyright 2022 George Keith Watson
#   Module:         view/Help.py
#   Date Started:   March 21, 2022
#   Purpose:        pywebview viewer based help content and navigation.
#   Development:
#
import multiprocessing
from copy import deepcopy

import webview

from tkinter import Tk, messagebox, LabelFrame, Radiobutton, StringVar, W, E, RAISED, SUNKEN, BOTH, BooleanVar

from model.Installation import INSTALLATION_FOLDER

PROGRAM_TITLE = "Help"


class HelpStyleConfigureFrame(LabelFrame):

    def __init__(self, container, listener, **keyWordArguments):
        LabelFrame.__init__(self, container, keyWordArguments)
        self.listener = listener
        self.selectStyleVar = StringVar()
        self.radiobuttonSlideOutMenu = Radiobutton(self, text='Slide Out Menu', variable=self.selectStyleVar, anchor=W,
                                                   value='Slide Out Menu')
        self.radiobuttonDropDownMenu = Radiobutton(self, text='Drop Down Menu', variable=self.selectStyleVar, anchor=W,
                                                   value='Drop Down Menu')
        self.radiobuttonExpandCollapse = Radiobutton(self, text='Expand & Collapse', variable=self.selectStyleVar, anchor=W,
                                                     value='Expand & Collapse')
        self.radiobuttonHorizontalList = Radiobutton(self, text='Horizontal List', variable=self.selectStyleVar, anchor=W,
                                                     value='Horizontal List')
        self.radiobuttonCalendar = Radiobutton(self, text='Calendar', variable=self.selectStyleVar, anchor=W,
                                               value='Calendar')
        self.radiobuttonDayNightToggle = Radiobutton(self, text='DayNight Toggle', variable=self.selectStyleVar, anchor=W,
                                                     value='DayNight Toggle')
        #   self.selectStyleVar.set('DayNight Toggle')
        self.selectStyleVar.trace_variable('w', self.styleSelected)

        self.radiobuttonSlideOutMenu.grid(row=0, column=0, sticky=E + W)
        self.radiobuttonDropDownMenu.grid(row=1, column=0, sticky=E + W)
        self.radiobuttonExpandCollapse.grid(row=2, column=0, sticky=E + W)
        self.radiobuttonHorizontalList.grid(row=3, column=0, sticky=E + W)
        self.radiobuttonCalendar.grid(row=4, column=0, sticky=E + W)
        self.radiobuttonDayNightToggle.grid(row=5, column=0, sticky=E + W)

    def styleSelected(self, *args):
        print("HelpStyleConfigure.styleSelected:\t" + self.selectStyleVar.get())
        if self.listener is not None:
            self.listener({'source': 'HelpStyleConfigureFrame.styleSelected', 'style': self.selectStyleVar.get()})

    def messageReceiver(self, message: dict):
        print("HelpStyleConfigure.messageReceiver:\t" + str(message))


class WebViewState:
    webViewWindow = None
    webFileMap = {}
    webFileMap['Slide Out Menu'] = "file://" + INSTALLATION_FOLDER + "WebPageTemplates/Slide Out Menu/index.html/"
    webFileMap['Drop Down Menu'] = "file://" + INSTALLATION_FOLDER + "WebPageTemplates/Drop Down Menu/index.html/"
    webFileMap['Expand & Collapse'] = "file://" + INSTALLATION_FOLDER + "WebPageTemplates/Expand & Collapse/index.html/"
    webFileMap['Horizontal List'] = "file://" + INSTALLATION_FOLDER + "WebPageTemplates/Horizontal List/index.html/"
    webFileMap['Calendar'] = "file://" + INSTALLATION_FOLDER + "WebPageTemplates/Calendar/index.html/"
    webFileMap['DayNight Toggle'] = "file://" + INSTALLATION_FOLDER + "WebPageTemplates/DayNight Toggle/index.html/"

    def __init__(self):
        pass


class MultiProcessingClass(object):

    def __init__(self, name: str, initProperties: dict = None):
        print("MultiProcessingClass constructor:\t" + name)
        self.name = name
        if initProperties is not None:
            if not isinstance(initProperties, dict):
                raise Exception("MultiProcessingClass constructor - Invalid initProperties argument:  " + str(initProperties))
            self.properties = deepcopy(initProperties)
        else:
            self.poperties = {}

        self.mainView = None
        self.helpStyleConfigureFrame = None

        for key, value in self.poperties.items():
            self.__dict__[name] = value

    def getName(self):
        return self.name

    def getProperty(self, name: str):
        if isinstance(name, str) and name in self.properties:
            return self.properties[name]
        return None

    def setStyle(self, style: str):
        print("Help module setStyle:\t" + style)
        WebViewState.webViewWindow = webview.create_window(style, WebViewState.webFileMap[style])
        self.helpStyleConfigureFrame.update()
        webview.start()

    def messageReceiver(self, message: dict):
        print("Help module messageReceiver:\t" + str(message))
        #   {'source': 'HelpStyleConfigureFrame.styleSelected', 'style': self.selectStyleVar.get()}
        if 'source' in message:
            if message['source'] == 'HelpStyleConfigureFrame.styleSelected':
                if 'style' in message:
                    self.setStyle(message['style'])

    def launchHelpStyleSelector(self):
        print("MultiProcessingClass.launchHelpStyleSelector")
        self.mainView = Tk()
        self.mainView.protocol('WM_DELETE_WINDOW', self.ExitProgram)
        self.mainView.geometry("400x300+100+50")
        self.mainView.title(PROGRAM_TITLE)
        self.helpStyleConfigureFrame = HelpStyleConfigureFrame(self.mainView, self.messageReceiver,
                                                          text="Select Help Page Style",
                                                          border=5, relief=RAISED)
        self.helpStyleConfigureFrame.pack(expand=True, fill=BOTH)

        self.mainView.mainloop()

    def ExitProgram(self):
        answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
        if answer:
            self.mainView.destroy()


class Worker:

    def __init__(self, queue):
        """
        This will launch another worker process that will message this one while this one also
        messages the other worker process.
        """
        print("workerProcess - type of queue:\t" + str(type(queue)))
        otherWorker = queue.get()
        print("workerProcess - message in queue:\t" + str(otherWorker))
        if isinstance(otherWorker, MultiProcessingClass):
            print("\nOther Worker:")
            print("\tClass:\tMultiProcessingClass")
            print("\tName:\t" + otherWorker.getName())
            print(Worker.__doc__)
        otherWorker.launchHelpStyleSelector()

    def workerProcess(self, queue):
        pass

    def messageReceiver(self, message: dict):
        print("Worker.messageReceiver:\t" + str(message))


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=Worker, args=(queue, ))
    process.start()
    queue.put(MultiProcessingClass("Process Name: Help"))

    queue.close()
    queue.join_thread()
    process.join()

    exit(0)

    mainView = Tk()
    mainView.protocol('WM_DELETE_WINDOW', ExitProgram)
    mainView.geometry("400x300+100+50")
    mainView.title(PROGRAM_TITLE)



    def setStyle(style: str):
        print("Help module setStyle:\t" + style)
        WebViewState.webViewWindow = webview.create_window(style, WebViewState.webFileMap[style])
        helpStyleConfigureFrame.update()
        webview.start(gui='qt')


    def messageReceiver(message: dict):
        print("Help module messageReceiver:\t" + str(message))
        #   {'source': 'HelpStyleConfigureFrame.styleSelected', 'style': self.selectStyleVar.get()}
        if 'source' in message:
            if message['source'] == 'HelpStyleConfigureFrame.styleSelected':
                if 'style' in message:
                    setStyle(message['style'])


    helpStyleConfigureFrame     = HelpStyleConfigureFrame(mainView, messageReceiver, text="Select Help Page Style",
                                                          border=5, relief=RAISED)
    helpStyleConfigureFrame.pack(expand=True, fill=BOTH)

    mainView.mainloop()

