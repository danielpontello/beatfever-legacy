#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
import pygame
import math
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(37, GPIO.OUT)
screen_width = 800
screen_height = 600

GameDisplay = pi3d.Display.create(x=100, y=100, w=screen_width, h=screen_height, background=(0,0,0,1), frames_per_second=60.0, use_pygame=False)
#what does use_pygame do anyways.. it doesnt seem to really change anything, even when i have a pygame window..

GameCamera = pi3d.Camera(is_3d=False)
SpriteShader = pi3d.Shader("uv_flat")
bgTexture = pi3d.Texture("res/bg_1080p.png", blend=False)
#in my game, setting this to True does nothing. Also, i really hope its not because the picture is a jpg..
bg = pi3d.ImageSprite(bgTexture, SpriteShader, w=screen_width, h=screen_height, z=3.0)

grape = pi3d.Texture("res/grape.png", blend=True)
grapeSprite = pi3d.ImageSprite(texture=grape, shader=SpriteShader, w=120.0, h=120.0, z=1.0)

alpha = 0.3
cont = 0
var = False
while GameDisplay.loop_running():
	cont+=1
	if cont % 5 == 0:
		var = not var
	if var:
		GPIO.output(37, 1)
	else:		
		GPIO.output(37, 0)
	print(var)
	grapeSprite.draw()
	grapeSprite.position(50,70, 1.0)
	bg.draw()
	#if i draw the grape after the bg, alpha works. however in my project this doesnt seem to happen.
	
	print(alpha)
	grapeSprite.set_alpha(alpha)
	
	
