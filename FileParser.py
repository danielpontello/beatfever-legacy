# This is a separate module for parser functions to be added.
# This is being created as static, so only one parser exists for the whole game.

from nota import Nota
from timingpoint import TimingPoint
from tools import *
import random
import math

def get_Name (osufile):
	Splitlines = osufile.split('\n')
	for Line in Splitlines:
		if len(Line) > 0:
			if Line.find('Title:', 0, len(Line)) != -1:
				title = Line.split(':', 1)
	return title[1].replace("\r", "")
	
def get_PreviewTime (osufile):
	Splitlines = osufile.split('\n')
	for Line in Splitlines:
		if len(Line) > 0:
			if Line.find('PreviewTime:', 0, len(Line)) != -1:
				time = Line.split(':', 1)
	return int(time[1])
				
def get_Artist (osufile):
	Splitlines = osufile.split('\n')
	for Line in Splitlines:
		if len(Line) > 0:
			if Line.find('Artist:', 0, len(Line)) != -1:
				artist = Line.split(':', 1)
	return artist[1].replace("\r", "")

def get_TimingPoints(osufile):
	Lines = osufile.split('\n')
	TimingPointString = []
	TimingPoints = []
	save = False;
	
	for line in Lines:
		if len(line) > 2:
			if save:
				TimingPointString.append(line)
		else:
			save = False
		if line.find("[TimingPoints]") != -1:
			save = True
	
	for point in TimingPointString:
		# self, offset, mpb, meter, sampleType, sampleSet, volume, inherited, kiai
		params = point.split(',')
		#print params
		offset = float(params[0])
		mpb = float(params[1])
		meter = int(params[2])
		sampleType = int(params[3])
		sampleSet = int(params[4])
		volume = int(params[5])
		inherited = int(params[6])
		kiai = int(params[7])
		
		newPoint = TimingPoint(offset, mpb, meter, sampleType, sampleSet, volume, inherited, kiai)		
		TimingPoints.append(newPoint)
	return TimingPoints
			
	
def get_NoteList (osufile, sprites, screen_width, screen_height, bpm):
	NoteList = []
	SplitLines = []
	#This function returns a list of notes with all their properties to the user
	#Make sure you have a list to receive it
	SplitLines = osufile.split('[HitObjects]\r\n', 1)
	SplitObjects = SplitLines[1].split('\n')
	for Line in SplitObjects:
		if len(Line) > 0:
			params = Line.split(',')
			posx = int(params[0])
			posy = int(params[1])
			time = int(params[2])
			ntype = int(params[3])
			IgnoreFirstLine = True
			if ntype == 1 or ntype == 5:
				nota = Nota(posx, posy, time, sprites[random.randint(0,3)], screen_width, screen_height, 1)
				NoteList.append(nota)
			elif ntype == 2 or ntype == 6:
				## THE GOD LINE
				## this.sliderTime = game.getBeatLength() * (hitObject.getPixelLength() / sliderMultiplier) / 100f;
				curva = params[5]
				repeat = int(params[6])
				pixellength = float(params[7])
				
				sliderEndTime = (bpm * (pixellength/1.4) / 100.0)
				
				curveParams = curva.split('|')[1:]
				
				xCoords = []
				for i in curveParams:
					xCoords.append(int(i.split(':')[0]))
					
				#notai = Nota(posx, posy, time, spritinhotexture, screen_width, screen_height)
				#NoteList.append(notai)
				
				numSteps = (int)(math.ceil(sliderEndTime * 0.01))
				#print(curveParams)
				SpriteValue = random.randint(0,3)
				for k in range(numSteps+1):
					t = float(k) / (numSteps)
					mnx = int(B(xCoords, 0, len(xCoords) - 1, t))
					#print("time: " + str(time))
					mny = time + (float(k)/float(numSteps)) * float(sliderEndTime)
					#print("mnx: " + str(mnx))
					#print("t: " + str(t))
					
					if t == 0 or t==1:
						notam = Nota(mnx, mny, mny, sprites[SpriteValue], screen_width, screen_height, 1)
					else:
						notam = Nota((random.randint(-11, 11)+mnx), mny, mny, sprites[4], screen_width, screen_height, 2)
					NoteList.append(notam)		
			elif ntype == 8 or ntype == 12:
					endTime = int(params[5])
					
					for i in range(20):
						notasp = Nota(random.randint(0, 512), posy, random.randint(time, endTime), sprites[5], screen_width, screen_height, 3)
						NoteList.append(notasp)
	return NoteList
			
			
def get_BreakPeriods(osufile):
	Lines = osufile.split('\n')
	BreakPString = []
	BreakPoints = []
	save = False;
	
	for line in Lines:
		if line.find("//") == -1:
			if save:
				BreakPString.append(line)
		else:
			save = False
		if line.find("//Break Periods") != -1:
			save = True
			
	for splitted in BreakPString:
		params = splitted.split(",")
		StartBreakTime = int(params[1])
		EndBreakTime = int(params[2])
		BreakPoints.append((StartBreakTime, EndBreakTime))
	#print(BreakPoints)
	return BreakPoints	
