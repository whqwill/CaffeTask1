#!/usr/bin/env python

#---two parameters:the beginning number of images(default 1),the end number of image(default the last one)---#

#the number in prototype file should be ordered#

import sys
import os
from PIL import Image as image
from numpy import *

#fixed parameters
image_root = '/work/cv2/haiwang/data/CUB200-2011/images/'  #change
keyfile =  '/work/cv2/haiwang/data/CUB200-2011/parts/part_locs.txt' #change
mapfile =  '/work/cv2/haiwang/data/CUB200-2011/parts/images.txt' #change
prototype = '/work/cv2/haiwang/data/CUB200-2011/prototype6.txt' #change
original = 'original/'
normalized = 'normalization_old/' 
std_w = 150
std_h = 150
#head = (False,True,False,False,False,False,False,False,False,False,False,False,False,False,True)
K = 15 #the number of key points

#init parameters
keypoints = []
N = 0 #the number of images
B = 1 #the beginning number of images
keypoints_p = []
P = []

#read prototype parameters
pfile = open(prototype)
while True:
	line = pfile.readline()
	if line in (None,''): break
	data = map(int,line.split())
	box = tuple([data[1],data[2],data[3],data[4]])
	P.append((data[0],box))

#read keypoints of each image
key = open(keyfile)
line = key.readline()
while not line in (None,''):
	kpoint = []
	for i in range(K):
		kpoint.append((float(line.split()[2]),float(line.split()[3]),int(line.split()[4])))
		line = key.readline()
	keypoints.append(kpoint)
	N += 1
	for p in P:
		if p[0] == N:
			keypoints_p.append((p[1],kpoint))

#the range of images to be dealed with
if len(sys.argv) > 1:
	B = int(sys.argv[1])
if len(sys.argv) > 2: 
	N = int(sys.argv[2])

#normalization
if not os.path.isdir(image_root+normalized):
	os.mkdir(image_root+normalized)
imagemap = open(mapfile)

for i in range(B-1):
	imagemap.readline()

