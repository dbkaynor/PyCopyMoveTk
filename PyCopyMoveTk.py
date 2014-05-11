# https://docs.python.org/3/
#
#TODO
#Check source and destinations for permissions and ownership

#Debug levels
#Priorities for source file?
#    SetDefaults()
#    ProjectLoad('default')
#    GetClipBoard()Main.clipboard_get()
#    ParseCommandLine()
#
# Walkway lights
# GeoMetro car seat, center tail light
# Trailer lights
#
# http://www.shayanderson.com/linux/using-git-with-remote-repository.htm
#
import sys
import os
import time
import platform
sys.path.append('auxfiles')
#import tkinter
from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import argparse
import logging
import shutil
import re
import __main__ as main
from inspect import currentframe, getframeinfo
from send2trash import send2trash
from ToolTip import ToolTip
import subprocess
from subprocess import Popen, PIPE
#import hashlib  #sha1
import pprint
pp=pprint.pprint

Main = tkinter.Tk()

#------------------------------
class Vars():
    DestinationCheckToggleStateVar = BooleanVar()
    DestinationCheck01Var = BooleanVar()
    DestinationCheck02Var = BooleanVar()
    DestinationCheck03Var = BooleanVar()
    DestinationCheck04Var = BooleanVar()
    DestinationCheck05Var = BooleanVar()
    DestinationCheck06Var = BooleanVar()
    DestinationCheck07Var = BooleanVar()
    DestinationCheck08Var = BooleanVar()
    KeepFlagsCheckVar = BooleanVar()
    AskOnCopyVar = BooleanVar()
    AskOnMoveVar = BooleanVar()
    AskOnRecycleVar = BooleanVar()
    AskOnDeleteVar = BooleanVar()
    AskOnRenameVar = BooleanVar()
    AskBeforeOverWriteDuringCopyVar = BooleanVar()
    AskBeforeOverWriteDuringMoveVar = BooleanVar()

    StatusVar = StringVar()
    SourceInfoVar = StringVar()
    ProjectFileNameVar = StringVar()
    ProjectFileExtensionVar = StringVar()
    LogFileNameVar = StringVar()
    SystemEditorVar = StringVar()
    SystemRenamerVar = StringVar()
    StartUpDirectoryVar = StringVar()
    AuxDirectoryVar = StringVar()
    HelpFileVar = StringVar()
    CommentsVarList = []
    HelpTopLevelVar = None
    FileRenameTopLevelVar = None
#------------------------------
#LogLevel 0 is log everything
def Logger(LogMessage, FrameInfoDict, ShowInStatus = False, PrintToCommandLine = False, LogLevel = 0):
    MyLogger = logging.getLogger(Vars.LogFileNameVar.get())
    mystr = LogMessage + ' Module:' + str(FrameInfoDict[0]) +  '  Line:' + str(FrameInfoDict[1])
    MyLogger.debug(mystr)
    if PrintToCommandLine: print(mystr)
    if ShowInStatus: Vars.StatusVar.set(LogMessage)
'''
debug, info,warning, error, critical, log, exception
'''
#------------------------------
#Set up defaults in case there is no project file
def SetDefaults():
    print('SetDefaults')
    Vars.KeepFlagsCheckVar.set(1)
    Vars.AskOnCopyVar.set(1)
    Vars.AskOnMoveVar.set(1)
    Vars.AskOnRecycleVar.set(1)
    Vars.AskOnDeleteVar.set(1)
    Vars.AskOnRenameVar.set(1)
    Vars.AskBeforeOverWriteDuringCopyVar.set(1)
    Vars.AskBeforeOverWriteDuringMoveVar.set(1)
    FileSourceEntry.delete(0,END)
    Vars.DestinationCheck01Var.set(0)
    Vars.DestinationCheck02Var.set(0)
    Vars.DestinationCheck03Var.set(0)
    Vars.DestinationCheck04Var.set(0)
    Vars.DestinationCheck05Var.set(0)
    Vars.DestinationCheck06Var.set(0)
    Vars.DestinationCheck07Var.set(0)
    Vars.DestinationCheck08Var.set(0)
    Vars.SystemRenamerVar.set('')
    Vars.SystemEditorVar.set('')

#------------------------------
#Initialize the program
def StartUpStuff():
    print('StartUpStuff')
    #-- Lots of startup stuff ------------------------------------
    #The following are defaults which will be over written by a project file
    if sys.platform.startswith('linux'):
        Vars.SystemEditorVar.set('gedit')
        Vars.SystemRenamerVar.set('pyrename')
        Vars.ProjectFileExtensionVar.set('prjl')
    elif sys.platform.startswith('win32'):
        Vars.SystemEditorVar.set('c:\\windows\\notepad.exe')
        Vars.SystemRenamerVar.set('C:\\Program Files (x86)\\Ant Renamer\\Renamer.exe')
        Vars.ProjectFileExtensionVar.set('prjw')

    Vars.StartUpDirectoryVar.set(os.getcwd())
    Vars.AuxDirectoryVar.set(os.path.join(Vars.StartUpDirectoryVar.get(),'auxfiles','.'))
    Vars.HelpFileVar.set(os.path.join(Vars.AuxDirectoryVar.get(), 'PyCopyMoveTk.hlp'))
    print(Vars.AuxDirectoryVar.get())
    SetUpLogger()

    Logger(str(os.environ.get('OS')), getframeinfo(currentframe()))
    Logger(str(platform.uname()), getframeinfo(currentframe()))
    Logger('Number of argument(s): ' + str(len(sys.argv)), getframeinfo(currentframe()), ShowInStatus = True)
    Logger('Argument List: ' + str(sys.argv), getframeinfo(currentframe()))

    ProjectLoad('default')
    GetClipBoard()

#------------------------------
#Parse the command line
def ParseCommandLine():
    #Test that the file exists on the path
    def is_valid_file(parser, arg):
        if len(arg) == 0: arg = FileSourceEntry.get()
        if arg == '.': arg = ''
        if not os.path.isfile(arg) and arg != '':
            tkinter.messagebox.showerror('Source file error' , \
                'The source file does not exist or is not a file\n' + arg)
            Logger('The source file does not exist or is not a file ' + arg, getframeinfo(currentframe()))
        else:
            FileSourceEntry.delete(0, END)
            FileSourceEntry.insert(0, arg)
            Vars.SourceInfoVar.set(FileStat(FileSourceEntry.get()))
            Logger('Source from command line: >>' + arg + '<<', getframeinfo(currentframe()))

    def is_valid_project(parser, arg):
        if not os.path.isfile(arg):
            tkinter.messagebox.showerror('Project file error' , \
                'The project file does not exist or is not a file\n' + arg)
            Logger('The project file does not exist or is not a file ' + arg, getframeinfo(currentframe()))
            return
        else:
            Vars. ProjectFileNameVar.set(arg)
            Logger('Project file from command line: >>' + arg + '<<', getframeinfo(currentframe()))

    parser = argparse.ArgumentParser(description='A tool to help copy or move files.')

    #parser.add_argument('-s', '--source', dest='filename', required=False,
    #   help='Source file to use', metavar='FILE', type=lambda x: is_valid_file(parser,x))
    parser.add_argument('source', nargs='?', default='', type=lambda x: is_valid_file(parser,x))
    parser.add_argument('-d', '--debug', help='Enable debugging', action='store_true', required=False)
    parser.add_argument('-p', '--project', dest='filename', required=False,
        help='Specify a project file to use', metavar='FILE', type=lambda x: is_valid_project(parser,x))

    args = parser.parse_args()

    if args.debug:
        import pdb
        pdb.set_trace()
        Logger('debug is on', getframeinfo(currentframe()), ShowInStatus = True)
    else:
        Logger('debug is off', getframeinfo(currentframe()), ShowInStatus = True)
