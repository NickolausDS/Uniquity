##VERSION 0.4.2-alpha

Added features

* Added nicer filename formatting
* Scans now auto-sort files based on size

Fixed

* Fix bug with "flicker effect" when selecting files during large scans
* Various stability bugs

##VERSION 0.4.1-alpha

Added features

* Added support for preserving selections after updates


##VERSION 0.4.0-alpha

Added features

* New layout for duplicate files!
	* This layout is much faster, and doesn't bog down on large scans
	* Added color-coding between differing files
* New layout for update panel

Fixed

* Large scans no longer slow down
* Update panel displaying oddly with long filenames
* Various other small bugs


##VERSION 0.3.0-alpha

Added features

* Added concurrency, meaning large scans no longer tie up the GUI
* Optimized the scanner by a magnitude of 10 at least. Scans are MUCH faster, and
large scans are now possible
* Verified files now show up immediately when they are found.
* The progress indicator now shows the amount of files scanned, as well as the amount of bytes


Fixed

* Bug with scanning files with special characters in their filenames
* Refactored lots of model code, making future updates and add-ons faster to develop
	* In fact, I don't think any original model code exists
* Bug when special files were scanned, such as sockets and links

Changed

* Disabled the Progress bar for now, since the scanner is now too fast for it to make any sense.
* Disabled the 'skipped file output' until proper logging is established



##VERSION 0.2.0-alpha

Added features!

* DragAndDrop now works! Drag any file into Uniquity to scan it!
* Menu highlighting has been added! Buttons will highlight when they can be used, and will grey out when they can't.
* Duplicate file sizes are now shown!
	* Also added subjective description to sizes for non-technical users
* Progress updates are now shown. No more wondering what Uniqutiy is doing in the background!
	* Only partial names shown in progress bar to avoid clutter

Fixed

* Bug with progress updater not showing the latest file being scanned



##VERSION 0.1.1-pre-alpha

Refactored some code, made slight improvements

* Fixed Bug with opening file in Mac's Finder
* The delete button now prompts the user before deleting files
* Refactored some backend code

##VERSION 0.1.0-pre-alpha

The first version of Uniquity has been released! Hopefully this is the beginning of a beautiful new program!
