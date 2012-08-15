'''
Thread Managing Class
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import config, fsutil
import time

#threads = []
threadsdone = []
threadsrunning = []


# Finds threads that can currently run (and have not already run)
def findRunnableThreads(threads):
    returnme = []
    cpumax = fsutil.getCPUCount()
    current = 0
    for i in threads:
        if not i in threadsdone and current < cpumax:
            deps = 0
            depsl = len(i["deps"])
            for x in i["deps"]:
                if x in threadsdone:
                    deps = deps + 1
            if deps >= depsl:
                returnme.append(i)
        current = current + 1
        if current >= cpumax:
            break
    return returnme


# Run a thread
def runThread(thread):
    threadsrunning.append(thread)
    thread["thread"].start()


# Check if a thread is alive
def checkThread(thread):
    if thread in threadsrunning:
        if not thread["thread"].isAlive():
            threadsrunning.remove(thread)


# Thread loop
def threadLoop(threads):
    while config.ThreadStop is False:
        # Clear old threads
        for x in threadsrunning:
            checkThread(x)
        # Run runnable threads
        for x in findRunnableThreads(threads):
            runThread(x)
        time.sleep(1 / config.ThreadRPS)