#------------------------------
#Try to get source file from clipboard
def GetClipBoard():
    try:
        temp = Main.clipboard_get()
        temp = temp.replace('"', '').strip()
        Vars.StatusVar.set(temp)
        if os.path.isfile(temp):
            FileSourceEntry.delete(0, END)
            FileSourceEntry.insert(0, temp)
            Vars.SourceInfoVar.set(FileStat(FileSourceEntry.get()))
            Logger('From clipboard: ' + temp, getframeinfo(currentframe()), ShowInStatus = True)
        else:
            Logger('Invalid path from clipboard: ' + temp, getframeinfo(currentframe()), ShowInStatus = True)
    except:
        Logger('No clipboard data', getframeinfo(currentframe()), ShowInStatus = True)

#------------------------------
#This will either delete a file or move it to trash
def RemoveAFile(File, Trash):
    Logger('Remove a file: ' + File + str(Trash), getframeinfo(currentframe()))
    #if os.access(FileName,os.W_OK)
    if not os.path.exists(File):
        return
    if Trash:
        try:
            send2trash(File)
        except OSError:
            tkinter.messagebox.showerror('Send file to trash error. ' ,File + '\nPermissions?')
    else:
        try:
            os.remove(File)
        except OSError:
            tkinter.messagebox.showerror('Delete a file error. ' ,File + '\nPermissions?')
#------------------------------
#Setup the logger
def SetUpLogger():
    Vars.LogFileNameVar.set(os.path.join(Vars.StartUpDirectoryVar.get(),'PyCopyMoveTk.log'))
    logger = logging.getLogger(Vars.LogFileNameVar.get())
    #logger.setLevel(logging.DEBUG)
    RemoveAFile(Vars.LogFileNameVar.get(), Trash = False)
    #if os.path.exists(Vars.LogFileNameVar.get()): os.remove(Vars.LogFileNameVar.get())
    logger = logging.basicConfig(level=logging.DEBUG,
                filename=Vars.LogFileNameVar.get(),
                format='%(asctime)s %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
#------------------------------

#This class handles file rename for the file info menu
class FileRename:
    RenameEntry = None
    BeforeFilename = ''
    AfterFilename = ''
    Path = ''
    Basename = ''
#------------------------------
    def Swapcase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0,END)
        self.RenameEntry.insert(0,filename.swapcase())
        print('==='+filename)

    def Titlecase(self):
        filename = self.RenameEntry.get()
        def titlecase(s):
            return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
            lambda mo: mo.group(0)[0].upper() +
            mo.group(0)[1:].lower(),s)
        self.RenameEntry.delete(0,END)
        self.RenameEntry.insert(0,titlecase(filename))

    def Uppercase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0,END)
        self.RenameEntry.insert(0,filename.upper())
        self.RenameEntry.focus_set()

    def Lowercase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0,END)
        self.RenameEntry.insert(0,filename.lower())
        self.RenameEntry.focus_set()

    def Capitalize(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0,END)
        self.RenameEntry.insert(0,filename.capitalize())
        self.RenameEntry.focus_set()

    def Done(self): #Filename will always be the same
        self.AfterFilename = os.path.join(self.Path,self.RenameEntry.get())
        Logger('Rename. Before: %s  After: %s' % (self.BeforeFilename, self.AfterFilename), getframeinfo(currentframe()))
        try:
            os.rename(self.BeforeFilename, self.AfterFilename)
        except OSError as e:
            Logger('Rename file error: %s' % e, getframeinfo(currentframe()))
            tkinter.messagebox.showerror('Rename file error',
                'no can do' +
                '\nBefore filename:' + self.BeforeFilename +
                '\nAfter filename:' + self.AfterFilename +
                '\n\nReturn code: %s' % e)
        Vars.FileRenameTopLevelVar.withdraw()

    def Cancel(self):
        Vars.FileRenameTopLevelVar.withdraw()

    def RenameAFile(self):
        Vars.FileRenameTopLevelVar = Toplevel()
        Vars.FileRenameTopLevelVar.title('File rename')
        Vars.FileRenameTopLevelVar.resizable(0,0)
        Vars.FileRenameTopLevelVar.option_add('*Font', 'courier 10')

        Main.update()
        FileRenameTopLevelSizeX = 400
        FileRenameTopLevelSizeY = 100
        Mainsize = Main.geometry().split('+')
        x = int(Mainsize[1]) + FileRenameTopLevelSizeX / 2
        y = int(Mainsize[2]) + FileRenameTopLevelSizeY / 2
        Vars.FileRenameTopLevelVar.geometry("%dx%d+%d+%d" % (FileRenameTopLevelSizeX, FileRenameTopLevelSizeY, x, y))
        Vars.FileRenameTopLevelVar.resizable(1,0)

        FileRenameFrame1 = Frame(Vars.FileRenameTopLevelVar, relief=SUNKEN, bd=1)
        FileRenameFrame1.pack(side=TOP,fill=X)
        FileRenameFrame2 = Frame(Vars.FileRenameTopLevelVar, relief=SUNKEN, bd=1)
        FileRenameFrame2.pack(side=TOP,fill=X)
        FileRenameFrame3 = Frame(Vars.FileRenameTopLevelVar, relief=SUNKEN, bd=1)
        FileRenameFrame3.pack(side=TOP,fill=X)

        #Start here
        self.BeforeFilename = FileSourceEntry.get()
        self.Basename = os.path.basename(self.BeforeFilename)
        self.Path = os.path.dirname(self.BeforeFilename)

        Label(FileRenameFrame1, text=self.BeforeFilename).pack(fill=X)
        self.RenameEntry = Entry(FileRenameFrame1)
        self.RenameEntry.pack(fill=X)
        self.RenameEntry.delete(0,END)
        self.RenameEntry.insert(0,self.Basename)
        self.RenameEntry.focus_set()

        Button(FileRenameFrame2, text='Done', width=8, command=self.Done).pack(side=LEFT)
        Button(FileRenameFrame2, text='Cancel', width=8, command=self.Cancel).pack(side=LEFT)
        Button(FileRenameFrame2, text='Title', width=8, command=self.Titlecase).pack(side=LEFT)

        Button(FileRenameFrame3, text='Upper', width=8, command=self.Uppercase).pack(side=LEFT)
        Button(FileRenameFrame3, text='Lower', width=8, command=self.Lowercase).pack(side=LEFT)
        Button(FileRenameFrame3, text='Swap', width=8, command=self.Swapcase).pack(side=LEFT)
        Button(FileRenameFrame3, text='Capitalize', width=10, command=self.Capitalize).pack(side=LEFT)

#------------------------------
#This function starts a system file such as notepad.exe
# TODO I can not get it to work with name with spaces

