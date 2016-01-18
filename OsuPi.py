#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" ESC kills game."""
import pi3d
import pygame
import math
import os
import sys
from nota import Nota
from tools import lerp
from FileParser import *
from pygame.locals import *
Gpio_IsSupported = True
try:
	import RPi.GPIO as GPIO
except:
	print("GPIO support not found. Skipping...")
	Gpio_IsSupported = False

if Gpio_IsSupported:
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(37, GPIO.OUT)
	GPIO.setup(38, GPIO.OUT)

screen_width = 1920
screen_height = 1080
noteblock = 0
song = sys.argv[1]

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# ====================================== Variable Setup =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

pygame.mixer.pre_init(44100, 8, False, 1024)
pygame.init()
white    = (255, 255, 255)

songs = []

KiaiTimeActive = False

for root, dirs, files in os.walk('songs'):
    for name in dirs:
        songs.append(name)

#print("Select song: ")

#for i in range(len(songs)):
#    print(str(i) + ". " + songs[i])

#index = int(raw_input())

# ====================================== SONG-LOADING STUFF ==========================================
with open("songs/" + song + "/DataNew.osu", "r") as file:
  data = file.read()
print("File read")
fileLines = data.split('\n')
lastTime = int(fileLines[len(fileLines)-2].split(',')[2])
print("Retrieving timing points..")
timingPoints = get_TimingPoints(data)

bpm = timingPoints[0].mpb
bpmPoints = []
bpmCounter = timingPoints[0].offset
numPoints = len(timingPoints)
breakPeriods = get_BreakPeriods(data)
currentBeat = 0
currentTimingPoint = 0
i = bpmCounter
print("Generating beat list..")
#for i in range(bpmCounter, lastTime):
while i < lastTime:
	if currentTimingPoint <= len(timingPoints)-2:
		if i >= timingPoints[currentTimingPoint+1].offset:
			if timingPoints[currentTimingPoint+1].mpb < 0:
				KiaiTimeActive = timingPoints[currentTimingPoint+1].kiai
				currentTimingPoint += 1
			else:
				bpm = timingPoints[currentTimingPoint+1].mpb
				KiaiTimeActive = timingPoints[currentTimingPoint+1].kiai
				currentTimingPoint += 1
	
	if i >= bpmCounter + bpm:
		bpmPoints.append((bpmCounter, KiaiTimeActive))
		bpmCounter += bpm
	i += 0.5
	#Variable i means precision for while loop that generates the beat table
	
pygame.mixer.music.load('songs/' + song + '/Song.mp3')

FakeScreen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
GameDisplay = pi3d.Display.create(x=0, y=0, w=screen_width, h=screen_height, background=(0,0.22,1,0), frames_per_second=60.0, use_pygame=True)
SpriteShader = pi3d.Shader("uv_flat")
BlendShader = pi3d.Shader("uv_flat")
GameCamera = pi3d.Camera(is_3d=False)

FrameTick = pygame.time.Clock()
FakeScreen.fill(white)

count = 0
notas = []

GameEdgeXLeft = -screen_width/2 +300
GameEdgeXRight = screen_width/2 -300

GameFont = pi3d.Font("fonts/DroidSansMono.ttf", font_size=96, color="#FFFFFF")
Gpio_LedCount = 0

#======================================== GAME INFO (scores, combos) ==================================
score_count = 0
score_lerp = 0
score_text = '0'.zfill(10)
ScoreString = pi3d.String(camera=GameCamera, font=GameFont, string=score_text, x=screen_width/2-55, y=screen_height/2-40, z=3.0, is_3d=False, size=0.20, justify="R")
ScoreString.set_shader(SpriteShader)

combo_count = 1
combo_text = '0   '
ComboString = pi3d.String(camera=GameCamera, font=GameFont, string=combo_text, x=screen_width/2+20, y=screen_height/2-100, z=3.0, is_3d=False, size=0.335, justify="C")
ComboString.set_shader(SpriteShader)

GameFont.blend = True
accuracy_text = '000.00%'
AccuracyString = pi3d.String(camera=GameCamera, font=GameFont, string=accuracy_text, x=screen_width/2-55, y=screen_height/2-110, z=3.0, is_3d=False, size=0.20, justify="R")
AccuracyString.set_shader(SpriteShader)

GameOverString = pi3d.String(camera=GameCamera, font=GameFont, string="Results", x=0, y=screen_height/2-110, z=3.0, is_3d=False, size=0.350, justify="C")
GameOverString.set_shader(SpriteShader)

stats = "Score: 0000000000000\n Accuracy: 100.00%\n Hit: 354x\n Miss: 120x\n\nThanks for playing!"
StatsString = pi3d.String(camera=GameCamera, font=GameFont, string=stats, x=0, y=0, z=3.0, is_3d=False, size=0.20, justify="C")
StatsString.set_shader(SpriteShader)
base_score = 300

