'''
Created on 30 Jul 2017

@author: tim
'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty
from kivy.clock import Clock


class HomeScreen(BoxLayout):
    '''
    Main page containing the buttons and timers.
    '''
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.ids.clock1.seconds_to_start = 300
        
    def start(self):
        self.event = Clock.schedule_interval(self.change_time, 1)
    
    def change_time(self, dt):
        self.ids.clock1.seconds_to_start -= dt


class ClockDisplay(Label):
    scale_factor = .9
    factor = dimension = None
    seconds_to_start = NumericProperty(180)
    
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
        mins = self.seconds_to_start/60
        secs = self.seconds_to_start % 60
        
        self.text = '%d' % mins + ':' '%02d' % secs


class TimerApp(App):
    def build(self):
        return HomeScreen()
        

if __name__ == '__main__':
    TimerApp().run()