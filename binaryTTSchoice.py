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

filenames = []
for bchoice in choices:
    filenames.append(["./wav/"+bchoice[0]+".wav","./wav/"+bchoice[1]+".wav"])
    engine.save_to_file(bchoice[0], f"./wav/{bchoice[0]}.wav")
    engine.save_to_file(bchoice[1], f"./wav/{bchoice[1]}.wav")
    engine.runAndWait()
    
print("Created and saved the text to speech!")
