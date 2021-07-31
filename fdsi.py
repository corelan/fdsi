#!/usr/bin/env python3
# simple python script to detect & report possible issues that may prevent Dropbox from syncing correctly
# Checks are performed based on the list of "bad characters", file path length limitations, and other criteria as documented here:
# https://help.dropbox.com/files-folders/sort-preview/file-names  


import os, sys, getopt
requirelist = []
try:
    import pathlib
except:
    requirelist.append("Python 3")
    pass

if len(requirelist) > 0:
    print("Oops, we ran into some issues. This script requires the following:")
    for item in requirelist:
        print("- %s" % item)
    sys.exit(2)


global showverbose
global pathlength
global allEntries

class CEntry:

    def __init__(self):
        # type 0 = folder
        # type 1 = file
        self.type = 0           
        self.typename = "Folder"
        self.filename = ""
        self.foldername = ""
        self.fullpath = ""
        self.pathlength = 0
        self.badchars = []
        self.issuelist = []

    def addEntry(self, entryname, parentfolder, entrytype):
        self.entryname = entryname
        self.parentfolder = parentfolder
        self.type = entrytype
        self.fullpath = os.path.join(self.entryname, self.parentfolder)
        self.pathlength = len(self.fullpath)
        self.badchars = getBadChars(self.entryname, entrytype)
        # Folder
        if entrytype == 0:
            self.typename = "Folder"
        # File
        if entrytype == 1:
            self.typename = "File"

        if len(self.badchars) > 0:
            badcharlist = " ".join(self.badchars)
            self.issuelist.append( "%s contains the following restricted characters: %s" % (self.typename, badcharlist) )
        if entrytype == 0 and entryname.endswith(" "):
            self.issuelist.append( "%s ends with a space" % (self.typename) )
        if self.pathlength > pathlength:
            self.issuelist.append( "%s is longer than %d characters (%d to be specific)" % (self.typename, pathlength, self.pathlength))


def getBadChars(thisentry, entrytype):
    badlist = ["/", "\\", "<", ">", ":", '"', "|", "?", "*"]
    #if entrytype == 0:
    #    badlist.append(".")
    itemsfound = []
    for baditem in badlist:
        if baditem in thisentry:
            itemsfound.append(baditem)
    return itemsfound

def showBanner():
    bannertxt = """
       __    _     _ 
      / _|  | |   (_)
     | |_ __| |___ _ 
     |  _/ _` / __| |
     | || (_| \__ \ |
     |_| \__,_|___/_|
 
    fdsi.py - Find Dropbox Sync Issues
    https://github.com/corelan/fdsi

 """
    print(bannertxt)
    return

def showsyntax():
    global pathlength
    print("")
    print("Usage: python3 '%s' <optional argument(s)>\n" % pathlib.Path(__file__))
    print("Optional arguments:")
    print("\t-p <path>\tSet startfolder to path. Default = current folder")
    print("\t-v \t\tShow additional verbose information")
    print("\t-l <number>\tSet maximum file path length. Default: %d" % pathlength)
    print("")


def processFolder(folderpath):
    global allEntries
    global showverbose
    
    pathobj = pathlib.Path(folderpath)
    parentname = pathobj.parent.absolute()
    foldername = os.path.basename(folderpath)

    if showverbose:
        print("   [+] Processing folder '%s' in '%s'" % (foldername, parentname))

    cfolder = CEntry()
    cfolder.addEntry(foldername, parentname, 0)
    allEntries.append(cfolder)
    subfolders = []
    localfiles = []
    nrfiles = 0
    
    itemlist = os.scandir(folderpath)
    for direntry in itemlist:
        if direntry.is_dir():
            subfolders.append(os.path.join(folderpath, direntry.name))
        elif direntry.is_file():
            cfile = CEntry()
            cfile.addEntry(direntry.name, folderpath, 1)
            allEntries.append(cfile)
            nrfiles += 1

    if showverbose:
        print("      Folder contains %d subfolders and %d files" % (len(subfolders), nrfiles))

    if len(subfolders) > 0:
        for subfolder in subfolders:
            processFolder(subfolder)


def getIssues():
    global allEntries
    global pathlength
    issuecnt = 0
    print("\n   [+] Analysis results:")
    
    for thisentry in allEntries:
        if len(thisentry.issuelist) > 0:
            print("      %s '%s' requires fixing the following issue(s):" %  (thisentry.typename, thisentry.fullpath))
            issuecnt += 1
            for thisissue in thisentry.issuelist:
                print("      > %s" % thisissue)
    print ("\n   [+] Done. A total of %d entries found with issues" % issuecnt)
    return



def main(argv):

    showBanner()
    global showverbose
    global pathlength
    global allEntries

    showverbose = False
    pathlength = 260
    allEntries = []

    startfolder = os.getcwd()

    # check command arguments
    try:
        opts, argv = getopt.getopt(sys.argv[1:], "h:p:v:l:")
    except getopt.GetoptError:
      showsyntax()
      sys.exit(2)

    for opt, v in opts:
        if opt == "-h":
            showsyntax()
            sys.exit(0)
        elif opt == "-v":
            showverbose = True
        elif opt in ("-p"):
            startfolder = v
        elif opt == "-l":
            try:
                pathlength = int(v)
            except Exception as e:
                print("   *** Invalid length, reset to 260 *** ")
                pathlength = 260

    print("\n   [+] Working folder: '%s'\n" % startfolder)
    if os.path.isabs(startfolder):
        processFolder(startfolder)
        getIssues()
    else:
        print("   *** %s is not an absolute path. Please provide a full path instead of a relative path ***" % startfolder)

if __name__ == "__main__":
    main(sys.argv[1:])
