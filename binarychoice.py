# -*- coding: utf-8 -*-
"""
Created on Wed May 31 08:28:14 2023

@author: cpers
"""

import pygame
from pygame import joystick
pygame.init()
joystick.init()
joysticks = [joystick.Joystick(x) for x in range(joystick.get_count())]
for joy in joysticks:
    joy.init()

choices = [["yes","no"]]

filenames = []
for bchoice in choices:
    filenames.append(["./mp3/"+bchoice[0]+".mp3","./mp3/"+bchoice[1]+".mp3"])
    
pygame.mixer.music.load(filenames[0][0])
def joyStickHandler(event):
    if event.type == pygame.JOYBUTTONDOWN:
        if(event.joy == 1):return
        if(event.button == 10):
            pygame.mixer.music.load(filenames[0][0])
        if(event.button == 11):
            pygame.mixer.music.load(filenames[0][1])
    if event.type == pygame.JOYBUTTONUP:
        if(event.joy == 1):return
        pygame.mixer.music.play()
                
try:    
    while(True):
        for e in pygame.event.get():
            joyStickHandler(e)
except KeyboardInterrupt:
    pygame.mixer.music.unload()
    pygame.quit()
    print("Goodbye!")
    