def StartFile(filename, trace ,arg1='', arg2='', arg3=''):
    if arg1 == '':
        args = [filename]
    elif arg2 == '':
        args = [filename, arg1]
    elif arg3 == '':
        args = [filename, arg1, arg2]
    else:
        args = [filename, arg1, arg2, arg3]
    Logger('StartFile arguments: ' + str(args), getframeinfo(currentframe()))
    Logger('StartFile trace: ' + str(trace), getframeinfo(currentframe()), ShowInStatus = True)
    ce = None
    print(args)
    try:
        ce = subprocess.call(args)
    except OSError:
        tkinter.messagebox.showerror('StartFile did a Badddddd thing ' , \
         'Arguments: ' + str(args) + '\nReturn code: ' + str(ce))
        return
#------------------------------
#Loads a selected file into the defined system editor
def ShowEditFile(FileName=None):
    if FileName == None:
        FileName = tkFileDialog.askopenfilename(
            defaultextension='.*',
            initialdir=os.path.dirname(os.path.realpath(Vars.AuxDirectory.get())),
            filetypes=[('All files','*.*')],
            title='Show/Edit a file',
            parent=Vars.OptionsTopLevel)

    Logger('Show/Edit file: >>' + FileName + '<<', getframeinfo(currentframe()), ShowInStatus = True)
    FileName = os.path.normpath(FileName)
    try:
        StartFile(Vars.SystemEditorVar.get(), ShowEditFile ,FileName)
    except IOError:
        tkinter.messagebox.showerror('Show/Edit file error', 'Requested file does not exit.\n ' + FileName)
        return
#------------------------------
#Loads a project file
#Lines without a ~ in the line are ignored and may be used as comments
#Lines with # in position 0 may be used as comments
def ProjectLoad(LoadType='none'):
    if LoadType == 'default':
        Vars.ProjectFileNameVar.set(os.path.join(Vars.AuxDirectoryVar.get(), 'PyCopyMoveTk.'+ Vars.ProjectFileExtensionVar.get()))
    else:
        Vars.ProjectFileNameVar.set(tkinter.filedialog.askopenfilename(
            defaultextension = Vars.ProjectFileExtensionVar.get(),
            filetypes = [('Project file','PyCopyMove*.' + Vars.ProjectFileExtensionVar.get()),('All files','*.*')],
            initialdir = Vars.AuxDirectoryVar.get(),
            initialfile = 'PyCopyMoveTk.' + Vars.ProjectFileExtensionVar.get(),
            title = 'Load a PyCopyMoveTk project file',
            parent = Main))
    Vars.ProjectFileNameVar.set(os.path.normpath(Vars.ProjectFileNameVar.get()))

    Logger('Project Load ' + Vars.ProjectFileNameVar.get(), getframeinfo(currentframe()), ShowInStatus = True)

    ProjectEntry.delete(0,END)
    ProjectEntry.insert(0, Vars.ProjectFileNameVar.get())

    title = 'Select a file',
    try:
        f = open(Vars.ProjectFileNameVar.get(), 'r')
    except IOError:
        tkinter.messagebox.showerror('Project file error', 'Requested file does not exist.\n>>' + Vars.ProjectFileNameVar.get() + '<<')
        return

    lines = f.readlines()
    f.close()
    try:
        if not 'PyCopyMoveTk.py project file' in lines[0]:
            tkinter.messagebox.showerror('Project file error', 'Not a valid project file.\nproject file' + '\n' + lines[0] )
            Logger('PyCopyMoveTk.py project file ' + lines[0].strip(), getframeinfo(currentframe()))
            return
    except:
        tkinter.messagebox.showerror('Project file error', 'Unable to read project file' +  Vars.ProjectFileNameVar.get())
        Logger('PyCopyMoveTk.py project file. Unable to read file', getframeinfo(currentframe()))
        return

    del lines[0] # remove the first line so it won't be added to the comments list
    #Clear any widgets that need to be
    FileSourceListbox.delete(0,END)
    Vars.CommentsListVar = []
    for line in lines:
        if '~' in line and line[0] != '#':
            t = line.split('~')
            if 'False' in t[1]:
                t[1] = 0
            elif 'True' in t[1]:
                t[1] = 1

            if 'DestinationEntry01~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry01.delete(0,END)
                DestinationEntry01.insert(0,x)
            if 'DestinationEntry02~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry02.delete(0,END)
                DestinationEntry02.insert(0,x)
            if 'DestinationEntry03~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry03.delete(0,END)
                DestinationEntry03.insert(0,x)
            if 'DestinationEntry04~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry04.delete(0,END)
                DestinationEntry04.insert(0,x)
            if 'DestinationEntry05~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry05.delete(0,END)
                DestinationEntry05.insert(0,x)
            if 'DestinationEntry06~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry06.delete(0,END)
                DestinationEntry06.insert(0,x)
            if 'DestinationEntry07~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry07.delete(0,END)
                DestinationEntry07.insert(0,x)
            if 'DestinationEntry08~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry08.delete(0,END)
                DestinationEntry08.insert(0,x)
            if 'KeepFlagsCheckVar~' in line:
                Vars.KeepFlagsCheckVar.set(int(t[1]))
            if 'AskOnCopyVar~' in line:
                Vars.AskOnCopyVar.set(int(t[1]))
            if 'AskOnMoveVar~' in line:
                Vars.AskOnMoveVar.set(int(t[1]))
            if 'AskOnRecycleVar~' in line:
                Vars.AskOnRecycleVar.set(int(t[1]))
            if 'AskOnDeleteVar~' in line:
                Vars.AskOnDeleteVar.set(int(t[1]))
            if 'AskOnRenameVar~' in line:
                Vars.AskOnRenameVar.set(int(t[1]))
            if 'AskBeforeOverWriteDuringCopyVar~' in line:
                Vars.AskBeforeOverWriteDuringCopyVar.set(int(t[1]))
            if 'AskBeforeOverWriteDuringMoveVar~' in line:
                Vars.AskBeforeOverWriteDuringMoveVar.set(int(t[1]))
            if 'DestinationCheck01Var~' in line:
                Vars.DestinationCheck01Var.set(int(t[1]))
            if 'DestinationCheck02Var~' in line:
                Vars.DestinationCheck02Var.set(int(t[1]))
            if 'DestinationCheck03Var~' in line:
                Vars.DestinationCheck03Var.set(int(t[1]))
            if 'DestinationCheck04Var~' in line:
                Vars.DestinationCheck04Var.set(int(t[1]))
            if 'DestinationCheck05Var~' in line:
                Vars.DestinationCheck05Var.set(int(t[1]))
            if 'DestinationCheck06Var~' in line:
                Vars.DestinationCheck06Var.set(int(t[1]))
            if 'DestinationCheck07Var~' in line:
                Vars.DestinationCheck07Var.set(int(t[1]))
            if 'DestinationCheck08Var~' in line:
                Vars.DestinationCheck08Var.set(int(t[1]))
            if 'SystemEditorVar~' in line and len(t[1]) > 1:
                x = os.path.normpath(t[1].strip())
                Vars.SystemEditorVar.set(x)
            if 'SystemRenamerVar~' in line and len(t[1]) > 1:
                x = os.path.normpath(t[1].strip())
                Vars.SystemRenamerVar.set(x)
            if 'FileSourceEntry~' in line:
                x = os.path.normpath(t[1].strip())
                if x == '.': x = ''
                FileSourceEntry.delete(0,END)
                FileSourceEntry.insert(0,x)
                Vars.SourceInfoVar.set(FileStat(FileSourceEntry.get()))
            if 'SourcesList~' in line:
                FileSourceListbox.insert(END,t[1].strip())
        else:
            Vars.CommentsListVar.append(line)
            #The following are assummed to be comments and are stored as such
            #All lines with # in the first column are comments
            #All line that do not contain ~ are comments

    VerifyPaths('Load')
    Logger('Project opened: ' + Vars.ProjectFileNameVar.get(), getframeinfo(currentframe()), ShowInStatus = True)
