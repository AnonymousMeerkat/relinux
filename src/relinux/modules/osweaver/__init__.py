'''
OSWeaver Module for relinux
@author: Anonymous Meerkat
'''

from relinux import threadmanager, config
import tkinter

relinuxmodule = True
modulename = "OSWeaver"

# Just in case config.ISOTree doesn't include a /
isotreel = config.ISOTree + "/"
tmpsys = config.TempSys + "/"
configs = {}
aptcache = {}


def runThreads():
    threads = []
    threads.extend(isoutil.threads)
    threads.extend(squashfs.threads)
    threads.extend(tempsys.threads)
    threadmanager.threadLoop(threads)


def run(adict):
    global configs, aptcache
    configs = adict["config"]["OSWeaver"]
    aptcache = adict["aptcache"]
    gui = adict["gui"]
    pagenum = gui.wizard.add_tab()
    gui.mypage = tkinter.Label(gui.wizard.page_container(pagenum), text=_("My Page"))
    gui.wizard.add_page_body(pagenum, _("Page"), gui.mypage)

from relinux.modules.osweaver import isoutil, squashfs, tempsys
