'''
Created on 16 Feb 2017

@author: tim
'''
from kivy.app import App
from kivy.uix.button import Button


class MyClass(App):
    '''
    classdocs
    '''
    def build(self):
        return Button(text='Hello!',
                      background_color=(0, 0, 1, 1),  # List of
                                                      # rgba components
                      font_size=150)
    
    
if __name__=="__main__":
    MyClass().run()
        