#------------------------------
#Saves a project file
def ProjectSave():
    Logger('ProjectSave ' + Vars.ProjectFileNameVar.get(), getframeinfo(currentframe()), ShowInStatus = True)

    if VerifyPaths('Save') != 0:
        if tkinter.messagebox.askyesno('Bad paths detected','Do you want to continue?') == False:
            Logger('Project saved aborted. Bad path detected.', getframeinfo(currentframe()), ShowInStatus = True)
            return

    print(os.path.dirname(Vars.AuxDirectoryVar.get()))
    Vars.ProjectFileNameVar.set(tkinter.filedialog.asksaveasfilename(
        defaultextension = Vars.ProjectFileExtensionVar.get(),
            filetypes = [('Project file','PyCopyMove*.' +
            Vars.ProjectFileExtensionVar.get()),('All files','*.*')],
            initialdir = Vars.AuxDirectoryVar.get(),
            initialfile = 'PyCopyMoveTk.' + Vars.ProjectFileExtensionVar.get(),
            title = 'Save a PyCopyMoveTk project file',
            parent = Main))

    Vars.ProjectFileNameVar.set(os.path.normpath(Vars.ProjectFileNameVar.get()))
    ProjectEntry.delete(0,END)
    ProjectEntry.insert(0, Vars.ProjectFileNameVar.get())

    try:
        f = open(Vars.ProjectFileNameVar.get(), 'w')
    except IOError:
        tkinter.messagebox.showerror('Project file error', 'Unable to open requested file.\n>>' + Vars.ProjectFileNameVar.get() + '<<')

    if not Vars.ProjectFileNameVar.get():
        return

    f.write('PyCopyMoveTk.py project file\n')
    for item in Vars.CommentsListVar:
        f.write(item)
    f.write('DestinationEntry01~' + DestinationEntry01.get().strip() + '\n')
    f.write('DestinationEntry02~' + DestinationEntry02.get().strip() + '\n')
    f.write('DestinationEntry03~' + DestinationEntry03.get().strip() + '\n')
    f.write('DestinationEntry04~' + DestinationEntry04.get().strip() + '\n')
    f.write('DestinationEntry05~' + DestinationEntry05.get().strip() + '\n')
    f.write('DestinationEntry06~' + DestinationEntry06.get().strip() + '\n')
    f.write('DestinationEntry07~' + DestinationEntry07.get().strip() + '\n')
    f.write('DestinationEntry08~' + DestinationEntry08.get().strip() + '\n')
    f.write('KeepFlagsCheckVar~' + str(Vars.KeepFlagsCheckVar.get()) + '\n')
    f.write('AskOnCopyVar~' + str(Vars.AskOnCopyVar.get()) + '\n')
    f.write('AskOnMoveVar~' + str(Vars.AskOnMoveVar.get()) + '\n')
    f.write('AskOnRecycleVar~' + str(Vars.AskOnRecycleVar.get()) + '\n')
    f.write('AskOnDeleteVar~' + str(Vars.AskOnDeleteVar.get()) + '\n')
    f.write('AskOnRenameVar~' + str(Vars.AskOnRenameVar.get()) + '\n')
    f.write('AskBeforeOverWriteDuringCopyVar~' + str(Vars.AskBeforeOverWriteDuringCopyVar.get()) + '\n')
    f.write('AskBeforeOverWriteDuringMoveVar~' + str(Vars.AskBeforeOverWriteDuringMoveVar.get()) + '\n')
    f.write('DestinationCheck01Var~' + str(Vars.DestinationCheck01Var.get()) + '\n')
    f.write('DestinationCheck02Var~' + str(Vars.DestinationCheck02Var.get()) + '\n')
    f.write('DestinationCheck03Var~' + str(Vars.DestinationCheck03Var.get()) + '\n')
    f.write('DestinationCheck04Var~' + str(Vars.DestinationCheck04Var.get()) + '\n')
    f.write('DestinationCheck05Var~' + str(Vars.DestinationCheck05Var.get()) + '\n')
    f.write('DestinationCheck06Var~' + str(Vars.DestinationCheck06Var.get()) + '\n')
    f.write('DestinationCheck07Var~' + str(Vars.DestinationCheck07Var.get()) + '\n')
    f.write('DestinationCheck08Var~' + str(Vars.DestinationCheck08Var.get()) + '\n')
    f.write('SystemEditorVar~' + Vars.SystemEditorVar.get() + '\n')
    f.write('SystemRenamerVar~' + Vars.SystemRenamerVar.get() + '\n')
    f.write('FileSourceEntry~' + FileSourceEntry.get().strip() + '\n')
    for item in FileSourceListbox.get(0,END):
        f.write('SourcesList~' + item + '\n')
    f.close()
    Logger('Project saved: ' + Vars.ProjectFileNameVar.get(), getframeinfo(currentframe()), ShowInStatus = True)
#------------------------------
def sha1file(filename):
    sha1 = hashlib.sha1()
    f = open(filename, 'rb')
    try:
        sha1.update(f.read())
    except:
        Logger('whoops '  + str(exception), getframeinfo(currentframe()),False)
    finally:
        f.close()
    return sha1.hexdigest()
#------------------------------
#Returns statistics on a file
def FileStat(FileName):
    try:
        FileStats = os.stat(FileName)
        Size = 'File size: {:,}'.format(FileStats.st_size)
        Time = '  Modified: %s' % time.ctime(FileStats.st_mtime)
        #CheckSum = crc32file(FileName)
    except:
        Size = 0
        Time = 0
    return Size + Time
#------------------------------
#Allow the user to browse for a file to use as the source file
def BrowseSourceFile():
    filename = tkinter.filedialog.askopenfilename(
    initialdir = os.path.dirname(FileSourceEntry.get()),
    filetypes = [('All files','*.*')],
    title = 'Select a file',
    parent = Main)
    if filename:
        FileSourceEntry.delete(0, END)
        FileSourceEntry.insert(0, os.path.normpath(filename))
        Vars.SourceInfoVar.set(FileStat(FileSourceEntry.get()))
    Logger('Browse source file: ' + filename, getframeinfo(currentframe()), ShowInStatus = True)