#======================================== End of Var Setup =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
print("Loading sprites..")
#||||||||Sprite loading routine

pear = pi3d.Texture("res/pear.png", blend=True)
pearSprite = pi3d.ImageSprite(texture=pear, shader=SpriteShader, w=85.0, h=85.0, z=3.0)

grape = pi3d.Texture("res/grape.png", blend=True)
grapeSprite = pi3d.ImageSprite(texture=grape, shader=SpriteShader, w=85.0, h=85.0, z=3.0)

apple = pi3d.Texture("res/apple.png", blend=True)
appleSprite = pi3d.ImageSprite(texture=apple, shader=SpriteShader, w=85.0, h=85.0, z=3.0)

orange = pi3d.Texture("res/orange.png", blend=True)
orangeSprite = pi3d.ImageSprite(texture=orange, shader=SpriteShader, w=85.0, h=85.0, z=3.0)

banana = pi3d.Texture("res/banana.png", blend=True)
bananaSprite = pi3d.ImageSprite(texture=banana, shader=SpriteShader, w=85.0, h=85.0, z=3.0)

miniFruit = pi3d.ImageSprite("res/minifruit.png", SpriteShader, w=24.0, h=24.0, z=6.0)

sprites = [pearSprite, appleSprite, orangeSprite, grapeSprite, miniFruit, bananaSprite]

bg = pygame.image.load("res/bgnew.png")

#bgTexture = pi3d.Texture("res/pear.png", blend=False)
#bg = pi3d.ImageSprite(bgTexture, SpriteShader, w=1920, h=1080, z=6.0)

catcherTexture = pi3d.Texture("res/catcher.png", blend=True, mipmap=False)
catcher = pi3d.ImageSprite(catcherTexture, SpriteShader, w=(300.0)*0.8, h=(360)*0.8, z=4.0)

catcherTexture = pi3d.Texture("res/catcher.png", blend=True, mipmap=False)
catcher = pi3d.ImageSprite(catcherTexture, SpriteShader, w=(300.0)*0.8, h=(360)*0.8, z=4.0)

catcherTextureFlipped = pi3d.Texture("res/catcherflip.png", blend=True, mipmap=False)
catcherFlipped = pi3d.ImageSprite(catcherTextureFlipped, SpriteShader, w=(300.0)*0.8, h=(360)*0.8, z=4.0)

kiaiTexture = pi3d.Texture("res/miniglow.png", blend=True)
kiaiSpriteSide = pi3d.ImageSprite(kiaiTexture, SpriteShader, w=300, h=1080, z=3.2)
kiaiSpriteSide.position(-900, 0, 3.2)

kiaiTextureFlip = pi3d.Texture("res/miniglowFlip.png", blend=True)
kiaiSpriteSideFlip = pi3d.ImageSprite(kiaiTextureFlip, SpriteShader, w=300, h=1080, z=3.2)
kiaiSpriteSideFlip.position(900, 0, 3.2)

ApproveTexture = pi3d.Texture("res/pass.png", blend=True)
ApproveSprite = pi3d.ImageSprite(ApproveTexture, SpriteShader, w=470, h=364, z=3.2)
ApproveSprite.position(50000, 0, 3.2)

FailTexture = pi3d.Texture("res/fail.png", blend=True)
FailSprite = pi3d.ImageSprite(FailTexture, SpriteShader, w=470, h=468, z=3.2)
FailSprite.position(50000, 0, 3.2)

warningTexture = pi3d.Texture("res/get_ready.png", blend=True)
warnSprite = pi3d.ImageSprite(warningTexture, SpriteShader, w=554, h=77, z=3.2)
FailSprite.position(50000, 0, 3.2)


glowTex = pi3d.Texture("res/glow.png", blend=True, mipmap=False)
glows = []
currentGlow = 0
for i in range(0, 10):
	glow = pi3d.ImageSprite(glowTex, BlendShader, w=100, h=800, z=4.0)
	glow.position(3000, 3000, z=4.0)
	glows.append(glow)

#|||||||| End of Sprite loading

#=-=-=-= PARSER =-=-=-=-=
print("Parsing ingame notelist..")
notas = get_NoteList(data, sprites, screen_width, screen_height, bpm)

#=-=-=-=-=-=-=-=-=-=-=-=-=

