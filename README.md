# fdsi
Find/Fix Dropbox Sync Issues - find issues with files/folders that may prevent Dropbox from syncing correctly 

According to Dropbox' documentation (https://help.dropbox.com/files-folders/sort-preview/file-names), certain conditions may prevent Dropbox from syncing files/folders correctly.
This script will attempt to discover
* invalid characters
* long file paths
* space at end of filename, before the extension

# Usage

Run `python3 fdsi.py`

By default, the script will process the current (working) directory.

# Arguments

`-p <path>`     Specify the starting folder. fdsi will process this folder and all subfolders
`-l <number>`   Specify the maximum path length. Set to 260 by default.
`-h`            Show the help