#------------------------------
#Allow the user to browse for a destination directory to use
def BrowseDestinationFile(Destination):
    temp = ''
    if Destination == '01': temp = DestinationEntry01.get()
    elif Destination == '02': temp = DestinationEntry02.get()
    elif Destination == '03': temp = DestinationEntry03.get()
    elif Destination == '04': temp = DestinationEntry04.get()
    elif Destination == '05': temp = DestinationEntry05.get()
    elif Destination == '06': temp = DestinationEntry06.get()
    elif Destination == '07': temp = DestinationEntry06.get()
    elif Destination == '08': temp = DestinationEntry08.get()

    if not os.path.isdir(temp):
        tkinter.messagebox.showerror('Destination error', 'Destination directory does not exist.\n' + temp)
        Logger('Destination error. Current destination directory does not exist. ' + temp, getframeinfo(currentframe()))

    DestinationName = tkinter.filedialog.askdirectory(
                        initialdir = temp,
                        parent = Main,
                        title = 'Select a destination directory',
                        mustexist = True)
    Logger('Browse destination file: ' + Destination + '  ' + DestinationName, getframeinfo(currentframe()), ShowInStatus = True)
    if DestinationName:
        DestinationName = os.path.normpath(DestinationName)
        if Destination == '01':
            DestinationEntry01.delete(0, END)
            DestinationEntry01.insert(0,DestinationName)
        elif Destination == '02':
            DestinationEntry02.delete(0, END)
            DestinationEntry02.insert(0,DestinationName)
        elif Destination == '03':
            DestinationEntry03.delete(0, END)
            DestinationEntry03.insert(0,DestinationName)
        elif Destination == '04':
            DestinationEntry04.delete(0, END)
            DestinationEntry04.insert(0,DestinationName)
        elif Destination == '05':
            DestinationEntry05.delete(0, END)
            DestinationEntry05.insert(0,DestinationName)
        elif Destination == '06':
            DestinationEntry06.delete(0, END)
            DestinationEntry06.insert(0,DestinationName)
        elif Destination == '07':
            DestinationEntry07.delete(0, END)
            DestinationEntry07.insert(0,DestinationName)
        elif Destination == '08':
            DestinationEntry08.delete(0, END)
            DestinationEntry08.insert(0,DestinationName)

#------------------------------
#Does the copy or move of the source file to the destination location
def CopyOrMoveActions(Action, Src, Dest):
    Src = Src.strip('\n').replace('\"','') #remove leading and trailing double quotes
    Dest = Dest.strip('\n').replace('\"','') #remove leading and trailing double quotes
    if not os.path.isfile(Src):
        tkinter.messagebox.showerror('Source error', 'Source is not a file or does not exist.\n' + Src)
        Logger(Action + 'Source is not a file or does not exist: ' + Src, getframeinfo(currentframe()), ShowInStatus = True)
        return
    if not os.path.isdir(Dest):
        tkinter.messagebox.showerror('Destination error', 'Destination is not a directory\n' + Dest)
        Logger(Action + 'Destination error. Destination is not a directory: ' + Dest, getframeinfo(currentframe()), ShowInStatus = True)
        return

    if Action == 'Copy':
        if Vars.AskOnCopyVar.get():
            if not tkinter.messagebox.askyesno(Src,
               'Proceed with copy?\nSource: ' + Src + '\nDestination: ' + Dest):
                Logger(Action + ' aborted by user ' + Src + ' ' + Dest, getframeinfo(currentframe()), ShowInStatus = True)
                return

        if Vars.AskBeforeOverWriteDuringCopyVar.get():
            if os.path.isfile(os.path.join(Dest, os.path.split(Src)[1])):
                if not tkinter.messagebox.askyesno('Copy question',
                    Dest + '\nSource file exists in destination.\nOverwrite?\n' + FileStat(os.path.join(Dest,os.path.split(Src)[1]))):
                    Logger('Copy overwite aborted by user. ' + Src + ' ' + Dest, getframeinfo(currentframe()), ShowInStatus = True)
                    return

        try:
            if Vars.KeepFlagsCheckVar.get():
                shutil.copy2(Src, Dest) #Copy without flags
            else:
                shutil.copy(Src, Dest) #Copy with flags
        except shutil.Error as e:
            Logger(Action + ' error. Error: %s' % e, getframeinfo(currentframe()))
            tkinter.messagebox.showerror('Copy error', e)
        except OSError as e:
            Logger(Action + ' error: %s' % e, getframeinfo(currentframe()))
            tkinter.messagebox.showerror('Copy error', e)

    if Action == 'Move':
        if Vars.AskOnMoveVar.get():
            if not tkinter.messagebox.askyesno('Move file',
                'Proceed with move?\nSource: ' + Src + '\nDestination: ' + Dest):
                Logger(Action + ' aborted by user. ' + Src + ' ' + Dest, getframeinfo(currentframe()), ShowInStatus = True)
                return

        DestFileName = os.path.join(Dest, os.path.split(Src)[1])
        if os.path.isfile(DestFileName):
            if Vars.AskBeforeOverWriteDuringMoveVar.get():
                if not tkinter.messagebox.askyesno('Move question',
                    'Source file exists in destination.\nOverwrite?\n' + FileStat(DestFileName)):
                    Logger('Move overwrite aborted. ' + Src + ' ' + Dest, getframeinfo(currentframe()), ShowInStatus = True)
                    return
            Logger('Move overwrite dest file removed. ' + Src + ' ' + DestFileName, getframeinfo(currentframe()), ShowInStatus = True)
            RemoveAFile(os.path.join(Dest, os.path.split(Src)[1]), Trash = True)
            #send2trash(os.path.join(Dest, os.path.split(Src)[1]))

        try:
            shutil.move(Src, Dest)
        except shutil.Error as e:
            Logger(Action + ' error. Error: %s' % e, getframeinfo(currentframe()), ShowInStatus = True)
            tkinter.messagebox.showerror('Move error\n', e)
        except OSError as e:
            Logger(Action + ' error: %s' % e, getframeinfo(currentframe()), ShowInStatus = True)
            tkinter.messagebox.showerror('Move error\n', e)
    Logger(Action + ' Source:' + Src + ' Destination:' + Dest, getframeinfo(currentframe()), ShowInStatus = True)
#------------------------------
#Tests to see where to copy or move the source file to
#Muliple destinations are valid
def CopyOrMove(Action):
    Src = FileSourceEntry.get()
    Logger(Action + ' ' + Src , getframeinfo(currentframe()))
    count = 0

    if Vars.DestinationCheck01Var.get(): CopyOrMoveActions(Action, Src, DestinationEntry01.get()); count+=1
    if Vars.DestinationCheck02Var.get(): CopyOrMoveActions(Action, Src, DestinationEntry02.get()); count+=1
    if Vars.DestinationCheck03Var.get(): CopyOrMoveActions(Action, Src, DestinationEntry03.get()); count+=1
    if Vars.DestinationCheck04Var.get(): CopyOrMoveActions(Action, Src, DestinationEntry04.get()); count+=1
    if Vars.DestinationCheck05Var.get(): CopyOrMoveActions(Action, Src, DestinationEntry05.get()); count+=1
    if Vars.DestinationCheck06Var.get(): CopyOrMoveActions(Action, Src, DestinationEntry06.get()); count+=1
    if Vars.DestinationCheck07Var.get(): CopyOrMoveActions(Action, Src, DestinationEntry07.get()); count+=1
    if Vars.DestinationCheck08Var.get(): CopyOrMoveActions(Action, Src, DestinationEntry08.get()); count+=1

    if count == 0:
        Logger('Copy Or Move. No destinations specified' +  Src, getframeinfo(currentframe()), ShowInStatus = True)
        tkinter.messagebox.showinfo('Copy Or Move', 'No destinations specified\n' + Src)