pygame.mixer.music.play()
BeatTime = 0
previousFrameTime = 0
lastReportedPlayerPosition = 0
InterpolatedSongTime = 0
BeatCount = 0
BeatDelayBuffer = 0
CurrentBreak = 0
FrameCount = 0
x_catcher = 0
y_catcher = (-screen_height/2)+30
catcher.position(x_catcher, y_catcher, 4.0)
FlippedScreenFake = False
click = pygame.mixer.Sound('click.wav')
rightsound = pygame.mixer.Sound('res/sectionpass.wav')
wrongsound = pygame.mixer.Sound('res/sectionfail.wav')
normalHit = pygame.mixer.Sound("res/normalhit.wav")
tickHit = pygame.mixer.Sound("res/normaltick.wav")
normalHit.set_volume(0.4)
tickHit.set_volume(0.4)
click.set_volume(1.0)
NotaXGlob = 0
alphaKiai = 0
kiaiTimeActive = 0
kiaiDelay = 0
BreakActive = 0
BreakDelay = 0
BreakDraw = 0
CountDraw = 0
BreakAlpha = 0
WarnAlpha = 0
ShouldWarn = 0
WarnTime = 0

ReadyWarningTime = 0

catcherSpeed = 14
catcherFlopped = 0

kiaiSpriteSide.set_alpha(alphaKiai)
kiaiSpriteSideFlip.set_alpha(alphaKiai)

hitnotes = 0
totalnotes = 0
accuracy = 100
maxcombo = 0
gameover = False
print("Starting gameloop.")
#=============================================================MAIN GAME LOOP

