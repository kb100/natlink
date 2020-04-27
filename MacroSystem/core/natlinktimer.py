"""
Handling of more calls to the Natlink timer
Quintijn Hoogenboom, 25-4-2020

"""
#---------------------------------------------------------------------------
import copy
import time
import natlink
natlinktimer = None


class NatlinkTimer:
    """
    This class utilises :meth:`natlink.setTimerCallback`, so more callback can be done
    """

    def __init__(self):
        """
        """
        self.callbacks = {}
        self.debug = None

    def __del__(self):
        """stop the timer, when destroyed
        """
        natlink.setTimerCallback(None, 0)
    
    def addCallback(self, callback, interval, debug=None):
        """add an interval 
        """
        self.debug = self.debug or debug
        curTime = time.time()
        if interval <= 0:
            self.removeCallback(callback)
            return
        if interval <= 24:
            interval = interval * 1000
        interval = int(interval)
        prevTime = curTime
        self.callbacks[callback] = (interval, prevTime)
        if self.debug: print("set timer %s: %s (%s)"% (callback, interval, prevTime))
        self.hittimer()

    def removeCallback(self, callback, debug=None):
        """remove a callback function
        """
        self.debug = self.debug or debug
        if self.debug: print("remove timer for %s"% callback, prevTime)

        try:
            del self.callbacks[callback]
        except KeyError:
            pass
        if not self.callbacks:
            if self.debug: print("last timer removed, setTimerCallback to 0")

            natlink.setTimerCallback(None, 0)
            return
        self.hittimer()
        
    def hittimer(self):
        """move to a next callback point
        """
        starttime = time.time()
        if self.debug: print("start hittimer at", starttime)

        nextTimes = []
        for callbackFunc, (interval, prevTime) in copy.copy(self.callbacks).items():
            elapsed = starttime - prevTime
            if elapsed >= interval:
                try:
                    if self.debug: print("do callback %s (%s, %s)"% (callbackFunc, elapsed, interval))
                    callbackFunc()
                except:
                    if self.debug: print("callbackFunc %s throws an exception, remove from callbacks dict"% callbackFunc)
                    del self.callbacks[callbackFunc]
                else:
                    if self.debug > 1: print("set new timer interval %s: %s"% (callbackFunc, interval))
                    nextTimes.append(interval)
            else:
                remaining = interval - elapsed
                if self.debug > 1: print("set remaining time for %s: %s"% (callbackFunc, remaining))
                nextTimes.append(remaining)
        
        endtime = time.time()
        callbackstime = endtime - starttime
        if self.debug: print("time for %s callback functions: %s"% (len(self.callbacks), callbackstime))
        
        if self.callbacks:
            nextTime = int(min(nextTimes))
            if self.debug: print("set nextTime to: %s"% nextTime)
            natlink.setTimerCallback(self.hittimer, nextTime)
        else:
            if self.debug: print("no callbackFunction any more, switch off the natlink timerCallback")
            natlink.setTimerCallback(None, 0)

def setTimerCallback(callback, interval, debug=None):
    """This function sets a callback
    
    Interval in seconds, unless larger than 24
    callback: the function to be called
    """
    global natlinktimer
    if not natlinktimer:
        natlinktimer = NatlinkTimer()
    if not natlinktimer:
        raise Exception("NatlinkTimer cannot be started")
    
    if callback is None:
        raise Exception("stop the timer callback with natlinktimer.removeCallback(callback)")
    
    if interval:
        natlinktimer.addCallback(callback, interval, debug=debug)
    else:
        natlinktimer.removeCallback(callback, debug=debug)

def removeTimerCallback(callback, debug=None):
    """This function removes a callback from the callbacks dict
    
    callback: the function to be called
    """
    global natlinktimer
    if not natlinktimer:
        print("no timers active, cannot remove %s from natlinktimer"% callback)
        return
    
    if callback is None:
        raise Exception("please stop the timer callback with removeTimerCallback(callback)\n    or with setTimerCallback(callback, 0)")
    
    natlinktimer.removeCallback(callback, debug=debug)

def stopTimerCallback():
    """should be called at destroy of Natlink
    """
    global natlinktimer
    if natlinktimer:
        del natlinktimer
