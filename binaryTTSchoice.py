# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 14:39:54 2023

@author: cpers
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May 31 08:28:14 2023

@author: cpers
"""


import pyttsx3
from config import config
engine = pyttsx3.init()
choices =config["choices"]
engine.save_to_file("Now choosing between:","./wav/CHOICES.wav")
for bchoice in choices:
    engine.save_to_file(bchoice[0], f"./wav/{bchoice[0]}.wav")
    engine.save_to_file(bchoice[1], f"./wav/{bchoice[1]}.wav")
    engine.runAndWait()
    print(f"Generated WAV files for {bchoice[0]} and {bchoice[1]}")
    