#------------------------------
#Does the copy or move of the source file to the destination location
def DeleteRecycleRenameInfo(Action):
    Src = FileSourceEntry.get()
    Src = Src.strip('\n').replace('\"','') #remove leading and trailing double quotes
    if not os.path.isfile(Src):
        Logger(Action + ' Source is not a file ' + Src, getframeinfo(currentframe()))
        tkinter.messagebox.showerror('Source error', 'Source is not a file\n' + Src)
        return
    Logger(Action + ' Source: ' + Src, getframeinfo(currentframe()), ShowInStatus = True)

    if Action == 'Recycle':
        if Vars.AskOnRecycleVar.get():
            if not tkinter.messagebox.askyesno('Recycle','Recycle may not work unless drive is local!\n' +
                                   'Proceed with recycle?\nSource: ' + Src):
                Logger(Action + ' file abort by user. ' + Src, getframeinfo(currentframe()), ShowInStatus = True)
                return
        try:
            #send2trash(Src)
            RemoveAFile(Src, Trash = True)
            Logger(Action + ' Source: ' + Src, getframeinfo(currentframe()), ShowInStatus = True)
        except OSError as e:
            Logger(Action + ' file error: %s' % e, getframeinfo(currentframe()))

    if Action == 'Delete':
        if Vars.AskOnDeleteVar.get():
            if not tkinter.messagebox.askyesno('Delete file', 'Proceed with delete?\nSource: ' + Src):
                Logger(Action + ' file abort by user. ' + Src, getframeinfo(currentframe()), ShowInStatus = True)
                return
        try:
            #os.remove(Src)
            RemoveAFile(Src, Trash = False)
            Logger(Action + ' Source: ' + Src, getframeinfo(currentframe()), ShowInStatus = True)
        except OSError as e:
            Logger(Action + ' file error: %s' % e, getframeinfo(currentframe()), ShowInStatus = True)

    if Action == 'Rename':
        FileRenameInstance = FileRename()
        FileRenameInstance.RenameAFile()
        Logger(Action + ' Not done yet ' + Src, getframeinfo(currentframe()), ShowInStatus = True)

    if Action == 'Info': #TODO

        '''
        st_ino
        st_dev
        st_nlink
        st_uid
        st_gid
        st_size
        st_atime
        st_mtime
        st_ctime
        Linux only
        st_blocks
        st_blksize
        st_rdev
        st_flags
        '''

        Logger(Action + ' Not done yet ' + Src, getframeinfo(currentframe()), ShowInStatus = True)
        FileStats = os.stat(FileSourceEntry.get())
        tkinter.messagebox.showinfo('File info',
            'File size: {:,}'.format(FileStats.st_size) + '\n' +
            'Protection bits: %o' % FileStats.st_mode + '\n' +
            'Access: %s' % time.ctime(FileStats.st_atime) + '\n' +
            'Modified: %s' % time.ctime(FileStats.st_mtime) + '\n' +
            'Creation: %s' % time.ctime(FileStats.st_ctime)
        )

#------------------------------
#Fetch the current source file path from the file source list
def SourceListOperations(Operation):

    if not FileSourceListbox.curselection() and (Operation == 'Fetch' or  Operation == 'Remove'):
        Logger('SourceListOperations: No item selected.', getframeinfo(currentframe()), ShowInStatus = True)
        return

    if Operation == 'Fetch':
        FileSourceEntry.delete(0, END)
        FileSourceEntry.insert(0, FileSourceListbox.get(FileSourceListbox.curselection()))
        Vars.SourceInfoVar.set(FileStat(FileSourceEntry.get()))
    elif Operation == 'Remove':
        FileSourceListbox.delete(FileSourceListbox.curselection())
    elif Operation == 'Add':
        if not os.path.isfile(FileSourceEntry.get()): # verify the data is valid
            Logger('FileSourceEntry path is not valid. ' + FileSourceEntry.get(),
                getframeinfo(currentframe()), ShowInStatus = True)
            return
        FileSourceListbox.insert(END, FileSourceEntry.get())

    # fetch the contents of FileSourceListbox
    temp_list = list(FileSourceListbox.get(0, END))

    # remove duplicates
    temp_list = list(set(temp_list))

    # sort the listbox
    temp_list.sort(key=str.lower)

    # delete contents of present listbox
    FileSourceListbox.delete(0, END)

    # load listbox with fixed up data
    for item in temp_list:
        FileSourceListbox.insert(END, item)

    Logger('Source list operations ' + Operation, getframeinfo(currentframe()), ShowInStatus = True)
#------------------------------
#Show any text file using the defined system editor
def ViewEditAnyFile():
    ViewEditName = tkinter.filedialog.askopenfilename(
    initialdir =  Vars.AuxDirectoryVar.get(),
    filetypes = [('All files','*.*')],
    title = 'Select a file',
    parent = Main)

    if ViewEditName:
        Logger('View\Edit any file  ', getframeinfo(currentframe()), ShowInStatus = True)
        StartFile(Vars.SystemEditorVar.get(), 'View\Edit any file' ,os.path.normpath(ViewEditName))
