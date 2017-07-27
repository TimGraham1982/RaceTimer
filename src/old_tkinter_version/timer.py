'''
Created on 30 Aug 2016

@author: tim
'''

import time
import threading


class Countdown_Timer():
    def __init__(self,length, signals, display):
        self.length = length #Length and signals currently in senconds
        self.signals = signals[:]
        if 0 not in self.signals: self.signals.append(0)
        self.signals.sort()
        self.signals.reverse()
        self.display = display
        
    def count(self, stop_var):
        start_horn() 
        now = self.length
        for signal in self.signals:
            while now > signal:
                now -= self.second(time.time())
                if stop_var.is_set(): return
                self.clock_print(now)
            start_horn()

    def clock_print(self, seconds):
        #print("%02d:%02d" % divmod(round(seconds),60) )
        self.display.configure(text = "%02d:%02d" % divmod(round(seconds),60) )

    def second(self, start):
        while time.time() < start + 1:
            time.sleep(0.01)
        return time.time() - start

def start_horn_thread(horn_off, seconds=None):
    thread = threading.Thread(target=start_horn, args=(horn_off, seconds))
    print('here')
    thread.start

def start_horn(horn_off, seconds=None):
    '''
    Eventually this should be a function to sound the horn
    Possibly use gevent to open and close the relay but can this be used in windows
    '''
    print("BEEP")
    #If number of seconds is provided then wait that length of time before calling stop_horn
    # with horn_off event already set
    # Otherwise just call stop_horn
    if seconds is not None:
        time.sleep(seconds)
        horn_off.set()
    stop_horn(horn_off)


def stop_horn(horn_off):
    '''
    Eventually this should be a function to sound the horn
    Possibly use gevent to open and close the relay but can this be used in windows
    '''
    
    horn_off.wait()
    print("End Beep")
