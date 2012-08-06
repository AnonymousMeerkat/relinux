'''
OSWeaver Module for relinux
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import threadmanager, config, gui
import Tkinter

relinuxmodule = True
relinuxmoduleapi = "0.4a1"
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
    ourgui = adict["gui"]
    pagenum = ourgui.wizard.add_tab()
    ourgui.mypage = gui.Label(ourgui.wizard.page(pagenum), text=_("My Page"))
    ourgui.wizard.add_page_body(pagenum, _("Page"), ourgui.mypage)

from relinux.modules.osweaver import isoutil, squashfs, tempsys
