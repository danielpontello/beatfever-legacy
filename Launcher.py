#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" ESC kills game."""
import pi3d
import pygame
import math
import os
import sys 
import subprocess
from nota import Nota
from tools import lerp
from song import Song
from FileParser import *
from pygame.locals import *
Gpio_IsSupported = True
#try:
	#import RPi.GPIO as GPIO
#except:
	#print("GPIO support not found. Skipping...")
	#Gpio_IsSupported = False	

#if Gpio_IsSupported:
	#GPIO.setmode(GPIO.BOARD)
	#GPIO.setup(37, GPIO.OUT)
	#GPIO.setup(38, GPIO.OUT)

screen_width = 1920
screen_height = 1080
noteblock = 0

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# ====================================== Variable Setup =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

pygame.mixer.pre_init(44100, 8, False, 1024)
pygame.init()
white    = (255, 255, 255)
bg = pygame.image.load("res/bg_1080p.png")
GameFont = pi3d.Font("fonts/DroidSansMono.ttf", font_size=48, image_size=256, color="#FFFFFF")

FakeScreen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
GameDisplayLauncher = pi3d.Display.create(x=0, y=0, w=screen_width, h=screen_height, background=(0,0.22,1,0), frames_per_second=60.0, use_pygame=True)
BlendShader = pi3d.Shader("uv_flat")
GameCamera = pi3d.Camera(is_3d=False)
SpriteShader = pi3d.Shader("uv_flat")


songs = []
selected = 0
for root, dirs, files in os.walk('songs'):
    for name in dirs:
        songs.append(name)

songsString = ""
songsList = []
Pi3dIsAPieceOfBullshit = []
for i in range(len(songs)):
	with open("songs/" + songs[i] + "/DataNew.osu", "r") as file:
		data = file.read()
		titleData = get_Name(data)
		artistData = get_Artist(data)
		previewTime = get_PreviewTime(data)
		songObj = Song(titleData, artistData, songs[i], previewTime)
		songsList.append(songObj)
		songsString = songsList[i].name + "\n"
		songsObject = pi3d.String(camera=GameCamera, font=GameFont, string=songsString, x=0, y=0, z=3.0, is_3d=False, size=0.40, justify="C")
		songsObject.set_shader(SpriteShader)
		Pi3dIsAPieceOfBullshit.append(songsObject)

title = pi3d.String(camera=GameCamera, font=GameFont, string="SONG SELECT", x=0, y=400, z=3.0, is_3d=False, size=0.60, justify="C")
title.set_shader(SpriteShader)
catcher = pi3d.ImageSprite("res/selector.png", SpriteShader, w=1920, h=100, z=4.0)
FrameTick = pygame.time.Clock()
FakeScreen.fill(white)
FlippedScreenFake = False
#=============================================================MAIN GAME LOOP

texty = 0
targety = 0
oldUpPressed = 0
oldDownPressed = 0
oldEnterPressed = 0
upPressed = 0
downPressed = 0
enterPressed = 0
selected = 0
changeSong = False
pygame.mixer.music.load('songs/' + songsList[selected].folder + '/Song.mp3')
#pygame.mixer.music.play(0, songsList[selected].previewTime)
pygame.mixer.music.play()

while GameDisplayLauncher.loop_running():
  if changeSong:
    pygame.mixer.music.load('songs/' + songsList[selected].folder + '/Song.mp3')
    pygame.mixer.music.play()
    changeSong = False
 # bg.position(0, 0, currentBeat+15.0)
 # bg.draw() 
  for event in pygame.event.get():
    if event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        print('Quit command received')
        GameDisplayLauncher.stop()
        pygame.quit()
        #GPIO.cleanup()
        
  catcher.draw()
  title.draw()
        
  oldUpPressed = upPressed
  oldDownPressed = downPressed
  oldEnterPressed = enterPressed
        
  upPressed = pygame.key.get_pressed()[K_UP]
  downPressed = pygame.key.get_pressed()[K_DOWN]  
  enterPressed = pygame.key.get_pressed()[K_SPACE]  
   
  if (oldUpPressed == 0 and upPressed != 0):
	  selected -= 1
	  changeSong = True
	  #print(str(selected))
	  
  if (oldDownPressed == 0 and downPressed != 0):
	  selected += 1
	  changeSong = True
	  #print(str(selected))
	  
  if (oldEnterPressed == 0 and enterPressed != 0):
	  song = songsList[selected]
	  GameDisplayLauncher.clear()
	  GameDisplayLauncher.destroy()
	  pygame.quit()
	  subprocess.call(["python", "OsuPi.py", song.folder])
	  
  selected = clamp(selected, 0, len(songsList)-1) 
	  
  for i in range(len(Pi3dIsAPieceOfBullshit)):
	  Pi3dIsAPieceOfBullshit[i].position(0, lerp(Pi3dIsAPieceOfBullshit[i].y(), ((i - selected- 1) * -90)-140, 0.5), 3.0)
	  Pi3dIsAPieceOfBullshit[i].draw()
	  
  
  texty = lerp(texty, targety, 0.5)
  
  #MenuString.position(0, texty - 40, 3.0)
  #MenuString.draw()
  #MenuString.quick_change(str(songsString))
  
  if not FlippedScreenFake:
    FakeScreen.blit(bg, (0,0,1920,1080))
    FlippedScreenFake = True
    pygame.display.flip()
			
