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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\u001b[34m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\u001b[31m'
    GREEN = '\u001b[32m'
    BLACK  = '\33[30m'
    WHITE  = '\33[37m'
    VIOLET = '\33[35m'
    ORANGE = '\033[33m'
    LIGHTRED = '\033[91m'
    LIGHTGREEN = '\033[92m'
    LIGHTGREY = '\033[37m'
    BG_BLACK  = '\33[40m'
    BG_RED    = '\33[41m'
    BG_GREEN  = '\33[42m'
    BG_YELLOW = '\33[43m'
    BG_BLUE   = '\33[44m'
    BG_VIOLET = '\33[45m'
    BG_BEIGE  = '\33[46m'
    BG_WHITE  = '\33[47m'


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
        self.fullpath = os.path.join(self.parentfolder, self.entryname)
        self.pathlength = len(self.fullpath)
        self.badchars = getBadChars(self.entryname, entrytype)
        self.nonasciichars = getNonAsciiChars(self.entryname, entrytype)
        # Folder
        if entrytype == 0:
            self.typename = "Folder"
        # File
        if entrytype == 1:
            self.typename = "File"

        if len(self.badchars) > 0:
            badcharlist = " ".join(self.badchars)
            self.issuelist.append(f"{bcolors.RED}%s contains the following restricted characters: %s{bcolors.ENDC}" % (self.typename, badcharlist) )
            self.issuelist.append( "Full path:")
            self.issuelist.append( "%s" % self.fullpath)

        if len(self.nonasciichars) > 0:
            nonasciilist = " ".join(self.nonasciichars)
            self.issuelist.append(f"{bcolors.RED}%s contains the following non-ascii characters: %s{bcolors.ENDC}" % (self.typename, nonasciilist) )
            self.issuelist.append( "Full path:")
            self.issuelist.append( "%s" % self.fullpath)

        if entrytype == 0 and self.entryname.endswith(" "):
            self.issuelist.append(f"{bcolors.RED}%s %s ends with a space{bcolors.ENDC}" % (self.typename, self.entryname) )
            self.issuelist.append( "Full path:")
            self.issuelist.append( "%s" % self.fullpath)

        if entrytype == 1:
            fileparts = os.path.splitext(self.entryname)
            if len(fileparts) > 0:
                filename = fileparts[0]
                if filename.endswith(" "):
                    self.issuelist.append("%s %s has a space at the end of the file name, before the extension" % (self.typename, self.entryname))
                    self.issuelist.append( "Full path:")
                    self.issuelist.append( "%s" % self.fullpath)

        if self.pathlength > pathlength:
            prefixtxt = ""
            if entrytype == 1:
                prefixtxt = "Full path to"
            self.issuelist.append( "%s %s is longer than %d characters (%d to be specific)" % (prefixtxt, self.typename, pathlength, self.pathlength))
            self.issuelist.append( "Full path:")
            self.issuelist.append( "%s" % self.fullpath)


def cleanfilename(filename, folderlocation):
    origfile = filename
    newfile = origfile.strip()

    replacelist = {}
    replacelist["а"] = "a"
    replacelist["–"] = "-"
    replacelist["’"] = "'"
    replacelist["ґ"] = "r"
    replacelist["…"] = "..."
    replacelist["İ"] = "I"
    replacelist["—"] = "-"
    replacelist["Ѕ"] = "S"

    for replacechar in replacelist:
        newfile = newfile.replace(replacechar, replacelist[replacechar])


    # remove space before extension
    fileparts = os.path.splitext(newfile)
    if len(fileparts) > 1:
        filename_before_ext = fileparts[0]
        if filename_before_ext.endswith(" "):
            newfile = filename_before_ext.strip(" ") + fileparts[1]

    if newfile != origfile:
            try:
                os.rename(os.path.join(folderlocation, origfile), os.path.join(folderlocation, newfile))
                #print(f"  Renaming file %s to %s" % (origfile, newfile))
            except Exception as e:
                print(f"     {bcolors.RED}*** Unable to rename file '%s': %s{bcolors.ENDC}" % (os.path.join(folderlocation, origfile), str(e)))




    return


def getBadChars(thisentry, entrytype):
    badlist = ["/", "\\", "<", ">", ":", '"', "|", "?", "*"]

    #if entrytype == 0:
    #    badlist.append(".")
    itemsfound = []
    for baditem in badlist:
        if baditem in thisentry:
            itemsfound.append(baditem)
    return itemsfound

def getNonAsciiChars(thisentry, entrytype):
    nonasciichars = []
    asciichars = " 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,+-_'&()[]{}!#@óüüáéàçè;"
    asciiarr = list(asciichars)
    entryarr = list(thisentry)
    for entrychar in entryarr:
        if not entrychar in asciichars:
            if not entrychar in nonasciichars:
                nonasciichars.append(entrychar)
    return nonasciichars


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
    print("\t-p <path>\tSet startfolder to path. Default = current folder.")
    print("\t-l <number>\tSet maximum file path length. Default: %d" % pathlength)
    print("\t-v \t\tShow additional verbose information.")
    print("\t-h \t\tShow this help message.")
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
    if showverbose:
        print("        > Added folder '%s'" % foldername)
    allEntries.append(cfolder)
    subfolders = []
    localfiles = []
    nrfiles = 0

    # first, sanitize filenames to avoid obvious issues

    itemlist = os.scandir(folderpath)
    for direntry in itemlist:
        if direntry.is_file():
            cleanfilename(direntry.name, folderpath)
    
    itemlist = sorted(os.scandir(folderpath), key=lambda e: e.name)

    for direntry in itemlist:
        if direntry.is_dir():
            subfolders.append(os.path.join(folderpath, direntry.name))
        elif direntry.is_file():
            cfile = CEntry()
            cfile.addEntry(direntry.name, folderpath, 1)
            allEntries.append(cfile)
            if showverbose:
                print("        > Processed file %s" % cfile.fullpath)
            nrfiles += 1

    if showverbose:
        print("       Folder contains %d subfolders and %d files" % (len(subfolders), nrfiles))

    if len(subfolders) > 0:
        subfolders.sort()
        for subfolder in subfolders:
            processFolder(subfolder)


def getIssues():
    global allEntries
    global pathlength
    issuecnt = 0
    print("\n   [+] Analysis results:")
    
    for thisentry in allEntries:
        if len(thisentry.issuelist) > 0:
            if thisentry.type == 0: # Folder
                entryname = thisentry.fullpath
            if thisentry.type == 1: # File
                entryname = thisentry.entryname
            print("\n       %s '%s' requires fixing the following issue(s):" %  (thisentry.typename, entryname))
            issuecnt += 1
            for thisissue in thisentry.issuelist:
                print("       > %s" % thisissue)
    print ("\n   [+] Done. A total of %d entries found with issues.\n" % issuecnt)
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
        opts, argv = getopt.getopt(sys.argv[1:], "p:l:hv")
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

    print("\n")
    if showverbose:
        print("   [+] Verbose mode active.")
    print("   [+] Working folder: '%s'\n" % startfolder)
    if os.path.isabs(startfolder):
        processFolder(startfolder)
        getIssues()
    else:
        print("   *** %s is not an absolute path. Please provide a full path instead of a relative path ***" % startfolder)

if __name__ == "__main__":
    main(sys.argv[1:])
