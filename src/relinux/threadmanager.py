# -*- coding: utf-8 -*-
'''
Thread Managing Class
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

from relinux import config, fsutil, logger, utilities
from PyQt4 import QtCore
import time
import threading
import copy
import collections


tn = logger.genTN("TheadManager")
cpumax = fsutil.getCPUCount() * 2


# Custom thread class
class Thread(QtCore.QThread):
    def __init__(self, **kw):
        QtCore.QThread.__init__(self)
        for i in kw:
            self.__dict__[i] = kw[i]

    def is_alive(self):
        return self.isRunning()

    def isAlive(self):
        return self.is_alive()

    def run(self):
        self.runthread()


# Finds threads that can currently run (and have not already run)
def findRunnableThreads(threadids, threadsdone, threadsrunning, threads, **options):
    returnme = []
    current = 0
    for i in threadids:
        thread = getThread(i, threads)
        #print(utilities.utf8all(thread["threadspan"], " ", current))
        if (thread["enabled"] and not i in threadsdone and current < cpumax and not
            ((thread["threadspan"] < 0 and current > 0) or
             (thread["threadspan"] > (cpumax - current)))):
            deps = 0
            depsl = len(thread["deps"])
            if "deps" in options and options["deps"]:
                deps = depsl
            else:
                for x in thread["deps"]:
                    if x in threadsdone or x == i:
                        deps += 1
            if deps >= depsl:
                returnme.append(i)
                if thread["threadspan"] < 0:
                    current = cpumax
                else:
                    current += thread["threadspan"]
            elif False:
                if thread["tn"] == "ISO" or True:
                    ls = []
                    for x in thread["deps"]:
                        if not x in threadsdone:
                            ls.append(str(getThread(x, threads)["tn"]) + " " + str(x))
        if current >= cpumax:
            break
    return returnme


# Run a thread
def runThread(threadid, threadsdone, threadsrunning, threads, lock, **options):
    thread = getThread(threadid, threads)
    if not thread["thread"].is_alive() and not threadid in threadsdone and not threadid in threadsrunning:
        threadsrunning.append(threadid)
        logger.logV(tn, logger.I, _("Starting") + " " + thread["tn"] + "...")
        thread["thread"].start()
        if options.get("poststart") != None and lock != None:
            with lock:
                options["poststart"](threadid, threadsrunning, threads)


# Check if a thread is alive
def checkThread(threadid, threadsdone, threadsrunning, threads, lock, **options):
    thread = getThread(threadid, threads)
    if threadid in threadsrunning:
        if not thread["thread"].is_alive():
            thread["thread"].wait()
            threadsrunning.remove(threadid)
            threadsdone.append(threadid)
            logger.logV(tn, logger.I, thread["tn"] + " " +
                        _("has finished. Number of threads running: ") + str(len(threadsrunning)))
            if options.get("postend") != None and lock != None:
                with lock:
                    options["postend"](threadid, threadsrunning, threads)


# Returns a thread from an ID
def getThread(threadid, threads):
    return threads[threadid]


# Make sure all threads have these attributes (which are "optional")
def addOptional(threads):
    for i in range(len(threads)):
        if not "threadspan" in threads[i]:
            threads[i]["threadspan"] = 1
        if not "enabled" in threads[i]:
            threads[i]["enabled"] = True
    logger.logVV(tn, logger.D, "Check addoptional")


# Thread loop
def threadLoop(threads1_, **options):
    logger.logV(tn, logger.D, "Running thread loop")
    # Remove pointers
    threads1 = copy.deepcopy(threads1_)
    # Initialization
    threadsdone = []
    threadsrunning = []
    threadids = []
    threads = []
    pslock = None
    pelock = None
    if "poststart" in options:
        pslock = threading.RLock()
        if "postend" in options and options["postend"] == options["poststart"]:
            pelock = pslock
    logger.logVV(tn, logger.D, "Check poststart")
    if "postend" in options and pelock == None:
        pelock = threading.RLock()
    logger.logVV(tn, logger.D, "Check postend")
    # Remove duplicates and remove disabled threads
    for i in threads1:
        if not i in threads and i["enabled"]:
            threads.append(i)
    logger.logVV(tn, logger.D, "Check remduplicates")
    addOptional(threads)
    # Generate the threads
    for i in range(len(threads)):
        temp_ = threads[i]["thread"]
        kw = {"tn": logger.genTN(threads[i]["tn"])}
        if "threadargs" in options:
            for x in options["threadargs"].keys():
                kw[x] = options["threadargs"][x]
        temp = temp_(**kw)
        threads[i]["thread"] = temp
    logger.logVV(tn, logger.D, "Check genthreads")
    # Generate the thread IDS
    for i in range(len(threads)):
        threadids.append(i)
    logger.logVV(tn, logger.D, "Check genthreadids")
    # Make sure thread dependencies are made as IDs, and not actual thread dictionaries
    for i in range(len(threads)):
        for x in range(len(threads[i]["deps"])):
            if threads[i]["deps"][x] in threads:
                for y in range(len(threads)):
                    if threads[i]["deps"][x] == threads[y]:
                        threads[i]["deps"][x] = y
                        break
    logger.logVV(tn, logger.D, "Check threaddeps")
    # Actual loop
    def _ActualLoop(threads, threadsdone, threadsrunning, threadids):
        logger.logVV(tn, logger.D, "Check ActualLoop")
        #global threads, threadsdone, threadsrunning, threadids
        while config.ThreadStop is False:
            # Clear old threads
            for x in threadsrunning:
                checkThread(x, threadsdone, threadsrunning, threads, pelock, **options)
            # End if all threads are done
            if len(threadsdone) >= len(threads):
                logger.logVV(tn, logger.D, "Ending ActualLoop")
                break
            # Run runnable threads
            for x in findRunnableThreads(threadids, threadsdone, threadsrunning, threads, **options):
                runThread(x, threadsdone, threadsrunning, threads, pslock, **options)
            time.sleep(float(1.0 / config.ThreadRPS))
        if ("threadsend" in options and isinstance(options["threadsend"], collections.Callable)):
            options["threadsend"](threadids, threadsdone, threads)
    # Make a new thread (so that the user can continue on using relinux)
    t = threading.Thread(target = _ActualLoop, args = (threads, threadsdone, threadsrunning, threadids))
    t.start()
