#   Project:        File Volume Indexer
#   Author:         George Keith Watson
#   Date Started:   January 31, 2019
#                   Imported to hardInfo on March 18, 2022
#   Copyright:      (c) Copyright 2019 George Keith Watson
#   Module:         view/PlatformInfo
#   Purpose:        View platform information
#   Development:
#
#   Project:        LinuxLogReader
#   Author:         George Keith Watson
#   Date Started:   August 25, 2021
#                   Imported to hardInfo on March 18, 2022
#   Copyright:      (c) Copyright 2021 George Keith Watson
#   Module:         view/PropertySheet
#   Date Started:   Imported from LinuxLogForensics project on March 18, 2022.
#   Purpose:        Scrollable Property Sheet for any record.
#   Development:    Copied from VolumeIndexer project on August 25, 2021 and modified to be generally applicable.
#
#       2022-03-16:
#           Generality requires that PropertySheet be a LabelFrame instead of a TopLevel.
#           This will allow one to be removed from any context and placed into any other.
#           Also required are getState() and setModel() methods, since tkinter does not
#           allow the container of a Frame to be changed once is is constructed.
#           Required process:
#               1)  getState() to retrieve all information displayed.
#               2)  grid_forget() or pack_forget() the Frame.
#               3)  destroy() the Frame and also its Toplevel if it has one.
#               4)  Set its reference to None, along with that of itw optional Toplevel to
#                       expedite recycling.
#               5)  Construct a new one with the data from the getState() on the previous provided
#                       either as construction time or using its setModel() method.
#               6)  Grid, pack, or place it in its new context.
#

from os import environ
from copy import deepcopy

from tkinter import Tk, messagebox, Toplevel, Label, Frame, LabelFrame, \
                    FLAT, SUNKEN, RAISED, GROOVE, RIDGE, \
                    W, E, N, S, LEFT, RIGHT, CENTER, BOTH

from view.FrameScroller import FrameScroller
from view.Components import PopupPanel

PROGRAM_TITLE = "Property Sheet"


class PropertyBox(Label):

    def __init__(self, container, model: dict, nameIndex: tuple, **keyWordArguments):
        self.checkArguments(model, nameIndex)
        Label.__init__(self, container, keyWordArguments)
        self.container = container
        self.model = None
        self.nameIndex = None
        self.nRows = 0
        self.nameLabels = {}
        self.valueLabels = {}
        self.setModel(model, nameIndex)

    def setModel(self, model: dict, nameIndex: tuple):
        self.checkArguments(model, nameIndex)
        self.model = model
        self.nameIndex = nameIndex

        #   Determine the length required for the labels
        nameTextLen = 0
        for name in self.nameIndex:
            if len(name) > nameTextLen:
                nameTextLen = len(name)
        valueTextLen = 0
        for name in self.nameIndex:
            if len(str(model[name])) > valueTextLen:
                valueTextLen = len(str(model[name]))
        nameTextLen += 3
        valueTextLen += 3
        rowCount = len(model.keys())
        if rowCount != self.nRows:
            #   reconstruct layout of labels
            row = 0
            for name in self.nameIndex:
                self.nameLabels[name] = Label(self, name='name_label_'+name.replace('.', '_'),
                                        text=name, width=nameTextLen, anchor=W, border=1, relief=RIDGE)
                self.nameLabels[name].bind('<Enter>', self.mouseEntered)
                self.nameLabels[name].bind('<Leave>', self.mouseExited)
                self.nameLabels[name].bind('<Button-1>', self.mouseClicked)
                self.nameLabels[name].bind('<Button-3>', self.mouseClicked)
                self.nameLabels[name].grid(row=row, column=0, sticky=W)

                self.valueLabels[name] = Label(self, name='value_label_'+name.replace('.', '_'),
                                                text=str(self.model[name]), width=valueTextLen, anchor=W,
                                               border=1, relief=RIDGE)
                self.valueLabels[name].bind('<Enter>', self.mouseEntered)
                self.valueLabels[name].bind('<Leave>', self.mouseExited)
                self.valueLabels[name].bind('<Button-1>', self.mouseClicked)
                self.valueLabels[name].bind('<Button-3>', self.mouseClicked)
                self.valueLabels[name].grid(row=row, column=1)
                row += 1
        else:
            #   previous layout can still be used
            pass

    def checkArguments(self, model: dict, nameIndex: tuple):
        if model is None or not isinstance(model, dict):
            raise Exception("PropertyBox constructor - invalid model argument:   " + str(model))
        if nameIndex is None or (not isinstance(nameIndex, list) and not isinstance(nameIndex, tuple)):
            raise Exception("PropertyBox constructor - invalid nameIndex argument:   " + str(nameIndex))
        for name in nameIndex:
            if not isinstance(name, str) or name not in model.keys():
                raise Exception("PropertyBox constructor - invalid nameIndex argument:   " + str(nameIndex))

    def mouseEntered(self, event):
        event.widget.config(fg='blue')

    def mouseExited(self, event):
        event.widget.config(fg='black')

    def mouseClicked(self, event):
        print("mouseClicked:\t" + str(event))