#------------------------------
#Toogle all destinations from selected to un-seleected state
def ToggleDestinations():
    Logger('ToggleDestinations ', getframeinfo(currentframe()))
    Vars.DestinationCheckToggleStateVar.set(not Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck01Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck02Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck03Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck04Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck05Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck06Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck07Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck08Var.set(Vars.DestinationCheckToggleStateVar.get())
    Logger('ToggleDestinations  ' + str(Vars.DestinationCheckToggleStateVar.get()), getframeinfo(currentframe()), ShowInStatus = True)
#------------------------------

#Verify that destinations exist and are writeable
def VerifyPaths(Type=''):
    # Checks if file name exists
    def SearchPath(name):
      path = os.environ['PATH']
      for dir in path.split(os.pathsep):
        binpath = os.path.join(dir, name)
        if os.path.exists(binpath):
          return True
      return False

    Logger('Verifypaths ', getframeinfo(currentframe()))
    Results = ''

    if not SearchPath(Vars.SystemEditorVar.get()):
         Results = 'System editor\n'

    if len(FileSourceEntry.get()) > 0 and not os.path.isfile(FileSourceEntry.get()):
        Results += 'Source\n'
    if not os.path.isdir(DestinationEntry01.get()) or not os.access(DestinationEntry01.get(), os.W_OK):
        Results += 'Destination 1\n'
    if not os.path.isdir(DestinationEntry02.get()) or not os.access(DestinationEntry02.get(), os.W_OK):
        Results += 'Destination 2\n'
    if not os.path.isdir(DestinationEntry03.get()) or not os.access(DestinationEntry03.get(), os.W_OK):
        Results += 'Destination 3\n'
    if not os.path.isdir(DestinationEntry04.get()) or not os.access(DestinationEntry04.get(), os.W_OK):
        Results += 'Destination 4\n'
    if not os.path.isdir(DestinationEntry05.get()) or not os.access(DestinationEntry05.get(), os.W_OK):
        Results += 'Destination 5\n'
    if not os.path.isdir(DestinationEntry06.get()) or not os.access(DestinationEntry06.get(), os.W_OK):
        Results += 'Destination 6\n'
    if not os.path.isdir(DestinationEntry07.get()) or not os.access(DestinationEntry07.get(), os.W_OK):
        Results += 'Destination 7\n'
    if not os.path.isdir(DestinationEntry08.get()) or not os.access(DestinationEntry08.get(), os.W_OK):
        Results += 'Destination 8\n'

    Logger('VerifyPaths  ', getframeinfo(currentframe()), ShowInStatus = True)
    if len(Results) != 0:
        tkinter.messagebox.showerror('Invalid path(s)','Invalid path(s):\n' + Results)
    else:
        if (Type != 'Save' and Type != 'Load'):
            tkinter.messagebox.showinfo('All paths valid','All paths valid!')
    return(len(Results)) #0 is No bad paths
#------------------------------
#Some debug stuff
def About():
    Logger('About ' + main.Vars.StartUpDirectoryVar.get(), getframeinfo(currentframe()), ShowInStatus = True)
    tkinter.messagebox.showinfo('About',  main.Vars.StartUpDirectoryVar.get() +
      '\n' + Main.geometry() +
      '\n' + str(Main.winfo_screenwidth()) + 'x' +  str(Main.winfo_screenheight()) +
      '\n' + 'Python version: ' + platform.python_version() +
      '\n' + platform.platform())
#------------------------------
#The help file (someday)
def Help():
    Logger('Help ' + main.Vars.StartUpDirectoryVar.get(), getframeinfo(currentframe()), ShowInStatus = True)
    Vars.StatusVar.set('Help')

    try:
        f = open(Vars.HelpFileVar.get(), 'r')
    except IOError:
        tkinter.messagebox.showerror('Help file error', 'Requested file does not exist.\n>>' + Vars.HelpFileVar.get() + '<<')
        return
    lines = f.readlines()
    f.close()

    Vars.HelpTopLevelVar = Toplevel()
    Vars.HelpTopLevelVar.title('Help')
    Vars.HelpTopLevelVar.option_add('*Font', 'courier 8')
    Vars.HelpTopLevelVar.withdraw()
    Vars.HelpTopLevelVar.wm_transient(Main)
    Vars.HelpTopLevelVar.deiconify()
    HelpTopLevelX = 550
    HelpTopLevelY = 550

    #This puts the help window in the center of the app ???
    Mainsize = Main.geometry().split('+')
    x = int(Mainsize[1]) + (HelpTopLevelX / 2)

    y = int(Mainsize[2]) + (HelpTopLevelY / 2)

    yScroll = Scrollbar(Vars.HelpTopLevelVar, orient=VERTICAL)
    yScroll.pack(side=RIGHT, fill=Y)
    xScroll = Scrollbar(Vars.HelpTopLevelVar, orient=HORIZONTAL)
    xScroll.pack(side=BOTTOM, fill=X)

    Vars.HelpTopLevelVar.geometry("%dx%d+%d+%d" % (HelpTopLevelX, HelpTopLevelY, x, y))
    Vars.HelpTopLevelVar.resizable(1,1)
    HelpListbox = Listbox(Vars.HelpTopLevelVar, height=3, font='Courier 8' , yscrollcommand=yScroll.set, xscrollcommand=xScroll.set)
    HelpListbox.pack(fill=BOTH, expand=YES)

    yScroll.config(command=HelpListbox.yview)
    xScroll.config(command=HelpListbox.xview)

    for l in lines:
        HelpListbox.insert(END,l.strip())
#------------------------------

#Build all the gui and start the program
menubar = Menu(Main)
Main['menu'] = menubar
ProjectsMenu = Menu(menubar)
SourceMenu = Menu(menubar)
OtherMenu = Menu(menubar)
OptionsMenu = Menu(menubar)

menubar.add_cascade(menu=ProjectsMenu, label='Project')
ProjectsMenu.add_command(label='Load', command=ProjectLoad)
ProjectsMenu.add_command(label='Save', command=ProjectSave)
ProjectsMenu.add_command(label='Edit', command=lambda: ShowEditFile(ProjectEntry.get()))

menubar.add_cascade(menu=SourceMenu, label='Source')
SourceMenu.add_command(label='Browse for source file', command=BrowseSourceFile)
SourceMenu.add_command(label='Add source to list', command=lambda: SourceListOperations('Add'))
SourceMenu.add_command(label='Remove source from list', command=lambda: SourceListOperations('Remove'))
SourceMenu.add_command(label='Fetch source from list', command=lambda: SourceListOperations('Fetch'))

menubar.add_cascade(menu=OtherMenu, label='Other')
OtherMenu.add_command(label='Get Clipboard', command=GetClipBoard)
OtherMenu.add_command(label='View log', command=lambda: StartFile(Vars.SystemEditorVar.get(),'View log' ,Vars.LogFileNameVar.get()))
OtherMenu.add_command(label='ViewEdit any file', command=ViewEditAnyFile)
OtherMenu.add_command(label='About', command=About)
OtherMenu.add_command(label='Help', command=Help)
OtherMenu.add_command(label='Verify paths', command=VerifyPaths)

menubar.add_cascade(menu=OptionsMenu, label='Options')
OptionsMenu.add_checkbutton(label='Keep flags on copy and move', variable=Vars.KeepFlagsCheckVar)
OptionsMenu.add_checkbutton(label='Ask on copy', variable=Vars.AskOnCopyVar)
OptionsMenu.add_checkbutton(label='Ask on move', variable=Vars.AskOnMoveVar)
OptionsMenu.add_checkbutton(label='Ask on recyle', variable=Vars.AskOnRecycleVar)
OptionsMenu.add_checkbutton(label='Ask on delete', variable=Vars.AskOnDeleteVar)
OptionsMenu.add_checkbutton(label='Ask on rename', variable=Vars.AskOnRenameVar)
OptionsMenu.add_checkbutton(label='Ask before overwrite during copy', variable=Vars.AskBeforeOverWriteDuringCopyVar)
OptionsMenu.add_checkbutton(label='Ask before overwrite during move', variable=Vars.AskBeforeOverWriteDuringMoveVar)
#---------------
FileFrame1 = Frame(Main, relief=SUNKEN, bd=1)
FileFrame1.pack(fill=X, side=TOP)
Label(FileFrame1, text='Source file',font=("Helvetica", 15)).pack(side=TOP, fill=BOTH, expand=YES)

BrowseSourceButon = Button(FileFrame1, text='Browse', command=BrowseSourceFile, width=8)
BrowseSourceButon.pack(side=LEFT)
ToolTip(BrowseSourceButon,'Browse for a source file path')
FileSourceEntry = Entry(FileFrame1, relief=SUNKEN ,bd=2)
FileSourceEntry.pack(fill=X)
ToolTip(FileSourceEntry,'Path for the source file')

SourceInfoLabel = Label(FileFrame1, textvariable=Vars.SourceInfoVar, bd=1)
SourceInfoLabel .pack(side=TOP, fill=BOTH, expand=YES)
ToolTip(SourceInfoLabel ,'Source stats')

#---------------
FileFrame2 = Frame(Main, relief=SUNKEN, bd=1)
FileFrame2.pack(side=TOP, fill=BOTH, expand=YES)

FileFrame3 = Frame(FileFrame2, relief=SUNKEN, bd=1, width=10)
FileFrame3.pack(side=LEFT)
ToolTip(FileFrame3,'Operations to the source list')

Button(FileFrame3, text='Add', width=8,
    command=lambda: SourceListOperations('Add')).pack(side=TOP, fill=BOTH, expand=YES)
Button(FileFrame3, text='Fetch', width=8,
    command=lambda: SourceListOperations('Fetch')).pack(side=TOP, fill=BOTH, expand=YES)
Button(FileFrame3, text='Remove', width=8,
    command=lambda: SourceListOperations('Remove')).pack(side=TOP, fill=BOTH, expand=YES)

FileFrame4 = Frame(FileFrame2, relief=SUNKEN, bd=1)
FileFrame4.pack(side=LEFT, fill=X, expand=YES)

yScroll = Scrollbar(FileFrame4, orient=VERTICAL)
yScroll.pack(side=RIGHT, fill=Y)
xScroll = Scrollbar(FileFrame4, orient=HORIZONTAL)
xScroll.pack(side=BOTTOM, fill=X)
FileSourceListbox = Listbox(FileFrame4, height=3, yscrollcommand=yScroll.set, xscrollcommand=xScroll.set)
FileSourceListbox.pack(fill=BOTH, expand=YES)

FileSourceListbox.bind('<Double-Button-1>', lambda x: SourceListOperations('Fetch') )
ToolTip(FileSourceListbox,'Saved list of source files. Double left click to fetch.')
yScroll.config(command=FileSourceListbox.yview)
xScroll.config(command=FileSourceListbox.xview)

OperationFrame = Frame(Main, relief=SUNKEN, bd=1)
OperationFrame.pack(side=TOP, fill=X, expand=YES)
ToolTip(OperationFrame,'Click a button to perform action')
Label(OperationFrame, text='Operations',font=("Helvetica", 15)).pack(side=TOP, fill=BOTH, expand=YES)

Button(OperationFrame, width=10, text='Copy',command=lambda: CopyOrMove('Copy')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Move',command=lambda: CopyOrMove('Move')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Recycle',command=lambda: DeleteRecycleRenameInfo('Recycle')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Delete',command=lambda: DeleteRecycleRenameInfo('Delete')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Rename',command=lambda: DeleteRecycleRenameInfo('Rename')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Info',command=lambda: DeleteRecycleRenameInfo('Info')).pack(side=LEFT)
#------------------------------
DestinationFrame = Frame(Main, relief=SUNKEN, bd=1)
DestinationFrame.pack(fill=X)
ToolTip(DestinationFrame,'Chose/add a destination path')
Label(DestinationFrame, text='Destination directories',font=("Helvetica", 15)).pack(side=TOP, fill=BOTH, expand=YES)

ToggleAllButton = Button(DestinationFrame, width=15, text='Toggle all',command=ToggleDestinations)
ToggleAllButton.pack()
ToolTip(ToggleAllButton,'Toggle all destination selects')

DestinationFrame01 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame01.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame01, text='Dest1', variable=Vars.DestinationCheck01Var).pack(side=LEFT)
Button(DestinationFrame01, text='Browse', command=lambda: BrowseDestinationFile('01')).pack(side=LEFT)
DestinationEntry01 = Entry(DestinationFrame01)
DestinationEntry01.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame02 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame02.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame02, text='Dest2', variable=Vars.DestinationCheck02Var).pack(side=LEFT)
Button(DestinationFrame02, text='Browse', command=lambda: BrowseDestinationFile('02')).pack(side=LEFT)
DestinationEntry02 = Entry(DestinationFrame02)
DestinationEntry02.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame03 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame03.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame03, text='Dest3', variable=Vars.DestinationCheck03Var).pack(side=LEFT)
Button(DestinationFrame03, text='Browse', command=lambda: BrowseDestinationFile('03')).pack(side=LEFT)
DestinationEntry03 = Entry(DestinationFrame03)
DestinationEntry03.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame04 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame04.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame04, text='Dest4', variable=Vars.DestinationCheck04Var).pack(side=LEFT)
Button(DestinationFrame04, text='Browse', command=lambda: BrowseDestinationFile('04')).pack(side=LEFT)
DestinationEntry04 = Entry(DestinationFrame04)
DestinationEntry04.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame05 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame05.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame05, text='Dest5', variable=Vars.DestinationCheck05Var).pack(side=LEFT)
Button(DestinationFrame05, text='Browse', command=lambda: BrowseDestinationFile('05')).pack(side=LEFT)
DestinationEntry05 = Entry(DestinationFrame05)
DestinationEntry05.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame06 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame06.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame06, text='Dest6', variable=Vars.DestinationCheck06Var).pack(side=LEFT)
Button(DestinationFrame06, text='Browse', command=lambda: BrowseDestinationFile('06')).pack(side=LEFT)
DestinationEntry06 = Entry(DestinationFrame06)
DestinationEntry06.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame07 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame07.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame07, text='Dest7', variable=Vars.DestinationCheck07Var).pack(side=LEFT)
Button(DestinationFrame07, text='Browse', command=lambda: BrowseDestinationFile('07')).pack(side=LEFT)
DestinationEntry07 = Entry(DestinationFrame07)
DestinationEntry07.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame08 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame08.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame08, text='Dest8', variable=Vars.DestinationCheck08Var).pack(side=LEFT)
Button(DestinationFrame08, text='Browse', command=lambda: BrowseDestinationFile('08')).pack(side=LEFT)
DestinationEntry08 = Entry(DestinationFrame08)
DestinationEntry08.pack(side=LEFT, fill=X, expand=TRUE)

