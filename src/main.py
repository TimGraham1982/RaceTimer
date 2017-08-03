'''
Created on 30 Jul 2017

@author: tim
'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import (NumericProperty, ListProperty, 
                             ObjectProperty, BoundedNumericProperty,
                             OptionProperty, StringProperty)
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from settings import settings_json
from kivy.uix.gridlayout import GridLayout

from functools import partial


class HomeScreen(BoxLayout):
    nstarts = NumericProperty(1, min=1, max=4)
    sequence = OptionProperty('5, 4, 1, Go', 
                              options = ['5, 4, 1, Go', 
                                         '6, 3, 1, Go', 
                                         '6, 3, Go', 
                                         '3, 2, 1, Go'])
    interval = NumericProperty(5)
    
    '''
    Main page containing the buttons and timers.
    '''
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.horn_trigger = Clock.create_trigger(
                            partial(self.sound_horn, 1.75))
        self.ids.clock1.horn_trigger = self.horn_trigger
        self.on_sequence()
        self.horn = SoundLoader.load('airhorn.wav')
    
    def start_stop(self):
        if hasattr(self, 'running'):
            if self.running.is_triggered:
                #Clock is running so we want to stop it
                self.stop()
                return
        
        #Clock not running so start it
        #Make sure horn is setup first
        if not self.horn_trigger.is_triggered:
            self.horn_trigger = Clock.create_trigger(
                                partial(self.sound_horn, 1.75))
        if self.ids.clock1.seconds_to_start in self.ids.clock1.sound_signals:
            self.horn_trigger()
        self.running = Clock.schedule_interval(self.cycle, 1)
        self.ids.start_stop_btn.text = 'POSTPONE/ABANDON'
    
    def cycle(self, dt):
        if not self.horn_trigger.is_triggered:
            self.horn_trigger = Clock.create_trigger(
                                partial(self.sound_horn, 1.75))
        self.ids.clock1.horn_trigger = self.horn_trigger
        new_time = round(self.ids.clock1.seconds_to_start - dt)
        self.ids.clock1.seconds_to_start = new_time
        
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
    
    def sound_horn(self,length,dt):
        self.horn.play()
        Clock.schedule_once(lambda dt: self.horn.stop(), length)
        
#    def on_nstarts(self):
#        '''
#        Eventually this should set up to 4 clocks on the display
#        '''
#        pass
    
    def on_sequence(self, *args):
        if self.sequence == '5, 4, 1, Go':
            self.ids.clock1.seconds_to_start = 5*60
            self.ids.clock1.sound_signals = [5*60, 4*60, 60, 0]
        elif self.sequence == '6, 3, 1, Go':
            self.ids.clock1.seconds_to_start = 6*60
            self.ids.clock1.sound_signals = [6*60, 3*60, 60, 0]
        elif self.sequence == '6, 3, Go':
            self.ids.clock1.seconds_to_start = 6*60
            self.ids.clock1.sound_signals = [6*60, 3*60, 0]
        elif self.sequence == '3, 2, 1, Go':
            self.ids.clock1.seconds_to_start = 3*60
            self.ids.clock1.sound_signals = [3*60, 2*60, 60, 0]


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
    
    def text_formatter(self, *args):
        if self.seconds_to_start in self.sound_signals:
            if hasattr(self, 'horn_trigger'): self.horn_trigger()
        mins = self.seconds_to_start/60
        secs = self.seconds_to_start % 60
        
        self.text = '%d' % mins + ':' '%02d' % secs


class TimerApp(App):
    def build(self):
        home=HomeScreen()
        home.nstarts = self.config.get('Race settings','nstarts')
        home.sequence = self.config.get('Race settings','sequence')
        return home
    
    def build_config(self, config):
        config.setdefaults('Race settings',
            {'sequence': '5, 4, 1, Go',
             'nstarts': 1,
             'interval' : 5})
    
    def build_settings(self, settings):
        settings.add_json_panel('Race settings',
                                self.config,
                                data = settings_json)
    
    def on_config_change(self, config, section, key, value):
        print 'In app nstarts=', value
        if key=='nstarts' : self.root.nstarts = value
        if key=='sequence': self.root.sequence = value
        if key=='interval': self.root.interval = value
        
        
if __name__ == '__main__':
    TimerApp().run()