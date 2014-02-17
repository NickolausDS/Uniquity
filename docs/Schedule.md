

##Version 0.2.0

The intention for this release is UI usability. This program should be predictable, and we should never have users confused when the program first starts up.

###Critical Tasks

* Make sure 'View' button works (done)
* Make sure 'Delete' button works (done)

###Tasks

* (done) Grey out (or make visually less provocative) menu buttons that can't be used.
	* Such as the view and delete buttons on startup. 
* (done) Drag-and-drop
	* Users expect this to be a thing!
* (done[ish]) Sort and display duplicate files by size
	* Free-ing up HD space is a big reason people use this program
* Shorten filenames to only what we're interested in
	* Showing full path names is cryptic, and dirties the User Interface
	* Only show what we want to see
* (done)Create a progress indicator, so the user knows how long it will take
	

###Useful Features

##Version 0.1.0

###Features



* Fully resizable Windows (done!)
* Redo the toolbar 
	* new button (done!)
	* add button (done!)
	* simple remove -- remove to-be-scanned folders (done!)
	* open dup file button (done for mac)
	* delete dup file button (done!)
		* undo delete (pushed back)
		* redo delete (pushed back)
	* Add color to status bar
		* Add green color to directory listing files that have finished (pushed back)
		* Add green color to status bar when finished (pushed back)
		* Add red whenever there is an error 
	* Add file menu (menu at top of application).
		* File
			* New
			* Add 
			* Quit
		* Edit
			* Paste
		* View
			* (checkbox) hash
		* Help
			* (quick guide) coming soon, don't implement
		* About 
			* done by windward produictions

####Drag and drop doesn't yet work in wxpython, so these won't be implemented yet.
* selectable dirs
* Drag and drop

###Hopeful features

* Limit Filesize
* Choose hash

###Future Features
* Add a gauge to the bottom of the screen for the user
* Separate threading
	* Scanning files needs to be done in a separate thread
	* Progress updating needs to be done in a separate thread
* Queueing new folders
	* Removing folders from queue
* Add color to status bar
	* Add green color to directory listing files that have finished
	* Add green color to status bar when finished
	* Add red whenever there is an error
* Add 

* Save and load a hash list of file directories
* Pause button
* Handle double click events when selected dir

