# -*- coding: utf-8 -*-
"""
Created on Wed May 31 08:28:14 2023

@author: cpers
"""

import pygame
from pygame import joystick
pygame.init()

joysticks = {}
    
choices = [["yes","no"]]

filenames = []
for bchoice in choices:
    filenames.append(["./mp3/"+bchoice[0]+".mp3","./mp3/"+bchoice[1]+".mp3"])
    
pygame.mixer.music.load(filenames[0][0])
DEBUG = False

def dprint(string):
    if DEBUG:
        print(string)

JOYSTICK = False
YESBUTTON =-1
NOBUTTON = -1
def joyStickHandler(event):
    global JOYSTICK
    global YESBUTTON
    global NOBUTTON
    if event.type == pygame.JOYDEVICEADDED:
        joy = joystick.Joystick(event.device_index)
        if joy.get_name() == "PRC Switch Input Device":
            return
        joysticks[joy.get_instance_id()]=joy

        dprint(f"Joystick {joy.get_instance_id()} connected")
        dprint(f"  GUID: {joy.get_guid()}")
        dprint(f"  Name: {joy.get_name()}")

    if event.type == pygame.JOYDEVICEREMOVED:
        joy = joystick.Joystick(event.device_index)
        if joy.get_name() == "PRC Switch Input Device":
            return
        if event.instance_id == JOYSTICK.get_instance_id():
            JOYSTICK = False
            YESBUTTON = -1
            NOBUTTON = -1
        del joysticks[event.instance_id]

        dprint(f"Joystick {event.instance_id} removed")
        
    if event.type == pygame.JOYBUTTONDOWN:
        if not JOYSTICK and event.instance_id in joysticks:
            dprint("Assigning Joystick...")
            JOYSTICK = joysticks[event.instance_id]
        dprint(f"Joy: {event.instance_id}")

        dprint(JOYSTICK.get_instance_id())

        if(event.instance_id != JOYSTICK.get_instance_id()):return
        
        if YESBUTTON == -1:
            YESBUTTON = event.button
        elif YESBUTTON!=event.button and NOBUTTON == - 1:
            NOBUTTON = event.button
        
        if(event.button == YESBUTTON):
            pygame.mixer.music.load(filenames[0][0])
        if(event.button == NOBUTTON):
            pygame.mixer.music.load(filenames[0][1])
    
    if event.type == pygame.JOYBUTTONUP:
        if not JOYSTICK  and event.instance_id in joysticks:
            dprint("Assigning Joystick...")
            JOYSTICK = joysticks[event.instance_id]
            return
        if(event.instance_id != JOYSTICK.get_instance_id()):return
        pygame.mixer.music.play()
                
try:
    while(1):    
        for e in pygame.event.get():
            joyStickHandler(e)
except KeyboardInterrupt:
    pygame.mixer.music.unload()
    pygame.quit()
    print("Goodbye!")

except Exception as e:
    print("Unknown Execption occured")
    print(e)
    pygame.mixer.music.unload()
    pygame.quit()
    
