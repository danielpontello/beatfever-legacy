#!/usr/bin/python

import pygame

pygame.init()
FakeScreen = pygame.display.set_mode((1600,600))
pygame.mixer.music.load('crush.mp3')
pygame.mixer.music.play()
while True:
	pygame.display.flip()
	
