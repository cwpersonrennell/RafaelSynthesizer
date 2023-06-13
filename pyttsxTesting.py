# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 14:25:58 2023

@author: cpers
"""

import pyttsx3
engine = pyttsx3.init()


engine.setProperty('rate',125)
engine.setProperty('volume',1.0)

voices = engine.getProperty('voices')

print(voices[0])
voices[0].age=5
engine.say("hello")
engine.runAndWait()