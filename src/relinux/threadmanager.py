'''
Thread Managing Class
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import config, fsutil
import time

#threads = []


# Finds threads that can currently run (and have not already run)
def findRunnableThreads(threads, threadsdone, threadsrunning):
    returnme = []
    cpumax = fsutil.getCPUCount()
    current = 0
    for i in threads:
        if not i["tn"] in threadsdone and current < cpumax:
            deps = 0
            depsl = len(i["deps"])
            for x in i["deps"]:
                if x["tn"] in threadsdone:
                    deps = deps + 1
            if deps >= depsl:
                returnme.append(i)
        current = current + 1
        if current >= cpumax:
            break
    return returnme


# Run a thread
def runThread(thread, threadsdone, threadsrunning):
    if not thread["thread"].isAlive() and not thread["tn"] in threadsdone:
        threadsrunning.append(thread["tn"])
        thread["thread"].start()


# Check if a thread is alive
def checkThread(thread, threadsdone, threadsrunning):
    if thread["tn"] in threadsrunning:
        if not thread["thread"].isAlive():
            threadsrunning.remove(thread["tn"])
            threadsdone.append(thread["tn"])


# Thread loop
def threadLoop(threads):
    threadsdone = []
    threadsrunning = []
    while config.ThreadStop is False:
        # Clear old threads
        for x in threadsrunning:
            checkThread(x, threadsdone, threadsrunning)
        # Run runnable threads
        for x in findRunnableThreads(threads, threadsdone, threadsrunning):
            runThread(x, threadsdone, threadsrunning)
        time.sleep(float(1.0 / config.ThreadRPS))
