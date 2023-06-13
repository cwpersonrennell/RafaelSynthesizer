# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 14:16:29 2023

@author: cpers
"""

from gtts import gTTS

text = "hello"
tts = gTTS(text=text,lang="en")
filename=f"C:/Users/cpers/Documents/GitHub/RafaelSynthesizer/mp3/{text}.mp3" 
    file.write("")
    file.close()
tts.save(filename)