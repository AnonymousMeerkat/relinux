Tutorial for module developers
==============================

## How relinux is setup ##
Relinux is split up into utilities and modules. Utilities are libraries that the modules use, and modules are
the parts that make up the relinux toolkit (OSWeaver being the main one).

## Tree and basic function of each file ##

	src
	├── __init__.py
	└── relinux
	    ├── config.py             Application configuration
	    ├── configutils.py        Utilities for parsing relinux.conf
	    ├── fsutil.py             Utilities to manage the system
	    ├── gui.py                Everything GUI-related
	    ├── __init__.py
	    ├── localization.py       Designed to ease usage of gettext, but might be deprecated soon
	    ├── logger.py             Logging utilities
	    ├── __main__.py           Runs relinux
	    ├── modloader.py          Module loader
	    ├── modules
	    │   ├── __init__.py
	    │   └── osweaver          OSWeaver Module
	    │       ├── __init__.py   Module information
	    │       ├── isoutil.py    Generates the ISO structure
	    │       ├── squashfs.py   Generates the SquashFS
	    │       └── tempsys.py    Generates the temporary system (that SquashFS will use)
	    ├── pwdmanip.py           Utilities for parsing /etc/passwd, /etc/g{roup|shadow}, and /etc/shadow
	    ├── test                  Temporary file to use awk/sed with :P
	    ├── threadmanager.py      Manages threads
	    └── versionsort.py        Contains a version sorting class (but will be moved to configutils)

## Creating a module ##
Modules are relatively easy to make. A basic module structure looks like this:

	modulename
	└── __init__.py

The `__init__.py` file does all the work in the module. Here is an example of one:

	'''
	Random Module
	@author: Anonymous
	'''
	
	relinuxmodule = True
	
	def run(adict):
		# Do something here

Note the relinuxmodule variable. Without that variable set to true, relinux will not detect the module.
The run function is called with a dictionary as soon as the module is loaded. The dictionary contains
pointers to objects that relinux uses (see next section for an example of one). 

## Making a GUI ##
As mentioned previously, the run function contains a dictionary that contains pointers to objects.
One of these is the GUI object, which allows you to change the GUI in any way you like, for example:

	def run(adict):
		gui = adict["gui"]
		pagenum = gui.wizard.add_tab()
		gui.mypage = tkinter.Label(gui.wizard.page_container(pagenum), text="My Page")
		gui.wizard.add_page_body(pagenum, "Page", gui.mypage)

This would create a page with the title of "Page", and the text inside would be "My Page"

## Using the libraries ##
This section will show a basic overview of the libraries given in relinux. To learn more information,
open up the files yourself!

### configutils ###
The configutils library contains various utilities to manage the configuration file.
The main usage is to convert the human-readable configuration file to a dictionary of dictionaries of
dictionaries. An example is show below:

Configuration file:

	Section MySection
		Option MyOption
			Value: MyValue
		EndOption
	EndSection

Parsed:

	{
		"MySection": {
			"MyOption": {
				"Value": "MyValue"
			}
		}
	}

Code:

	buffer = configutils.parseCompressedBuffer(configutils.compress(configutils.getBuffer(open(file))))

Note that relinux already parses it, and it is passed to each module by the "config" item

### fsutil ###
fsutil contains various utilities to manage the filesystem. Though there are many functions listed there,
this document will only cover one, ife.
IFE was created so that one could edit a file without worrying about losing stat information. It works in a
very similar fashion to the `awk` unix utility, but the editing is made to imitate `sed`'s `-i` flag.
Here is code that will add line numbers to a document:

	buffers = fsutil.ife_getbuffers("path/to/document")
	lineno = 0
	def _helper(line):
		global lineno
		returnme = [True, (str(lineno) + " " + line)]
		lineno = lineno + 1
		return returnme
	fsutil.ife(buffers, _helper)

### gui ###
Not exactly a library (more like a module), but very useful to check out the source if you are going to
build a GUI component

### logger ###
Logs information into four categores: Error, Information, Verbose, and Very-Verbose.
Sample usage;

	threadname = "MyThread"
	tn = logger.genTN(threadname)
	logger.logI(tn, "Message from " + threadname)

### pwdmanip ###
Various utilities for `/etc/passwd`, `/etc/group`, `/etc/gshadow` and `/etc/shadow`

### threadmanager ###
Manages threads. Example of usage:

	mythread = {"deps": [], "tn": "MyThread"}
	class MyThread(threading.Thread):
		def run(self):
			# Do something here
	mythread["thread"] = MyThread
	mysecondthread = {"deps": [mythread], "tn": "MySecondThread"}
	class MySecondThread(threading.Thread):
		def run(self):
			# Do something here
	mysecondthread["thread"] = MySecondThread
	threads = [mythread, mysecondthread]
	threadmanager.threadLoop(threads)

The code above would run `mysecondthread` after `mythread`. The `deps` system is very useful when many
threads require one thread to run. For example, here could be a tree of threads that need to be run:

		   1
		   |
		  / \
	     2   3
	    /   / \
	   4   5   6
	   \   |   /
	    \  |  /
	     \ | /
	      \|/  
	       7

Code:

	T1["deps"] = []
	T2["deps"] = T3["deps"] = [T1]
	T4["deps"] = [T2]
	T5["deps"] = T6["deps"] = [T3]
	T7["deps"] = [T4, T5, T6]