class PropertySheet(LabelFrame):

    FONT_FAMILY     = 'Arial'
    FONT_SIZE       = 10

    DEFAULT_DESIGN      = { 'toplevel': { 'config': {'borderwidth': 5, 'relief': RAISED},
                                          'geometry': {'width': 550, 'height': 400, 'left': 700, 'top': 50},
                                          'title': "Information"
                                       },
                            'frame':    { 'text': 'Properties', 'border': 3, 'relief': SUNKEN,
                                          'padx': 10, 'pady': 10
                                        },
                            'components': {'name': { 'config': { 'font': (FONT_FAMILY, FONT_SIZE), 'relief': GROOVE,
                                                                 'borderwidth': 1, 'anchor': CENTER},
                                                     'grid': {'sticky': W, 'padx': 5, 'pady': 2, 'sticky': E+W}
                                                    },
                                           'value': {'config': {'font': (FONT_FAMILY, FONT_SIZE), 'relief': GROOVE,
                                                        'borderwidth': 3, 'width': 50, 'anchor': W},
                                                     'grid': { 'sticky': W, 'padx': 5, 'pady': 2}
                                                    }
                                          }
                          }

    def __init__(self, container, name: str, properties: tuple, design: dict = None, listener=None,
                 **keyWordArguments ):
        if not isinstance(name, str):
            raise Exception("PropertySheet constructor - Invalid name argument:  " + str(name))
        if not isinstance(properties, tuple):
            raise Exception("PropertySheet constructor - Invalid properties argument:  " + str(properties))
        if design is not None and not isinstance(design, dict):
            raise Exception("PropertySheet constructor - Invalid design argument:  " + str(design))
        if listener is not None and not callable(listener):
            raise Exception("PropertySheet constructor - Invalid listener argument:  " + str(listener))
        self.name = name
        self.properties = deepcopy(properties)
        self.listener = listener
        self.design = deepcopy(PropertySheet.DEFAULT_DESIGN)
        if design is not None:
            self.cascadeDesign(design)

        for name, value in keyWordArguments.items():
            self.design['frame'][name] = value
        LabelFrame.__init__(self, container, self.design['frame'])

        self.frameScroller = FrameScroller(self, "frameScroller")
        self.contentFrame = self.frameScroller.getScrollerFrame()

        self.nameLabels= {}
        self.valueLabels = {}
        self.setModel(properties)

        self.frameScroller.pack(fill=BOTH, expand=True)

    def messageReceiver(self, message):
        print("PropertySheet.messageReceiver:\t" + str(message))
        if 'source' in message:
            pass

    def getState(self):
        return self.properties

    def setModel(self, properties):
        if properties is None or not isinstance(properties, tuple) or len(properties) != 2:
            return False
        if not isinstance(properties[1], list) and not isinstance(properties[1], tuple):
            return False
        if not isinstance(properties[0], dict):
            return False
        for name in properties[1]:
            if not name in properties[0]:
                return False
        #   Check fo unindexed entries?

        self.properties = deepcopy(properties)
        self.info = self.properties[0]
        self.nameIndex = self.properties[1]

        for name, label in self.nameLabels.items():
            label.grid_forget()
        for name, label in self.valueLabels.items():
            label.grid_forget()
        self.nameLabels = {}
        self.valueLabels = {}
        self.nameLabelToPropName    = {}
        self.valueLabelToPropName   =   {}
        row = 0
        for name in self.nameIndex:
            #   print('\tProperty Name:\t' + name)
            if not name in ("U-Name", 'System Alias'):
                labelName = Label(self.contentFrame, name='name_label_' + name.replace('.', '_'),
                                  text=name, anchor=W, border=3, relief=RIDGE)
                labelName.bind('<Enter>', self.mouseEntered)
                labelName.bind('<Leave>', self.mouseExited)
                labelName.bind('<Button-1>', self.mouseClicked)
                labelName.bind('<Double-Button-1>', self.mouseDoubleClicked)
                labelName.bind('<Button-3>', self.mouseClicked)
                self.nameLabels[name] = labelName
                self.nameLabelToPropName[labelName] = name
                labelName.grid(row=row, column=0, sticky=W)

                labelValue = Label(self.contentFrame, name='value_label_' + name.replace('.', '_'),
                                   text=str(self.info[name]), anchor=W, border=3, relief=RIDGE)
                labelValue.bind('<Enter>', self.mouseEntered)
                labelValue.bind('<Leave>', self.mouseExited)
                labelValue.bind('<Button-1>', self.mouseClicked)
                labelName.bind('<Double-Button-1>', self.mouseDoubleClicked)
                labelValue.bind('<Button-3>', self.mouseClicked)
                self.valueLabels[name] = labelValue
                self.valueLabelToPropName[labelValue] = name
                labelValue.grid(row=row, column=1)

                if self.design != None and 'components' in self.design:
                    if 'name' in self.design['components']:
                        if 'config' in self.design['components']['name']:
                            labelName.config(self.design['components']['name']['config'])
                        if 'grid' in self.design['components']['name']:
                            labelName.grid_configure(self.design['components']['name']['grid'])
                    if 'value' in self.design['components']:
                        if 'config' in self.design['components']['value']:
                            labelValue.config(self.design['components']['value']['config'])
                        if 'grid' in self.design['components']['value']:
                            labelValue.grid_configure(self.design['components']['value']['grid'])
                row += 1

    def getContentFrame(self):
        return self.contentFrame

    def mouseEntered(self, event):
        #   print("mouseEntered:\t" + str(event.widget._name))
        event.widget.config(fg='blue', border=3, relief=SUNKEN)

    def mouseExited(self, event):
        #   print("mouseExited:\t" + str(event.widget._name))
        event.widget.config(fg='black', border=3, relief=RIDGE)

    def accessEventInfo(self, event):
        propertyName = ''
        labelType = ''
        if event.widget in self.nameLabelToPropName:
            propertyName = self.nameLabelToPropName[event.widget]
            labelType = 'name'
        elif event.widget in self.valueLabelToPropName:
            propertyName = self.valueLabelToPropName[event.widget]
            labelType = 'value'
        return {
            'propertyName': propertyName,
            'labelType': labelType,
            'button': event.num,
            'controlName': event.widget._name
        }

    def mouseClicked(self, event):
        print("mouseClicked:\t" + str(event.widget._name))
        if self.listener is not None:
            message = self.accessEventInfo(event)
            message['source'] = "PropertySheet.mouseClicked"
            self.listener(message)

    def mouseDoubleClicked(self, event):
        print("PropertySheet.mouseDoubleClicked:\t" + str(event.widget._name))
        if self.listener is not None:
            message = self.accessEventInfo(event)
            message['source'] = "PropertySheet.mouseDoubleClicked"
            self.listener(message)

    def cascadeDesign(self, design: dict):
        if design is None:
            return
        if not isinstance(design, dict):
            raise Exception("PropertySheet.cascadeDesign - invalid design argument:   " + str(design))
        if 'toplevel' in design:
            if isinstance(design['toplevel'], dict):
                if 'config' in design['toplevel']:
                    if isinstance(design['toplevel']['config'], dict):
                        for name, value in design['toplevel']['config'].items():
                            self.design['toplevel']['config'][name] = value
                if 'geometry' in design['toplevel']:
                    if isinstance(design['toplevel']['geometry'], dict):
                        for name, value in design['toplevel']['geometry'].items():
                            self.design['toplevel']['geometry'][name] = value
                if 'title' in design['toplevel']:
                    if isinstance(design['toplevel']['title'], str):
                        self.design['toplevel']['title'] = design['toplevel']['title']
        if 'frame' in design:
            if isinstance(design['frame'], dict):
                if 'text' in design['frame'] and isinstance(design['frame']['text'], str):
                    self.design['frame']['text'] = design['frame']['text']
                if 'border' in design['frame'] and isinstance(design['frame']['border'], int):
                    self.design['frame']['border'] = design['frame']['border']
                if 'relief' in design['frame'] and isinstance(design['frame']['relief'], str):
                    self.design['frame']['relief'] = design['frame']['relief']
                if 'padx' in design['frame'] and isinstance(design['frame']['padx'], int):
                    self.design['frame']['padx'] = design['frame']['padx']
                if 'pady' in design['frame'] and isinstance(design['frame']['pady'], int):
                    self.design['frame']['pady'] = design['frame']['pady']
        if 'components' in design:
            if isinstance(design['components'], dict):
                if 'name' in design['components']:
                    if isinstance(design['components']['name'], dict):
                        if 'config' in design['components']['name']:
                            if isinstance(design['components']['name']['config'], dict):
                                for name, value in design['components']['name']['config'].items():
                                    self.design['components']['name']['config'][name] = value
                        if 'grid' in design['components']['name']:
                            if isinstance(design['components']['name']['grid'], dict):
                                for name, value in design['components']['name']['grid'].items():
                                    self.design['components']['name']['grid'][name] = value
                if 'value' in design['components']:
                    if isinstance(design['components']['value'], dict):
                        if 'config' in design['components']['value']:
                            if isinstance(design['components']['value']['config'], dict):
                                for name, value in design['components']['value']['config'].items():
                                    self.design['components']['value']['config'][name] = value
                        if 'grid' in design['components']['value']:
                            if isinstance(design['components']['value']['grid'], dict):
                                for name, value in design['components']['value']['grid'].items():
                                    self.design['components']['value']['grid'][name] = value


