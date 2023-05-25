# -*- coding: utf-8 -*-
"""
Created on Wed May 17 20:41:11 2023

@author: cpers
"""

import numpy as np
#import sounddevice
from pygame import sndarray, joystick
import pygame
pygame.init()
joystick.init()
joysticks = [joystick.Joystick(x) for x in range(joystick.get_count())]
for joy in joysticks:
    joy.init()


A2=110
A3=2*A2
A4=4*A2
A5=8*A2

As2 = 16/15*A2
As3 = 2*As2
As4 = 4*As2
As5 = 8*As2

B2 = 9/8*A2
B3 = 2*B2
B4 = 4*B2
B5 = 8*B2

C2 = 6/5 * A2
C3 = 2*C2
C4 = 4*C2
C5 = 8*C2

Cs2 = 5/4 * A2
Cs3 = 2*Cs2
Cs4 = 4*Cs2
Cs5 = 8*Cs2

D2 = 4/3 * A2
D3 = 2* D2
D4 = 4*D2
D5 = 8*D2

Ds2 = 45/32 * A2
Ds3 = 2* Ds2
Ds4 = 4* Ds2
Ds5 = 8*Ds2

E2 = 3/2 *A2
E3 = 2*E2
E4 = 4 * E2
E5 = 8*E2

F2 = 8/5 *A2
F3 = 2*F2
F4 = 4*F2
F5 = 8*F2

Fs2 = 5/3 *A2
Fs3 = 2*Fs2
Fs4 = 4*Fs2
Fs5 = 8*Fs2

G2 = 9/5 *A2
G3 = 2*G2
G4 = 4*G2
G5 = 8*G2

Gs2 = 15/8*A2
Gs3 = 2*Gs2
Gs4 = 4*Gs2
Gs5 = 8*Gs2

frequencies = [A2, As2,B2,C2,Cs2,D2,Ds2,E2,F2,Fs2,G2,Gs2,
               A3, As3,B3,C3,Cs3,D3,Ds3,E3,F3,Fs3,G3,Gs3,
               A4, As4,B4,C4,Cs4,D4,Ds4,E4,F4,Fs4,G4,Gs4,
               A5, As5,B5,C5,Cs5,D5,Ds5,E5,F5,Fs5,G5,Gs5]

fs = 44100

def guitarWave(x,h=1,l=0.1,N=10):
    result = 0
    def A(n):
        return (2*h*1)/(np.pi*np.pi*(1-l)*n*n)*np.sin(n*np.pi*l)
    for i in range(1,N+1):
        result+=A(i)*np.cos(i*x)
    return result
    
def triangleWave(x):
    #f(aX) = ax%3 --> period 3/a
    return (x%(2*np.pi))/(2*np.pi)-0.5

def squareWave(x):
    return triangleWave(-x+np.pi)+triangleWave(x)

def purple(x):
    return (2*triangleWave(x)+3*squareWave(x)+np.sin(x)/2)/6

def adsrEnvelope(x,a,d,s,r):
    if x>0 and x<=a:
        return (1/a)*x
    if x>a and x<=a+d:
        return (-0.25/d)*(x-a)+1
    if x>a+d and x<=a+d+s:
        return 0.75
    if x>a+d+s and x<=a+d+s+r:
        return (-0.75/(r))*(x-a-d-s)+0.75
    return 0

class Noise:
    def __init__(self, note, duration=0.25, amplitude=0.125,oscili = np.sin):
        self.note      = note
        self.duration  = duration
        self.amplitude =  amplitude
        self.oscili = oscili
        self.adsr(self.duration/10, self.duration/10,3/10*self.duration,0.5*self.duration)
        self.generateWaveForm()
    
    def adsr(self,a,d,s,r):
        self.a = a
        self.d = d
        self.s = s
        self.r = r
        self.generateWaveForm()
        
    def generateWaveForm(self):
        self.string = f"{round(self.note)}{self.duration}{self.amplitude}{self.oscili.__name__}{self.a}{self.d}{self.s}{self.r}"
        self.string = "./.npyaudio/"+self.string.replace(".","") +".npy"
        try:
            self.noise = np.load(self.string)
            self.sound = sndarray.make_sound(self.noise)
            return
        except:
            pass
        #Size of linear space, frequency samples * duration (in seconds)
        size = round(fs*self.duration)
        #create the linear space
        t = np.linspace(0,self.duration,size)
        
        #use the periodic oscilator to generate sound
        self.noise = []
        #Ug, really a for loop? I wanted to use numpy to be quicker than this, but not sure how to incorporate adsr otherwise.
        for i in range(0, size):
            self.noise.append(self.amplitude*adsrEnvelope(t[i],self.a,self.d,self.s,self.r)*self.oscili(2*np.pi*self.note*t[i]))        
        self.noise = np.array(self.noise)
        
        #convert to a signed 16 bit integer for pygame mixer stereo
        self.noise = (self.noise*65536).astype(np.int16)
        #reshape into a 2 dimensional array (stereo)
        self.noise = np.repeat(self.noise.reshape(size, 1), 2, axis = 1)
        np.save(self.string,self.noise)
        #get the sound and store it
        self.sound = sndarray.make_sound(self.noise)
        
    def play(self):
        #playback the sound on a random channel
        self.sound.play()
        return

oscilators = [guitarWave,triangleWave,squareWave]
instruments = []
for j in range(0, len(oscilators)):
    instruments.append([])
    for i in range(0,len(frequencies)):
        amp = 0.125
        instruments[j].append(Noise(frequencies[i],0.5,amp,oscilators[j]))

instrument = 0
pitch_offset = 0
num_instruments = len(oscilators)
instruments[0][0].play()
while(1): 
    try:
        for e in pygame.event.get():
            if(e.type == pygame.JOYAXISMOTION):
                print(e)
                if(e.axis == 0):
                    instrument=(round(e.value)+instrument)%num_instruments
                if(e.axis == 1):
                    pitch_offset+=round(e.value)
            if(e.type == pygame.JOYBUTTONDOWN):
                if(e.button==11):
                    pygame.quit()
                    break
                note = (e.button+pitch_offset)%len(instruments[instrument])
                instruments[instrument][e.button+pitch_offset].play()
    except Exception as e:
        print(e)
        break