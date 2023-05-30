# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:05:56 2023

@author: cpers
"""

from audio import *
import numpy as np
import pygame
from pygame import joystick, sndarray

pygame.init()
joystick.init()
joysticks = [joystick.Joystick(x) for x in range(joystick.get_count())]
for joy in joysticks:
    joy.init()

def triangleWave(x,freq):
    #f(aX) = ax%3 --> period 3/a
    return (x%(2*np.pi))/(2*np.pi)-0.5

def sineWave(x, freq=1):
    return np.sin(2*np.pi*freq*x)

def cosineWave(x,freq=1):
    return np.cos(2*np.pi*freq*x)

def squareWave(x, freq):
    return triangleWave(-x+np.pi,freq)+triangleWave(x,freq)

def pianoWave(x,freq, L=1,v=0.23, l = 0.23, N=5):
    c = freq*L/np.pi
    
    def k(n):
        return n*np.pi/L
    def w(n):
        return c*n*np.pi/L
    
    def B(n):
        return 2*v/w(n)*np.sin(n*np.pi*l/L)
    
    result=0
    for i in range(1,N+1):
        result+=B(i)*np.sin(w(i)*x)
    return result

def guitarWave(x,freq, h=0.3,l=0.5,N=5,tau = 6):
    result = 0
    c = 425 #meters/sec
    L = (c*np.pi)/freq
    l = l*L
    def k(n):
        return n*np.pi/L
    #harmonic frequencies
    #note that w(1) = freq == base harmonic
    def w(n):
        return c*n*np.pi/L
    
    def A(n):
        return h/(np.pi*np.pi*l/L*(1-l/L)*n*n)*(np.sin(n*np.pi*l/L))
    
    for i in range(1,N+1):
        result+=A(i)*np.cos(w(i)*x)*pow(np.exp(1),-x*i/tau)
    return result

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

def generateADSRNoise(note,T,a,d,s,r,amplitude,oscili):
    size = round(fs*T)
    t=np.linspace(0,T,size)
    noise=[]
    for i in range(0,size):
        noise.append(amplitude*adsrEnvelope(t[i],a,d,s,r)*oscili(2*np.pi*t[i],note))
    noise = np.array(noise)
    #convert to a signed 16 bit integer for pygame mixer stereo
    noise = (noise*65536/2).astype(np.int16)
    #reshape into a 2 dimensional array (stereo)
    noise = np.repeat(noise.reshape(size, 1), 2, axis = 1)
    return noise

class Noise:
    def __init__(self, note, duration=0.25, amplitude=0.125,oscili = np.sin):
        self.note      = note
        self.period    = 1/note
        self.duration  = duration
        self.amplitude =  amplitude
        self.oscili = oscili
        
        self.channel  = pygame.mixer.find_channel(True)
        
        self.attack  = []
        self.decay   = []
        self.sustain = []
        self.release = []
        
        self.adsr(self.duration/10, self.duration/10,3/10*self.duration,0.5*self.duration)
    
        #Generates all corresponding wave forms/files
        self.generateAll()
    
    def generateAll(self):
        self.generateWaveForm()
        #self.generateAttack()
        #self.generateDecay()
        #self.generateSustain()
        #self.generateRelease()
    
    def adsr(self,a,d,s,r):
        self.a = a
        self.d = d
        self.s = s
        self.r = r
        
    
    def generateAttack(self):
        string = f"Attack{self.a}{round(self.note)}{self.duration}{self.amplitude}{self.oscili.__name__}"
        string = "./.npyaudio/"+string.replace(".","")+".npy"
        noise = []
        try:
            noise = np.load(string)
            self.attack=sndarray.make_sound(noise)
            return
        except:
            pass
        
        noise =  generateADSRNoise(self.note,self.a,self.a,0,0,0,self.amplitude,self.oscili)
        np.save(string,noise)
        self.attack=sndarray.make_sound(noise)
        
    def generateDecay(self):
        string = f"Decay{self.d}{round(self.note)}{self.duration}{self.amplitude}{self.oscili.__name__}"
        string = "./.npyaudio/"+string.replace(".","")+".npy"
        noise = []
        try:
            noise = np.load(string)
            self.decay=sndarray.make_sound(noise)
            return
        except:
            pass
        
        noise =  generateADSRNoise(self.note,self.d,0,self.d,0,0,self.amplitude,self.oscili)
        np.save(string,noise)
        self.decay=sndarray.make_sound(noise)
   
    def generateSustain(self):
        string = f"Sustain{round(self.note)}{self.duration}{self.amplitude}{self.oscili.__name__}"
        string = "./.npyaudio/"+string.replace(".","")+".npy"
        noise = []
        try:
            noise = np.load(string)
            self.sustain=sndarray.make_sound(noise)
            return
        except:
            pass
        noise =  generateADSRNoise(self.note,self.period,0,0,self.period,0,self.amplitude,self.oscili)
        np.save(string,noise)
        
        self.sustain=sndarray.make_sound(noise)
        
    def generateRelease(self):
        string = f"Release{self.r}{round(self.note)}{self.duration}{self.amplitude}{self.oscili.__name__}"
        string = "./.npyaudio/"+string.replace(".","")+".npy"
        noise = []
        try:
            noise = np.load(string)
            self.release=sndarray.make_sound(noise)
            return
        except:
            pass
        
        noise =  generateADSRNoise(self.note,self.r,0,0,0,self.r,self.amplitude,self.oscili)
        np.save(string,noise)
        self.release=sndarray.make_sound(noise)
    
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
            self.noise.append(self.amplitude*adsrEnvelope(t[i],self.a,self.d,self.s,self.r)*self.oscili(2*np.pi*t[i],self.note))        
        self.noise = np.array(self.noise)
        
        #convert to a signed 16 bit integer for pygame mixer stereo
        self.noise = (self.noise*65536).astype(np.int16)
        #reshape into a 2 dimensional array (stereo)
        self.noise = np.repeat(self.noise.reshape(size, 1), 2, axis = 1)
        np.save(self.string,self.noise)
        #get the sound and store it
        self.sound = sndarray.make_sound(self.noise)
        
    def stop(self):
        self.channel.stop()
            
    def play(self):
        return self.sound.play()
    
oscilators = [guitarWave]
instruments = []
print("Building Audio Samples...")
for j in range(0, len(oscilators)):
    instruments.append([])
    for i in range(0,len(frequencies)):
        amp = 0.125
        instruments[j].append(Noise(frequencies[i],5,amp,oscilators[j]))
        #print(dir(instruments[j][i].channel))
print("Done!")
instrument = 0
pitch_offset = 0
num_instruments = len(oscilators)
for i in [0,12,24,36]:
    instruments[0][i].play()
    pygame.time.delay(500)
BUTTON_STATE=[]
for i in range(0,12):
    BUTTON_STATE.append(0)
while(1):
    for i in range(0,12):
        BUTTON_STATE[i]=joystick.Joystick(0).get_button(i)
    try:
        for e in pygame.event.get():
            if(e.type == pygame.KEYDOWN):
                if(e.key==pygame.K_LEFT):                    
                    pitch_offset-=1
                if(e.key==pygame.K_RIGHT):
                    pitch_offset+=1                    
            if(e.type == pygame.JOYAXISMOTION):
                joy = e.joy
                if(e.axis == 0):
                    instrument=(round(e.value)+instrument)%num_instruments
                if(e.axis == 1):
                    pitch_offset+=round(e.value)
            if e.type == pygame.JOYBUTTONDOWN:
                #print("BUTTON DOWN:", e.button)
                if(e.button==11):
                    pygame.quit()
                    break
                note = (e.button+pitch_offset)%len(instruments[instrument])
                instruments[instrument][note].play()
            if e.type == pygame.JOYBUTTONUP:
                pass
            
    except:
        pass
            