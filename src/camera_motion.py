#!/usr/bin/env python

#python -m pip install Pillow

import sys, pygame
import pygame.camera
from PIL import Image
import PIL.ImageOps

#set resolution of camera
cam_h_rez = 320
cam_v_rez = 240

#initiate pygame and pycam
pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0",(cam_h_rez,cam_v_rez))
cam.start()


#screen size and color parameters
size = width, height = int(cam_h_rez + (cam_h_rez / 2)), int(cam_v_rez )
black = 0,0,0
red = 255,0,0
screen = pygame.display.set_mode(size)


#window title
pygame.display.set_caption("Motion Detect")


#threshholds (adjust to optimize for your lighting conditions)
rgb_thresh = 17 #camera sensitivity 
movement_thresh = 2 #motion sensitvity


#main loop
while 1:

	#quit on window exit
	for event in pygame.event.get():
		if event.type == pygame.QUIT:sys.exit()
	#reset screen to black
	screen.fill(black)
	
	#capture and convert first frame	
	buffer_1 = cam.get_image()
	buffer_1 = pygame.image.tostring(buffer_1, 'RGB')
	#buffer_1 = Image.fromstring('RGB', (cam_h_rez, cam_v_rez),  buffer_1)
	buffer_1 = Image.frombytes('RGB', (cam_h_rez, cam_v_rez),  buffer_1)

	pixels = buffer_1.load()
	

	#loop counters
	v_counter = 0
	h_counter = 0	
	past_image_value = []
	rgb_counter = 0
	

	#capture and convert second frame
	buffer_2 = cam.get_image()
	buffer_2 = pygame.image.tostring(buffer_2, 'RGB')
	#buffer_2 = Image.fromstring('RGB', (cam_h_rez, cam_v_rez),  buffer_2)
	buffer_2 = Image.frombytes('RGB', (cam_h_rez, cam_v_rez),  buffer_2)

	pixels2 = buffer_2.load()


	#loop 2
	while v_counter < cam_v_rez:
		while h_counter < cam_h_rez:


			#average out RGB values
			rgb_total1 = pixels[h_counter, v_counter]
			rgb_total2 = pixels2[h_counter, v_counter]
			rgb_1 = (rgb_total1[0] + rgb_total1[1] + rgb_total1[2]) / 3
			rgb_2 = (rgb_total2[0] + rgb_total2[1] + rgb_total2[2]) / 3


			#compare RGB values of first and second frame vased on thresholds
			if (rgb_1 - rgb_2) > rgb_thresh or (rgb_2 - rgb_1) > rgb_thresh:

				#gerate array to render as motion detection image
				#if motion detected add white pixel
				past_image_value.append((255,255,255))
				rgb_counter = rgb_counter + 255


			else:	

				#if motion not detected add black pixel
				past_image_value.append((0,0,0))
												
								
			h_counter = h_counter + 1	

			
		h_counter = 0
		v_counter = v_counter + 1
	

	#render image from array
	render_img = Image.new('RGB', (cam_h_rez, cam_v_rez))
	render_img.putdata(past_image_value)
	#render = render_img.tostring()
	render = render_img.tobytes()
	render = pygame.image.fromstring(render, (cam_h_rez, cam_v_rez), 'RGB')


	#if amount of motion detected on screen (white area) exceeds a certain threshold, flash screen red	
	if (rgb_counter / (cam_h_rez * cam_v_rez)) > movement_thresh:
		screen.fill(red)
			
	#pygame render
	screen.blit(render,(cam_v_rez / 3, 0))
	pygame.display.flip()




	