class PropertySheetTopLevel(Toplevel):

    FONT_FAMILY     = 'Arial'
    FONT_SIZE       = 10

    DEFAULT_DESIGN      = { 'toplevel': { 'config': {'borderwidth': 3, 'relief': SUNKEN},
                                          'geometry': {'width': 400, 'height': 300, 'x': 700, 'y': 50},
                                          'title': "Information"
                                       },
                            'components': {'name': { 'config': { 'font': (FONT_FAMILY, FONT_SIZE), 'relief': GROOVE,
                                                                 'borderwidth': 1, 'anchor': CENTER},
                                                     'grid': {'sticky': W, 'padx': 5, 'pady': 2, 'sticky': E+W}
                                                    },
                                           'value': {'config': {'font': (FONT_FAMILY, FONT_SIZE), 'relief': GROOVE,
                                                        'borderwidth': 3, 'width': 50, 'anchor': W},
                                                     'grid': { 'sticky': W, 'padx': 5, 'pady': 2}
                                                    }
                                          }
                          }

    DEFAULT_SCROLLABLE_DESIGN   = {}

    def __init__(self, parent, name: str, properties: tuple, design: dict = None, listener=None):
        Toplevel.__init__(self, parent, borderwidth=3, height=300,width=400, relief=SUNKEN)
        #Toplevel.__init__(self, parent, name=name)

        #   Replace any property in the default design with those present in the design attribute.
        #   Leave all others.
        self.design = PropertySheetTopLevel.DEFAULT_DESIGN
        if design is not None:
            self.cascadeDesign(design)
        self.listener = None
        if listener is not None and callable(listener):
            self.listener = listener

        if self.design != None and 'toplevel' in self.design:
            if 'config' in self.design['toplevel']:
                self.config(self.design['toplevel']['config'])
            if 'geometry' in self.design['toplevel']:
                self.width = self.design['toplevel']['geometry']['width']
                self.height = self.design['toplevel']['geometry']['height']
                self.x = self.design['toplevel']['geometry']['x']
                self.y = self.design['toplevel']['geometry']['y']
                geometryStr = str(self.width) + "x" + str(self.height) + '+' + str(self.x) + '+' + str(self.y)
                self.geometry( geometryStr )
            else:
                self.geometry( "650x400+700+50" )
            if 'title' in self.design['toplevel']:
                self.title(self.design['toplevel']['title'])
            else:
                self.title("Platform Information")

        self.frameScroller = FrameScroller(self, "frameScroller")
        self.contentFrame = self.frameScroller.getScrollerFrame()

        self.nameLabels= {}
        self.valueLabels = {}
        self.setModel(properties)

        self.frameScroller.pack(fill=BOTH, expand=True)

    def getContentFrame(self):
        return self.contentFrame

    def messageReceiver(self, message: dict):
        print("PropertySheet.messageReceiver:\t" + str(message))
        if message is None or not isinstance(message, dict):
            return False
        if 'type' in message:
            if message['type'] == 'setModel':
                if 'properties' in message and isinstance(message['properties'], tuple):
                    self.setModel(message['properties'])
            if message['type'] == 'selection':
                if 'properties' in message and isinstance(message['properties'], tuple):
                    # Assert:   message['properties'] == [message source].fileDataMap[self.fileName].getAttributes()
                    self.setModel(message['properties'])

    def sendMessage(self, message: dict):
        if self.listener is not None:
            self.listener(message)

    def mouseEntered(self, event):
        #   print("mouseEntered:\t" + str(event.widget._name))
        event.widget.config(fg='blue', border=3, relief=SUNKEN)

    def mouseExited(self, event):
        #   print("mouseExited:\t" + str(event.widget._name))
        event.widget.config(fg='black', border=3, relief=RIDGE)

    def mouseClicked(self, event):
        print("mouseClicked:\t" + str(event.widget._name))


    def setModel(self, properties):
        if properties is None or not isinstance(properties, tuple) or len(properties) != 2:
            return False
        if not isinstance(properties[1], list) and not isinstance(properties[1], tuple):
            return False
        if not isinstance(properties[0], dict):
            return False
        for name in properties[1]:
            if not name in properties[0]:
                return False
        #   Check fo unindexed entries?

        self.info = properties[0]
        self.nameIndex = properties[1]

        for name, label in self.nameLabels.items():
            label.grid_forget()
        for name, label in self.valueLabels.items():
            label.grid_forget()
        self.nameLabels = {}
        self.valueLabels = {}

        row = 0
        for name in self.nameIndex:
            #   print('\tProperty Name:\t' + name)
            if not name in ("U-Name", 'System Alias'):
                labelName = Label(self.contentFrame, name='name_label_'+name.replace('.', '_'),
                                  text=name, anchor=W, border=3, relief=RIDGE)
                labelName.bind('<Enter>', self.mouseEntered)
                labelName.bind('<Leave>', self.mouseExited)
                labelName.bind('<Button-1>', self.mouseClicked)
                labelName.bind('<Button-3>', self.mouseClicked)
                self.nameLabels[name] = labelName
                labelName.grid(row=row, column=0, sticky=W)

                labelValue = Label(self.contentFrame, name='value_label_'+name.replace('.', '_'),
                                   text=str(self.info[name]), anchor=W, border=3, relief=RIDGE)
                labelValue.bind('<Enter>', self.mouseEntered)
                labelValue.bind('<Leave>', self.mouseExited)
                labelValue.bind('<Button-1>', self.mouseClicked)
                labelValue.bind('<Button-3>', self.mouseClicked)
                self.valueLabels[name] = labelValue
                labelValue.grid(row=row, column=1)

                if self.design != None and 'components' in self.design:
                    if 'name' in self.design['components']:
                        if 'config' in self.design['components']['name']:
                            labelName.config(self.design['components']['name']['config'])
                        if 'grid' in self.design['components']['name']:
                            labelName.grid_configure(self.design['components']['name']['grid'])
                    if 'value' in self.design['components']:
                        if 'config' in self.design['components']['value']:
                            labelValue.config(self.design['components']['value']['config'])
                        if 'grid' in self.design['components']['value']:
                            labelValue.grid_configure(self.design['components']['value']['grid'])
                row += 1

    def cascadeDesign(self, design: dict):
        if design is None:
            return
        if not isinstance(design, dict):
            raise Exception("PropertySheet.cascadeDesign - invalid design argument:   " + str(design))
        if 'toplevel' in design:
            if isinstance(design['toplevel'], dict):
                if 'config' in design['toplevel']:
                    if isinstance(design['toplevel']['config'], dict):
                        for name, value in design['toplevel']['config'].items():
                            self.design['toplevel']['config'][name] = value
                if 'geometry' in design['toplevel']:
                    if isinstance(design['toplevel']['geometry'], dict):
                        for name, value in design['toplevel']['geometry'].items():
                            self.design['toplevel']['geometry'][name] = value
                if 'title' in design['toplevel']:
                    if isinstance(design['toplevel']['title'], str):
                        self.design['toplevel']['title'] = design['toplevel']['title']

        if 'components' in design:
            if isinstance(design['components'], dict):
                if 'name' in design['components']:
                    if isinstance(design['components']['name'], dict):
                        if 'config' in design['components']['name']:
                            if isinstance(design['components']['name']['config'], dict):
                                for name, value in design['components']['name']['config'].items():
                                    self.design['components']['name']['config'][name] = value
                        if 'grid' in design['components']['name']:
                            if isinstance(design['components']['name']['grid'], dict):
                                for name, value in design['components']['name']['grid'].items():
                                    self.design['components']['name']['grid'][name] = value
                if 'value' in design['components']:
                    if isinstance(design['components']['value'], dict):
                        if 'config' in design['components']['value']:
                            if isinstance(design['components']['value']['config'], dict):
                                for name, value in design['components']['value']['config'].items():
                                    self.design['components']['value']['config'][name] = value
                        if 'grid' in design['components']['value']:
                            if isinstance(design['components']['value']['grid'], dict):
                                for name, value in design['components']['value']['grid'].items():
                                    self.design['components']['value']['grid'][name] = value


