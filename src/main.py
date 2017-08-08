'''
Created on 30 Jul 2017

@author: tim
'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import (NumericProperty, ListProperty, 
                             ObjectProperty, BooleanProperty,
                             OptionProperty, StringProperty)
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from settings import settings_json
from kivy.uix.gridlayout import GridLayout

from functools import partial
import time
import numpy as np


class HomeScreen(BoxLayout):
    nstarts = NumericProperty(1, min=1, max=4)
    sequence = OptionProperty('5, 4, 1, Go', 
                              options = ['5, 4, 1, Go', 
                                         '6, 3, 1, Go', 
                                         '6, 3, Go', 
                                         '3, 2, 1, Go',
                                         '1, Go'])
    interval = NumericProperty(5)
    add_minute = BooleanProperty(False)
    recall_type = OptionProperty('stop_remaining_sequences', 
                                 options=['move_to_end',
                                          'stop_remaining_sequences'])
    
    '''
    Main page containing the buttons and timers.
    '''
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.on_nstarts()
        self.horn_trigger_set()
        for c in self.clock_list: c.horn_trigger = self.horn_trigger        
        self.on_sequence()
        self.horn = SoundLoader.load('airhorn.wav')
    
    def reset(self):
        if hasattr(self, 'running'):
            if not self.running.is_triggered:
                #Clock is running so we want to stop it
                self.on_sequence()
        else:
            self.on_sequence()      
    
    def start_stop(self):
        if hasattr(self, 'running'):
            if self.running.is_triggered:
                #Clock is running so we want to stop it
                self.stop()
                return
        
        #Clock not running so start it
        self.start()
        
    def start(self):
        #Make sure horn is setup first
        self.horn_trigger_set()
        for c in self.clock_list:
            if c.seconds_to_start in c.sound_signals:
                self.horn_trigger()
        self.running = Clock.schedule_interval(self.cycle, 1)
        self.ids.start_stop_btn.text = 'POSTPONE/ABANDON'
    
    def cycle(self, dt):
        self.horn_trigger_set()
        for c in self.clock_list:
            c.horn_trigger = self.horn_trigger
            if not c.paused:
                new_time = round(c.seconds_to_start - dt)
                c.seconds_to_start = new_time
        
    def general_recall(self):
        #find the race that has just started
        #Work out what needs to be done to time
        #For last start may need a popup to restart the sequence
        if not hasattr(self, 'running'): return
        if self.running.is_triggered:
            #wait for horn to stop
            if self.horn.state=='play':
                while self.horn.state=='play':
                    time.sleep(0.01)
                time.sleep(0.5)
            Clock.schedule_once(partial(self.sound_horn, 1.75), 0)
            Clock.schedule_once(partial(self.sound_horn, 1.75), 2.5)
            
            #If only 1 start then stop it to be run again.
            if self.nstarts==1: 
                self.running.cancel()            
                self.ids.start_stop_btn.text = 'START'

            #How many clocks are negative
            nstarted = 0
            times = []
            for c in self.clock_list:
                if c.seconds_to_start <= 0: 
                    nstarted+=1
                times.append(c.seconds_to_start)
            times = np.array(times)
            # Find index of clock which has just started
            clock_index = (np.abs(times)*-1).argmax()
                
            if nstarted==self.nstarts:
                #recall on last start
                pass
            else:
                if self.recall_type=='move_to_end':
                    add_time = int((self.interval*60 
                                + np.ceil(times.max()/60.)*60))
                    c = self.clock_list[clock_index]
                    c.seconds_to_start = c.seconds_to_start+add_time
                elif self.recall_type=='stop_remaining_sequences':
                    for i,c in enumerate(self.clock_list):
                        if i==clock_index or c.seconds_to_start > 0:
                            c.paused = True
                            #TODO: Reset remaining clocks
                            #TODO: Popup to restart the sequence

    def stop(self):
        content = ConfirmStopPopup(text='Do you really want to stop the timer?')
        content.bind(on_answer=self._on_answer)
        self.popup = Popup(title="Stop?",
                            content=content,
                            size_hint=(0.7,0.7),
                            auto_dismiss= False)
        self.popup.open()
        
    def _on_answer(self, instance, answer):
        self.popup.dismiss()
        
        if answer == 'yes_quiet':
            self.running.cancel()
            self.ids.start_stop_btn.text = 'START'
        if answer == 'yes_horn':
            self.running.cancel()
            Clock.schedule_once(partial(self.sound_horn, 1.75), 0)
            Clock.schedule_once(partial(self.sound_horn, 1.75), 2.5)
            self.ids.start_stop_btn.text = 'START'
    
    def horn_trigger_set(self):
        if hasattr(self, 'horn_trigger'):
            if not self.horn_trigger.is_triggered:
                self.horn_trigger = Clock.create_trigger(
                                    partial(self.sound_horn, 1.75))
        else:
            self.horn_trigger = Clock.create_trigger(
                                partial(self.sound_horn, 1.75))
    
    def sound_horn(self,length,dt):
        self.horn.play()
        Clock.schedule_once(lambda dt: self.horn.stop(), length)
        
    def on_nstarts(self, *args):
        '''
        Eventually this should set up to 4 clocks on the display
        '''
        if hasattr(self, 'clock_list'):
            for c in self.clock_list: self.ids.clocks.remove_widget(c)
        self.clock_list = []
        for i in range(int(self.nstarts)):
            c = ClockDisplay()
            self.ids.clocks.add_widget(c, index=i)
            self.clock_list.insert(0,c)
        self.on_sequence()
    
    def on_interval(self, *args):
        self.on_sequence()
        
    def on_add_minute(self, *args):
        self.on_sequence()
    
    def on_sequence(self, *args):
        for i,c in enumerate(self.clock_list):
            #Clear list of sound signals to avoid horn being triggered
            c.sound_signals = []
            if self.add_minute=='1': 
                extra=60            
            else: 
                extra=0
            if self.sequence == '5, 4, 1, Go':
                c.seconds_to_start = 5*60 + i*self.interval*60 + extra
                c.sound_signals = [5*60, 4*60, 60, 0]
                if i==0 and self.add_minute: c.sound_signals.insert(0, 6*60)
            elif self.sequence == '6, 3, 1, Go':
                c.seconds_to_start = 6*60 + i*self.interval*60 + extra
                c.sound_signals = [6*60, 3*60, 60, 0]
                if i==0 and self.add_minute: c.sound_signals.insert(0, 7*60)
            elif self.sequence == '6, 3, Go':
                c.seconds_to_start = 6*60 + i*self.interval*60 + extra
                c.sound_signals = [6*60, 3*60, 0]
                if i==0 and self.add_minute: c.sound_signals.insert(0, 7*60)
            elif self.sequence == '3, 2, 1, Go':
                c.seconds_to_start = 3*60 + i*self.interval*60 + extra
                c.sound_signals = [3*60, 2*60, 60, 0]
                if i==0 and self.add_minute: c.sound_signals.insert(0, 4*60)
            elif self.sequence == '1, Go':
                c.seconds_to_start = 60 + i*self.interval*60 + extra
                c.sound_signals = [60, 0]
                if i==0 and self.add_minute: c.sound_signals.insert(0, 2*60)



class ConfirmStopPopup(GridLayout):
    text = StringProperty()
   
    def __init__(self,**kwargs):
        self.register_event_type('on_answer')
        super(ConfirmStopPopup,self).__init__(**kwargs)
        
    def on_answer(self, *args):
        pass
    

class ClockDisplay(Label):
    scale_factor = .9
    factor = dimension = None
    seconds_to_start = NumericProperty(180)
    sound_signals = ListProperty([30,25])
    paused = BooleanProperty(False)
    
    def on_texture_size(self, *args):
        try:
            if not self.factor:
                self.factor = [self.font_size / self.texture_size[0], 
                               self.font_size / self.texture_size[1]]
    
            self.font_size0 = self.size[0] * self.scale_factor * self.factor[0]
            self.font_size1 = self.size[1] * self.scale_factor * self.factor[1]
    
            if self.font_size0 < self.font_size1:
                self.font_size = self.font_size0
            else:
                self.font_size = self.font_size1
        except ZeroDivisionError:
            pass
    
    def on_seconds_to_start(self, *args):
        if self.seconds_to_start in self.sound_signals:
            if hasattr(self, 'horn_trigger'): self.horn_trigger()
        mins = abs(self.seconds_to_start/60)
        secs = abs(self.seconds_to_start) % 60
        
        self.text = '%d' % mins + ':' '%02d' % secs
        if self.seconds_to_start <= 0:
            self.color = [0,1,0,1]
        else:
            self.color = [1,1,1,1]

class TimerApp(App):
    def build(self):
        home=HomeScreen()
        home.nstarts = self.config.get('Race settings','nstarts')
        home.interval = self.config.get('Race settings','interval')
        home.sequence = self.config.get('Race settings','sequence')
        home.add_minute = self.config.get('Race settings','add_minute')
        return home
    
    def build_config(self, config):
        config.setdefaults('Race settings',
            {'sequence': '5, 4, 1, Go',
             'nstarts': 1,
             'interval' : 5,
             'add_minute': False})
    
    def build_settings(self, settings):
        settings.add_json_panel('Race settings',
                                self.config,
                                data = settings_json)
    
    def on_config_change(self, config, section, key, value):
        if key=='nstarts' : self.root.nstarts = value
        if key=='sequence': self.root.sequence = value
        if key=='interval': self.root.interval = value
        if key=='add_minute': self.root.add_minute = value
        
        
if __name__ == '__main__':
    TimerApp().run()