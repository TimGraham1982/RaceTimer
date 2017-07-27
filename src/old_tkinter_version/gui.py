'''
Created on 3 Sep 2016

@author: tim
'''

import sys
sys.path.append('src')
from timer import Countdown_Timer, start_horn, start_horn_thread
import Tkinter as Tk
import tkMessageBox
import threading


class RaceTimer():
    def __init__(self, master):
        self.frame = Tk.Frame(master)
        self.frame.pack(fill=Tk.BOTH, expand=1)
        self.set_up_horn_thread()
        self.create_widgets()
        self._stop_timer = threading.Event()
        self._running = threading.Event()
        
    def create_widgets(self):
        self.start_button = Tk.Button(self.frame, text = "start",
                                        fg = 'Black', command = self.run_timer)
        self.start_button.grid(column=3, row = 0)
        self.stop_button = Tk.Button(self.frame, text = "STOP",
                                        fg = 'Black', command = self.stop_timer)
        self.stop_button.grid(column=3,row=1)
        self.horn_button = Tk.Button(self.frame, text='HORN', fg = 'Black')
        self.horn_button.grid(column=3,row=2)
        self.horn_button.bind('<ButtonPress-1>', self.start_horn_thread_local )
        self.horn_button.bind('<ButtonRelease-1>', self._horn_off.set )
        self.timing_choice_frame()
        self.clock_frame()
        
    def start_horn_thread_local(self):
        start_horn_thread(self._horn_off)

    def clock_frame(self):
        frame = Tk.Frame(self.frame, bd=2, relief=Tk.SUNKEN, width=45, height=30)
        frame.grid(row=3,columnspan=3)
        label = Tk.Label(frame, text="Time to next start:", font=("Helvetica", 30))
        self.clock_display = Tk.Label(frame, text="0:00", font=("Helvetica", 140))
        label.grid(row=0)
        self.clock_display.grid(row=1, rowspan=3)
        
    def set_up_horn_thread(self):
        self._horn_off = threading.Event()

    def timing_choice_frame(self):
        frame = Tk.Frame(self.frame, bd=2, relief=Tk.SUNKEN, width=38, padx=3)
        frame.grid(row = 0, columnspan=3)
        label = Tk.Label(frame,text = "Choose timing option:", width=20)
        label.grid(row = 0, column = 0)
    
        mb = Tk.Menubutton(frame, text = 'Choose Sequence', relief = 'raised', width=15)
        
        mb.menu = Tk.Menu(mb, tearoff=0)
        mb["menu"]  =  mb.menu
        self.sequence = Tk.StringVar()
        self.timing_choice_menu_options(mb)
        mb.grid(row = 0, column=1)
        
        label = Tk.Label(frame, text = 'Number of Starts', width=15)
        label.grid(row = 1, column=0)
        self.n_starts_button = Tk.Spinbox(frame,from_=1, to=20 , width=20)
        self.n_starts_button.grid(row=1, column=1)

    def timing_choice_menu_options(self, mb):
        
        mb.menu.add_radiobutton(label = '5, 4, 1, Go',
                             variable = self.sequence,
                             value = '541go')
        
        mb.menu.add_radiobutton(label = '6, 3, 1, Go (followed by 3, 1, Go)',
                             variable = self.sequence,
                             value='631go')

        mb.menu.add_radiobutton(label = '6, 3, 1, Go (followed by 6,3,1,Go)',
                             variable = self.sequence,
                             value='631go2')

        mb.menu.add_radiobutton(label = '6, 3, Go (subsequent starts at 3 minute intervals)',
                             variable = self.sequence,
                             value='63go_3')

        mb.menu.add_radiobutton(label = '6, 3, Go (subsequent starts at 6 minute intervals)',
                             variable = self.sequence,
                             value='63go_6')
        
        mb.menu.add_radiobutton(label = '3,2,1, Go (repeated for subsequent starts)',
                             variable = self.sequence,
                             value='321')

    def stop_timer(self):
        if not self._running.is_set(): return # Do nothing if timer is not running
        if tkMessageBox.askyesno("Stop Timer?", "Do you really wish to stop the timer?"):
            self._stop_timer.set()
            self.thread.join()    
        
    def run_timer(self):
        if self._running.is_set(): return #Do noting if timer is already running
        sequence = self.sequence.get()
        
        n_starts = int(self.n_starts_button.get())
        
        if sequence=='541go':
            self.length = n_starts * [300]
            self.signals = n_starts * [[240, 60]]
        elif sequence=='631go':
            self.length = [360]
            if n_starts>1: self.length.extend((n_starts-1) * [180])
            self.signals = n_starts * [[180, 60]]
        elif sequence=='631go2':
            self.length = n_starts * [360]
            self.signals = n_starts * [[180, 60]]
        elif sequence=='63go_3':
            self.length = [360]
            self.signals = [[180]]
            if n_starts>1: 
                self.length.extend((n_starts-1) * [180])
                self.signals.extend((n_starts-1)*[])
        elif sequence=='63go_6':
            self.length = n_starts * [360]
            self.signals = n_starts * [[180]]
        elif sequence=='321':
            self.length = n_starts * [180]
            self.signals = n_starts * [[120, 60]]
        else:
            tkMessageBox.showerror('No sequence selected', 
                                   'Please select a start sequence from the drop down menu')
            return
        
        self._stop_timer.clear()
        self._running.set()
        self.thread = threading.Thread(target=self._time, args=(n_starts, self._stop_timer))
        self.thread.start()
        
    def _time(self, n_starts, stop_thread):
        for i in range(n_starts):
            Countdown_Timer(self.length[i], self.signals[i], self.clock_display).count(stop_thread)
        self._running.clear()

def close_window():
    '''
    What to do if the user closes the window
    '''
    if tkMessageBox.askyesno("Quit?", "Do you really wish to quit?"):
        app._stop_timer.set()
        if hasattr(app, "thread"): app.thread.join()
        root.destroy()


if __name__=="__main__":
    root = Tk.Tk()
    #root.geometry("480x360")

    app = RaceTimer(root)
    
    root.protocol("WM_DELETE_WINDOW", close_window)

    root.mainloop()