while GameDisplay.loop_running(): 
 if not FlippedScreenFake:
   FakeScreen.blit(bg, (0,0,1920,1080))
   FlippedScreenFake = True
   pygame.display.flip()
	
 for event in pygame.event.get():
   if event.type == KEYDOWN:
     if event.key == K_ESCAPE:
       print('Quit command received')
       GameDisplay.stop()
       pygame.quit()
       GPIO.cleanup()
        
 if not gameover:
  GPIO.output(37, 0)
 # bg.position(0, 0, currentBeat+15.0)
 # bg.draw() 
  if alphaKiai > 0:
	  alphaKiai -= 0.04
	  
  if BreakAlpha >= 0 and accuracy >= 65.0:
	  BreakAlpha -= 0.01
	  ApproveSprite.set_alpha(BreakAlpha)
	  ApproveSprite.position(0, 0, 2)
	  ApproveSprite.draw()
  elif BreakAlpha >= 0 and accuracy < 65.0:
	  BreakAlpha -= 0.01
	  FailSprite.set_alpha(BreakAlpha)
	  FailSprite.position(0, 0, 2)
	  FailSprite.draw() 
  else:
	  FailSprite.position(5000, 0, 0)
	  ApproveSprite.position(5000, 0, 0)
  
  if ReadyWarningTime < InterpolatedSongTime and WarnAlpha > 0:
	  warnSprite.position(0, 400, 1)
	  warnSprite.draw()
	  WarnAlpha -= 0.009
	  warnSprite.set_alpha(WarnAlpha)
	  WarnTime += 1
	    
  if WarnAlpha <= 0:
	  warnSprite.position(0, 49284, 0)
	  
	  
  if kiaiTimeActive == 1:
   kiaiSpriteSide.draw()
   kiaiSpriteSide.set_alpha(alphaKiai)
   kiaiSpriteSideFlip.draw()
   kiaiSpriteSideFlip.set_alpha(alphaKiai)
        
  # Input  
  if(pygame.key.get_pressed()[K_LSHIFT] != 0):
      catcher_speed = 48
  else:
      catcher_speed = 24
  
  if (pygame.key.get_pressed()[K_RIGHT] != 0):
	  x_catcher += catcher_speed
	  catcherFlopped = 0
  if (pygame.key.get_pressed()[K_LEFT] != 0):
	  x_catcher -= catcher_speed
	  catcherFlopped = 1
    
  if combo_count > maxcombo:
    maxcombo = combo_count
  
  for glow in glows:
	if glow.alpha() <= 0:
		glow.position(3000, 3000, 9.0)
	else:
		glow.position(x_catcher, y_catcher+140, currentBeat+5)
		glow.set_alpha(glow.alpha()-0.13)
		glow.draw()

  
  
  x_catcher = clamp(x_catcher, GameEdgeXLeft, GameEdgeXRight)
  catcher.position(x_catcher, y_catcher, 4.0)
  catcherFlipped.position(x_catcher, y_catcher, 4.0)
  
  
  
  if(catcherFlopped == 1):
	  catcherFlipped.draw()
  else:
	  catcher.draw()
  
  # Lerpa o score pra dar aquele $wang
  score_lerp = int(math.ceil(lerp(score_lerp, score_count, 0.2)))
  score_text = str(score_lerp).zfill(10)
  
 
  ComboString.position(x_catcher, 0, 4.0)
  ComboString.draw()
  ScoreString.draw()
  AccuracyString.draw()
  ComboString.quick_change(str(combo_text))
  ScoreString.quick_change(str(score_text))
  AccuracyString.quick_change(str(accuracy_text))
  
  # TIMER INTERPOLATION
  count += 1
  
  timer = FrameTick.tick()
  previousFrameTime = timer

  if pygame.mixer.music.get_pos() != lastReportedPlayerPosition:
	  InterpolatedSongTime = (InterpolatedSongTime + pygame.mixer.music.get_pos())/2
	  lastReportedPlayerPosition = pygame.mixer.music.get_pos()
  
  if InterpolatedSongTime >= bpmPoints[currentBeat][0] and currentBeat < len(bpmPoints)-1:  
	GPIO.output(37, 1)
	currentBeat += 1
	#print((str)(BeatFrames))
	if bpmPoints[currentBeat][1] == 1:
		if kiaiDelay < 3:
			kiaiDelay += 1
		else:
			alphaKiai = 1
			kiaiTimeActive = 1
			GPIO.output(38, 1)
	else:
		if kiaiDelay == 3:
			kiaiDelay -= 1
		else:
			kiaiTimeActive = 0
		#print("No kiai time. Current beat is " + str(currentBeat) )
  #print(breakPeriods[CurrentBreak][1] - 1800)
  
  if len(breakPeriods) > 0:
	if CurrentBreak < len(breakPeriods):	
		if InterpolatedSongTime >= ((breakPeriods[CurrentBreak][1]-breakPeriods[CurrentBreak][0])/2) + breakPeriods[CurrentBreak][0]:
			ReadyWarningTime = breakPeriods[CurrentBreak][1] - 1800
			BreakActive = 1
			ShouldWarn = 1
			if accuracy >= 65.0:  
				rightsound.play()
				CurrentBreak += 1
				BreakAlpha = 1
				WarnAlpha = 1
			else:
				wrongsound.play()
				CurrentBreak += 1
				BreakAlpha = 1
				WarnAlpha = 1
		elif InterpolatedSongTime >= breakPeriods[CurrentBreak][1]: 
			BreakActive = 0
			ShouldWarn = 0


  for nota in notas[noteblock:noteblock+23]:
    if nota.outofscreen() and nota.get_removed() == False:
      noteblock += 1
      nota.set_removed()
      if nota.notetype != 3:
		totalnotes += 1
      if nota.notetype == 1:
		combo_count = 1
		combo_text = (str(combo_count))
      
    nota.sprite.draw()
    nota.update(InterpolatedSongTime)
    
    if totalnotes != 0:
		accuracy = (hitnotes/totalnotes)*100
		accuracy_text = "{0:.2f}%".format(accuracy)
    
    if nota.y <= y_catcher + 110 and nota.get_removed() == False and nota.y >= y_catcher + 75:
		if nota.x >= x_catcher-130 and nota.x <= x_catcher + 130:
			NotaXGlob = nota.x
			noteblock += 1
			hitnotes += 1
			totalnotes += 1
			nota.x = -200000
			combo_text = ((str)(combo_count))
			ComboString.quick_change(combo_text)
			nota.set_removed()
			if nota.notetype == 1:
				combo_count += 1
				score_count += base_score * combo_count
				glows[currentGlow%10].position(x_catcher, y_catcher+140, 9.0)
				glows[currentGlow%10].set_alpha(1.0)
				currentGlow += 1
				normalHit.play()
			else:
				score_count += base_score/3 * combo_count
				tickHit.play()
			if Gpio_IsSupported:
				GPIO.output(38, 1)
	#			Gpio_LedCount = 3
	#============================		
		
    
  #if count % 23 == 0:
    #print('Audio timer: '+(str)(pygame.mixer.music.get_pos()))
    #print('FPS: ' + (str)(1000/timer))
    #print('Noteblock Buffer: ' + str(noteblock))
    ##GPIO.output(37,1)
	
  if currentBeat == len(bpmPoints)-1:
   if InterpolatedSongTime >= bpmPoints[currentBeat][0] + 10000:
    gameover = True
    print("Game over.")
    print('Score:' + (str)(score_count))
    print('Accuracy:' + (str)(accuracy))
    print('Hit Notes:' + (str)(hitnotes))
    print('Max Combo:' + (str)(maxcombo))
    #GameDisplay.stop()
    #pygame.quit()
    #GPIO.cleanup()
 else:
  stats = "Score: " + (str)(score_count) + "\nAccuracy: " + (str)(accuracy) + "\nHit: " + (str)(hitnotes) + "\nMiss: " + (str)(hitnotes-totalnotes) + "\n\nThanks for playing!\n Press Space to exit."
  StatsString.quick_change(str(stats))
  GameOverString.draw()
  StatsString.draw()
