
##Version .3 The Pretty Looking Update deadline Sep 16th (Monday)

###Critical Features -- 



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

##Version .4

###Critical Features -- 

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



##Future Features

* Save and load a hash list of file directories
* Pause button
* Handle double click events when selected dir