#------------------------------
StatusFrame = Frame(Main, relief=SUNKEN, bd=1)
StatusFrame.pack(fill=X)
Label(StatusFrame, text='Status',font=("Helvetica", 15)).pack(side=TOP, fill=BOTH, expand=YES)
Statuslabel = Label(StatusFrame, textvariable=Vars.StatusVar, relief=GROOVE)
Statuslabel.pack(side=TOP, expand=TRUE, fill=X)
ToolTip(Statuslabel,'Display status')
ProjectEntry = Entry(StatusFrame)
ProjectEntry.pack(side=TOP, expand=TRUE, fill=X)
ToolTip(ProjectEntry,'Currently loaded project')
#------------------------------
ParseCommandLine()
SetDefaults() #Initialize the variables
StartUpStuff()
#------------------------------
Vars.LogFileNameVar.set(os.path.join(Vars.StartUpDirectoryVar.get(),'PyCopyMoveTk.log'))
#if os.path.exists(Vars.LogFileNameVar.get()): os.remove(Vars.LogFileNameVar.get())
MyLogger = logging.getLogger(Vars.LogFileNameVar.get())

MyLogger = logging.basicConfig(level=logging.DEBUG,
        filename=Vars.LogFileNameVar.get(),
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
#------------------------------
Main.bind('<F1>', lambda e:Help())
Main.bind('<F2>', lambda e:About())
Main.bind('<F3>', lambda e:BrowseSourceFile())
Main.bind('<F4>', lambda e:ProjectLoad())

Vars.StatusVar.set('Waiting')
Main.minsize(400,300)
Main.resizable(1,0)
Main.option_add('*Font', 'courier 10')
Main.title('PyCopyMoveTk')
Main.wm_iconname('PyCopyMoveTk')
Main.mainloop()