for i in range(B-1,N):
	#deal with directory
	path = imagemap.readline().split()[1]
	classpath = path.split('/')[0]+'/'
	print 'open',image_root+original+path,'...'
	im = image.open(image_root+original+path)
	if not os.path.isdir(image_root+normalized+classpath):
		print 'make dir',image_root+normalized+classpath,'...'
		os.mkdir(image_root+normalized+classpath)
	
	#store all parameters of each prototype for wraping 
	para_p = []
	for k_p in keypoints_p:
		box = k_p[0]
		kpoints_p = k_p[1] 

		#store Coordinate of key points
		Sp = 0; Mp = []; Mp_f_lr = []; Mi = []; #Mp_f_ud = [] 
		for j in range(K):
			if keypoints[i][j][2] == 1 and kpoints_p[j][2] == 1 and kpoints_p[j][0] >= box[0] and kpoints_p[j][0] <= box[2] and kpoints_p[j][1] >= box[1] and kpoints_p[j][1] <= box[3]:
				#print j,'test:',keypoints[i][j][0],keypoints[i][j][1],'prototype:',kpoints_p[j][0]-box[0],kpoints_p[j][1]-box[1]
				Mi.append([keypoints[i][j][0]-im.size[0]/2,keypoints[i][j][1]-im.size[1]/2])
				Mp.append([kpoints_p[j][0]-box[0],kpoints_p[j][1]-box[1]])
				Mp_f_lr.append([box[2]-kpoints_p[j][0],kpoints_p[j][1]-box[1]])
				#Mp_f_ud.append([kpoints_p[j][0]-box[0],box[3]-kpoints_p[j][1]])
				Sp += 1

		para_p.append((box,kpoints_p,Sp,Mp,Mi,0))
		para_p.append((box,kpoints_p,Sp,Mp_f_lr,Mi,1))
		#para_p.append((box,kpoints_p,Sp,Mp_f_ud,Mi,2))
	
	#select the best wraping parameters and relative wraping image	
	im_opt = im
	error_opt = -1 #means no value
	for para in para_p:
		
		box,kpoints_p,Sp,Mp,Mi,reversal = para

		w_new = box[2]-box[0]
		h_new = box[3]-box[1]
		
		if (Sp < 2):		
			continue

		#calculate parameters of 2D Similarity Transformation 
		Mp = matrix(Mp).T
		Mi = matrix(Mi).T 
		up = Mp.mean(1)
		ui = Mi.mean(1)
		Mp = Mp-up
		Mi = Mi-ui
		#print 'prototype',Mp.T
		#print up.A[0][0],up.A[1][0]
		
		#print im.size[0]/2+ui.A[0][0],im.size[1]/2+ui.A[1][0]
		U,S,V = linalg.svd(Mi*Mp.T)
		R = V.T*diag([1,linalg.det(V.T*U.T)])*U.T 
		s = trace(Mp.T*R*Mi)*1.0/trace(Mi.T*Mi)
		#print 'R',R
		#R.A[1][0] = -R.A[1][0]
		#R.A[0][1] = -R.A[0][1]
		#print 'R',R
		#print 's',s
		#print 'test'
		#calculate error
		error = 0.0
		for j in range(Sp):
			#print (s*R*Mi.T[j].T).A[0][0],(s*R*Mi.T[j].T).A[1][0]
			error += ((s*R*Mi.T[j].T).A[0][0]-Mp.T[j].T.A[0][0])**2 + ((s*R*Mi.T[j].T).A[1][0]-Mp.T[j].T.A[1][0])**2 			
		#print 'error',error
		#update optimal image
		if error_opt == -1 or error < error_opt:
			error_opt = error

			#crop image before 2D Similarity Transformation, let mean key points be the Coordinate origin
			modify = min(im.size[0]/2+ui.A[0][0],im.size[1]/2+ui.A[1][0],im.size[0]/2-ui.A[0][0],im.size[1]/2-ui.A[1][0])
			box_pre = [int(im.size[0]/2+ui.A[0][0]-modify),int(im.size[1]/2+ui.A[1][0]-modify),int(im.size[0]/2+ui.A[0][0]+modify),int(im.size[1]/2+ui.A[1][0]+modify)]
			im_tmp = im.crop(tuple(box_pre))

			#2D Similarity Transformation (rotate and resize)
			
			#if R.A[1][0] > 0:
			#	if R.A[0][0] >= 1:
			#		theta = arccos(1)
			#	else:
			#		theta = arccos(R.A[0][0])
			#else:
			#	if R.A[0][0] >= 1:
			#		theta = arccos(-1)+pi
			#	else:
			#		theta = arccos(-R.A[0][0])+pi
			theta = arccos(R.A[0][0])
			if R.A[1][0] > 0:
				theta = -theta
			#print 'rad2deg(theta)',rad2deg(theta)
			im_tmp = im_tmp.rotate(rad2deg(theta))
			im_tmp = im_tmp.resize((int(im_tmp.size[0]*s),int(im_tmp.size[1]*s)))

			#crop image after 2D Similarity Transformation, let image's size be the same as bounding box of prototype
			box_new = [int(max(im_tmp.size[0]/2-w_new/2,0)),int(max(im_tmp.size[1]/2-h_new/2,0)),int(min(im_tmp.size[0]/2+w_new/2,im_tmp.size[0])),int(min(im_tmp.size[1]/2+h_new/2,im_tmp.size[0]))]
			im_tmp = im_tmp.crop(tuple(box_new))

			im_opt = im_tmp
			if reversal == 1:
				im_opt = im_opt.transpose(image.FLIP_LEFT_RIGHT)
			if reversal == 2:
				im_opt = im_opt.transpose(image.FLIP_TOP_BOTTOM)

	#save image
	im_opt.resize((std_w,std_h)).save(image_root+normalized+path,'JPEG')
	#im_opt.save(image_root+normalized+path,'JPEG')
	




