# -*- coding: utf-8 -*-
"""
Created on Wed May 17 20:41:11 2023

@author: cpers
"""

import numpy as np
import sys

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

NOISE_IDLE = 0
NOISE_ATTACK = 1
NOISE_DECAY = 2
NOISE_SUSTAIN = 3
NOISE_RELEASE = 4
NOISE_COMPLETE= 5

def guitarWave(x,h=0.75,l=0.25,N=10):
    result = 0
    def A(n):
        return h/(np.pi*np.pi*(1-l)*n*n)*(np.sin(n*np.pi*l))
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

def generateADSRNoise(note,T,a,d,s,r,amplitude,oscili):
    size = round(fs*T)
    t=np.linspace(0,T,size)
    noise=[]
    for i in range(0,size):
        noise.append(amplitude*adsrEnvelope(t[i],a,d,s,r)*oscili(2*np.pi*note*t[i]))
    noise = np.array(noise)
    #convert to a signed 16 bit integer for pygame mixer stereo
    noise = (noise*65536).astype(np.int16)
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
        
        self.channel  = pygame.mixer.find_channel()
        
        self.stage   = NOISE_IDLE
        self.attack  = []
        self.decay   = []
        self.sustain = []
        self.release = []
        
        self.adsr(3*self.duration/10, 3*self.duration/10,3/10*self.duration,0.25*self.duration)
    
        #Generates all corresponding wave forms/files
        self.generateAll()
    
    @property
    def channel(self):
        return self._channel
    
    @channel.setter
    def channel(self,val):
        
        if type(val)=="NoneType" or val == None: 
            #print("Getting new Channel")
            self._channel = pygame.mixer.find_channel(True)
        else:
            #print("Setting channel to: ",val)
            self._channel = val
    
    def generateAll(self):
        self.generateWaveForm()
        self.generateAttack()
        self.generateDecay()
        self.generateSustain()
        self.generateRelease()
    
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
            self.noise.append(self.amplitude*adsrEnvelope(t[i],self.a,self.d,self.s,self.r)*self.oscili(2*np.pi*self.note*t[i]))        
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
            
    def play(self,stage=NOISE_COMPLETE):
       # print("Loop play...",stage,self.channel)
        try:
            #If releasing a sustained note, the channel will be busy
            #so in order to release it, we need to check the stage here
            #instead of later
            if stage == NOISE_RELEASE:
                # print("NOISE_RELEASE:",self.note)
                # print(self.channel)
                self.channel.stop()
                self.channel = self.release.play()
                return self.channel
                
            #if(self.channel.get_busy()): return self.channel
            
            if stage == NOISE_COMPLETE:
                self.channel = self.sound.play()
           
            elif stage == NOISE_ATTACK:
                self.channel = self.attack.play()
            elif stage == NOISE_DECAY:
                self.channel = self.decay.play()
            
            elif stage == NOISE_SUSTAIN:
                if(not self.channel.get_busy()):
                    self.channel = self.sustain.play(-1)
            
            return self.channel
        except AttributeError as e:
            #print(e)
            self.channel = pygame.mixer.find_channel(True)
            #pygame.mixer.stop()
            #sys.exit(1)
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
instruments[0][15].play()

ATTACKING = []
DECAYING = []
SUSTAINING = []
RELEASING = []
STOPPING =[]
print("All Instruments Loaded")

NOTE_PLAY=[]
for i in range(0,12):
    NOTE_PLAY.append(False)
   
while(1):
    try:
        for e in pygame.event.get():
            if(e.type == pygame.KEYDOWN):
                print("")
                if(e.key==pygame.K_LEFT):
                    
                    pitch_offset-=1
                if(e.key==pygame.K_RIGHT):
                    pitch_offset+=1                    
            if(e.type == pygame.JOYAXISMOTION):
                joy = e.joy
                if(e.axis == 0):
                    instrument=(round(e.value)+instrument)%num_instruments
                if(e.axis == 1):
                    print(ATTACKING,DECAYING,SUSTAINING,RELEASING)
                    pitch_offset+=round(e.value)
            if(e.type == pygame.JOYBUTTONDOWN):
                #print("BUTTON DOWN:", e.button)
                if(e.button==11):
                    STOPPING.extend(SUSTAINING)
                    STOPPING.extend(RELEASING)
                    STOPPING.extend(DECAYING)
                    STOPPING.extend(ATTACKING)
                    SUSTAINING = []
                    ATTACKING = []
                    RELEASING = []
                    DECAYING = []
                    continue
                if e.button not in ATTACKING:
                    ATTACKING.append(e.button)
                    
            if e.type == pygame.JOYBUTTONUP:
                if e.button in SUSTAINING:
                    SUSTAINING.remove(e.button)
                    RELEASING.append(e.button)
                    
        stage = NOISE_COMPLETE
        if(len(STOPPING)>0):
            for button in STOPPING:
                note = (button+pitch_offset)%len(instruments[instrument])
                instruments[instrument][note].stop()
                STOPPING.remove(button)
            pygame.mixer.stop()
            
        for button in RELEASING:
            note = (button+pitch_offset)%len(instruments[instrument])
            RELEASING.remove(button)
            instruments[instrument][note].play(stage=NOISE_RELEASE)
        
        for button in SUSTAINING:
            note = (button+pitch_offset)%len(instruments[instrument])
            instruments[instrument][note].play(stage=NOISE_SUSTAIN)
            
        for button in DECAYING:
            note = (button+pitch_offset)%len(instruments[instrument])
            #if(not instruments[instrument][note].channel.get_busy()):
            DECAYING.remove(button)
            SUSTAINING.append(button)
            #else:
            instruments[instrument][note].play(stage=NOISE_DECAY)
        
        for button in ATTACKING:
            note = (button+pitch_offset)%len(instruments[instrument])
        #    if(not instruments[instrument][note].channel.get_busy()):
            ATTACKING.remove(button)
            DECAYING.append(button)
         #   else:
            instruments[instrument][note].play(stage=NOISE_ATTACK)
        #print(SUSTAINING)
        #print(len(DECAYING))
    except AttributeError as e:
        print(e)
        break
    except Exception as e:
        print(e)
        break