def ExitProgram():
    answer = messagebox.askyesno('Exit program ', "Exit the " + PROGRAM_TITLE + " program?")
    if answer:
        mainView.destroy()


if __name__ == '__main__':
    mainView = Tk()
    mainView.geometry("700x500+100+50")
    mainView.title(PROGRAM_TITLE)
    mainView.layout = "grid"
    mainView.protocol('WM_DELETE_WINDOW', lambda: ExitProgram())

    #   Sample data:    currtent environment variable settings
    info = {}
    nameIndex = []
    for name, value in environ.items():
        print( name + ":\t" + str(value))
        info[name] = value
        nameIndex.append(name)
    nameIndex.sort()

    """
    DEFAULT_DESIGN      = { 'toplevel': { 'config': {'borderwidth': 5, 'relief': SUNKEN},
                                          'geometry': {'width': 650, 'height': 600, 'x': 700, 'y': 50},
                                          'title': "Information"
                                       },
                            'components': {'name': { 'config': { 'font': (FONT_FAMILY, FONT_SIZE), 'relief': GROOVE,
                                                                 'borderwidth': 1, 'anchor': CENTER},
                                                     'grid': {'sticky': W, 'padx': 5, 'pady': 2, 'sticky': E+W}
                                                    },
                                           'value': {'config': {'font': (FONT_FAMILY, FONT_SIZE), 'relief': GROOVE,
                                                        'borderwidth': 3, 'width': 50, 'anchor': W},
                                                     'grid': { 'sticky': W, 'padx': 5, 'pady': 2}
                                                    }
                                          }
                          }
    """


    design = {  'toplevel': {
                    'config': { 'borderwidth': 5,'relief': 'raised'},
                    'geometry': { 'width': 750, 'height': 500, 'x': 600, 'y': 50 }
                },
                'frame': {'text': 'Environment Variables', 'border': 3, 'relief': SUNKEN,
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
    #   popupPanel.setContent(propertySheet, **{'row': 0, "column": 0, 'padx': 5, 'pady': 5})
    #   Horizontal scroll appears to work better with pack():
    #   propertySheet.pack(expand=True, fill=BOTH)

    #   This works: (2022-03-16)
    #   state = propertySheet.getState()
    #   for key, value in state[0].items():
    #       state[0][key] = None
    #   propertySheet.setModel(state)

    #   popupPanel.show()
    mainView.mainloop()

    """
    platformInfo = PropertySheetTopLevel(None, "platformInfo", (info, nameIndex), design)
    mainView.mainloop()
    platformInfo.mainloop()
    """
