'''
OSWeaver Module for relinux
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import threadmanager, config, gui, configutils
import Tkinter

relinuxmodule = True
relinuxmoduleapi = "0.4a1"
modulename = "OSWeaver"

# Just in case config.ISOTree doesn't include a /
isotreel = config.ISOTree + "/"
tmpsys = config.TempSys + "/"
configs = {}
aptcache = {}
page = {}


def runThreads():
    from relinux.modules.osweaver import isoutil, squashfs, tempsys
    threads = []
    threads.extend(isoutil.threads)
    threads.extend(squashfs.threads)
    threads.extend(tempsys.threads)
    threadmanager.threadLoop(threads)


def run(adict):
    global configs, aptcache, page, isotreel, tmpsys
    configs = adict["config"]["OSWeaver"]
    isodir = configutils.getValue(configs[configutils.isodir])
    config.ISOTree = isodir + "/.ISO_STRUCTURE/"
    print(config.ISOTree)
    config.TempSys = isodir + "/.TMPSYS/"
    aptcache = adict["aptcache"]
    ourgui = adict["gui"]
    pagenum = ourgui.wizard.add_tab()
    page = gui.Frame(ourgui.wizard.page(pagenum))
    ourgui.wizard.add_page_body(pagenum, _("OSWeaver"), page)
    page.frame = gui.Frame(page, borderwidth=2, relief=Tkinter.GROOVE)
    page.progress = gui.Progressbar(page)
    page.progress.pack(fill=Tkinter.X, expand=True, side=Tkinter.BOTTOM,
                          anchor=Tkinter.S)
    page.frame.pack(fill=Tkinter.BOTH, expand=True, anchor=Tkinter.CENTER)
    page.button = gui.Button(page.frame, text="Start!", command=runThreads)
    page.button.pack()
