#!/usr/bin/env python

#---two parameters:the beginning number of images(default 1),the end number of image(default the last one)---#

#the number in prototype file should be ordered#

import sys
import os
from numpy import *
from PIL import Image as image

#things to modify:
#done 1. read the key points of each image advance in an array 
#done 2. implement a function that can compute bounding box using boolean key points array 
#done 3. implement the first version: modify getting bounding box of prototype from file to from function below
#	 								 add a determining condition "if head[k]" during store Coordinate of key points
#4. pre resize *
#done 5. change wapping image from PIL to opencv 
#6. implement the second version:don't use reading prototype parameters,
#								 instead loop all images, find a best one whoes avarage distance error is the min one 
#7. implement the third version: loop all images and all key points, 
#								 find a best one and best M-nearest ksy points whoes avarage distance error is the min one 
#                                modify M 
#8. implement the fouth version: loop all images and all key points and store a best prototype arrays (L length) 
#								 each time, if length > L, select L best results
#								 modify lambda


def buldbox(kpoint,kfalg):
	box = [INFINITY,INFINITY,-1,-1] 

	for i in range(len(kpoint)):
		if kpoint[i][2] == 1 and kfalg[i]:
			if kpoint[i][0] < box[0]:
				box[0] = kpoint[i][0]
			if kpoint[i][0] > box[2]:
				box[2] = kpoint[i][0]
			if kpoint[i][1] < box[1]:
				box[1] = kpoint[i][1]
			if kpoint[i][1] > box[3]:
				box[3] = kpoint[i][1]

	if box[0] == INFINITY or box[1] == INFINITY or box[2] == -1 or box[3] == -1:
		return -1

	#print (box[2]-box[0])*1.0/(box[3]-box[1])
	if box[3]-box[1]==0 or box[2]-box[0]== 0.05:
		return -1

	if (box[2]-box[0])*1.0/(box[3]-box[1]) > 20 or (box[2]-box[0])*1.0/(box[3]-box[1]) < 0.05:
		return -1

	if kfalg[0] == True:
		if 0.2*(box[2]-box[0]) > ex_min:
			add_w = 0.2*(box[2]-box[0])
		else:
			add_w = ex_min

		if 0.2*(box[3]-box[1]) > ex_min:
			add_h = 0.2*(box[3]-box[1])
		else:
			add_h = ex_min

		box[0] = int(box[0]-add_w)
		box[1] = int(box[1]-add_h)
		box[2] = int(box[2]+add_w)
		box[3] = int(box[3]+add_h)
	elif (box[2]-box[0])*1.0/(box[3]-box[1]) > 2:
		if 0.3*ex_rate*(box[2]-box[0]) > ex_min:
			add_w = 0.3*ex_rate*(box[2]-box[0])
		else:
			add_w = ex_min

		if ex_rate*(box[3]-box[1]) > ex_min:
			add_h = ex_rate*(box[3]-box[1])
		else:
			add_h = ex_min

		box[0] = int(box[0]-add_w)
		box[1] = int(box[1]-add_h)
		box[2] = int(box[2]+add_w)
		box[3] = int(box[3]+add_h)
	elif (box[2]-box[0])*1.0/(box[3]-box[1]) < 0.5:
		if ex_rate*(box[2]-box[0]) > ex_min:
			add_w = ex_rate*(box[2]-box[0])
		else:
			add_w = ex_min

		if 0.3*ex_rate*(box[3]-box[1]) > ex_min:
			add_h = 0.3*ex_rate*(box[3]-box[1])
		else:
			add_h = ex_min

		box[0] = int(box[0]-add_w)
		box[1] = int(box[1]-add_h)
		box[2] = int(box[2]+add_w)
		box[3] = int(box[3]+add_h)		
	else:
		if ex_rate*(box[2]-box[0]) > ex_min:
			add_w = ex_rate*(box[2]-box[0])
		else:
			add_w = ex_min

		if ex_rate*(box[3]-box[1]) > ex_min:
			add_h = ex_rate*(box[3]-box[1])
		else:
			add_h = ex_min

		box[0] = int(box[0]-add_w)
		box[1] = int(box[1]-add_h)
		box[2] = int(box[2]+add_w)
		box[3] = int(box[3]+add_h)		

	return (int(box[0]),int(box[1]),int(box[2]),int(box[3]))

def dis(a,b):
	return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5

def cpro(x,y,z):
	a = [z[0]-x[0],z[1]-x[1]]
	b = [y[0]-x[0],y[1]-x[1]]
	return a[0]*b[1]-a[1]*b[0]

def from16to5(p1,p3):
	p2 = [0,0]
	pa = [117.0 ,128.0]
	pb = [145.0 ,91.0]
	pc = [159.0 ,101.0]
	W = dis(pa,pc)
	S = abs(cpro(pa,pb,pc))
	H = S/W
	lam = (dis(pa,pb)**2-H**2)**0.5/W
	w = dis(p1,p3)
	h = H/W*w
	p0 = [(p3[0]-p1[0])*lam+p1[0],(p3[1]-p1[1])*lam+p1[1]]
	de = arccos((p3[0]-p1[0])/w)+pi/2
	#de = math.arcsin((p3[1]-p1[1])/w)+math.pi/2
	co = cos(de)
	si = sin(de)
	p2 = [p0[0]+h*co,p0[1]+h*si]
	return p2

def from15to6(p1,p3):
	p2 = [0,0]
	pa = [117.0 ,128.0]
	pc = [145.0 ,91.0]
	pb = [159.0 ,101.0]
	W = dis(pa,pc)
	S = abs(cpro(pa,pb,pc))
	H = S/W
	lam = (dis(pa,pb)**2-H**2)**0.5/W
	w = dis(p1,p3)
	h = H/W*w
	p0 = [(p3[0]-p1[0])*lam+p1[0],(p3[1]-p1[1])*lam+p1[1]]
	de = arccos((p3[0]-p1[0])/w)-pi/2
	#de = math.arcsin((p3[1]-p1[1])/w)+math.pi/2
	co = cos(de)
	si = sin(de)
	p2 = [p0[0]+h*co,p0[1]+h*si]
	return p2

def from110to5(p1,p3):
	p2 = [0,0]
	pa = [117.0 ,128.0]
	pb = [89.0 ,91.0]
	pc = [75.0 ,101.0]
	W = dis(pa,pc)
	S = abs(cpro(pa,pb,pc))
	H = S/W
	lam = (dis(pa,pb)**2-H**2)**0.5/W
	w = dis(p1,p3)
	h = H/W*w
	p0 = [(p3[0]-p1[0])*lam+p1[0],(p3[1]-p1[1])*lam+p1[1]]
	de = arccos((p3[0]-p1[0])/w)+pi/2
	#de = math.arcsin((p3[1]-p1[1])/w)+math.pi/2
	co = cos(de)
	si = sin(de)
	p2 = [p0[0]+h*co,p0[1]+h*si]
	return p2

def from15to10(p1,p3):
	p2 = [0,0]
	pa = [117.0 ,128.0]
	pc = [89.0 ,91.0]
	pb = [75.0 ,101.0]
	W = dis(pa,pc)
	S = abs(cpro(pa,pb,pc))
	H = S/W
	lam = (dis(pa,pb)**2-H**2)**0.5/W
	w = dis(p1,p3)
	h = H/W*w
	p0 = [(p3[0]-p1[0])*lam+p1[0],(p3[1]-p1[1])*lam+p1[1]]
	de = arccos((p3[0]-p1[0])/w)-pi/2
	#de = math.arcsin((p3[1]-p1[1])/w)+math.pi/2
	co = cos(de)
	si = sin(de)
	p2 = [p0[0]+h*co,p0[1]+h*si]
	return p2

#fixed parameters
#image_root = '/Users/will/Documents/hiwi/3/images/'  #change
#keyfile =  '/Users/will/Documents/hiwi/3/part/part_locs.txt' #change
#mapfile =  '/Users/will/Documents/hiwi/3/part/images.txt' #change
#prototype = '/Users/will/Documents/hiwi/3/proto_order_num1.txt' #change
#original = 'original/'
#normalized = 'normalization/' 
image_root = '/work/cv2/haiwang/data/CUB200-2011/images/'  #change
keyfile =  '/work/cv2/haiwang/data/CUB200-2011/parts/part_locs.txt' #change
mapfile =  '/work/cv2/haiwang/data/CUB200-2011/parts/images.txt' #change
prototype = '/work/cv2/haiwang/data/CUB200-2011/parts/proto_order.txt' #change
original = 'original/'
normalized = 'normalization/' 
ex_rate = 1.5
ex_min = 5
INFINITY = 100000
std_w = 150.0
std_h = 150.0
fix_K = 4
E0 = 0.5 
E1 = 0.5
head = (False,True,False,False,True,True,True,False,False,True,True,False,False,False,True)
#		1     2    3     4     5    6    7    8     9     10    11   12    13    14    15
full = (True,True,True,True,True,True,True,True,True,True,True,True,True,True,True)
K = 15 #the number of key points

#init parameters
keypoints = []
keypoints_p = []
N = 0 #the number of images
B = 1 #the beginning number of images
Np = int(sys.argv[1])

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

#read prototype 
pro = open(prototype)
for i in range(Np):
	data = pro.readline().split()
	keypoints_p.append([keypoints[int(data[0])],(int(data[1]),int(data[2]),int(data[3]),int(data[4]))])

#the range of images to be dealed with
if len(sys.argv) > 2:
	B = int(sys.argv[2])
if len(sys.argv) > 3: 
	N = int(sys.argv[3])

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

	im_size = im.size

	#select the best prototype  
	error_opt = -1
	im_opt = im
	for [kpoints_p,k_set] in keypoints_p:

		flag_k = [False for k in range(K)]
		for k in range(fix_K):
			flag_k[k_set[k]] = True

		box = buldbox(kpoints_p,flag_k)
		w_s = std_w/(box[2]-box[0])
		h_s = std_h/(box[3]-box[1])

		M = [] 
		M_f = []
		flag_k_f = []
		for j in range(K):
			if flag_k[j]:
				M.append([(kpoints_p[j][0]-box[0])*w_s,(kpoints_p[j][1]-box[1])*h_s])
				M_f.append([(box[2]-kpoints_p[j][0])*w_s,(kpoints_p[j][1]-box[1])*h_s])
			flag_k_f.append(flag_k[j])

		flag_k_f[6] = flag_k[10]
		flag_k_f[10] = flag_k[6]
		
		M = matrix(M).T
		u = M.mean(1)
		M = M-u

		M_f = matrix(M_f).T
		u_f = M_f.mean(1)
		M_f = M_f-u_f

		Mps = [(M,0,flag_k),(M_f,1,flag_k_f)]

		for [Mp,reversal,flag] in Mps:

			Mi = []
			flag_match = True
			for j in range(K):	
				if flag[j]:
					if keypoints[i][j][2] == 1:
						Mi.append([keypoints[i][j][0]-im_size[0]/2,keypoints[i][j][1]-im_size[1]/2])
					else:
						flag_match = False
						break
			Mi = matrix(Mi).T
			ui = Mi.mean(1)
			Mi = Mi-ui

			if not flag_match:
				continue

			#calculate parameters of 2D Similarity Transformation 
			U,S,V = linalg.svd(Mi*Mp.T)
			R = V.T*diag([1,linalg.det(V.T*U.T)])*U.T 
			s = trace(Mp.T*R*Mi)*1.0/trace(Mi.T*Mi)

			error = 0.0
			for j in range(fix_K):
				error += ((s*R*Mi.T[j].T).A[0][0]-Mp.T[j].T.A[0][0])**2 + ((s*R*Mi.T[j].T).A[1][0]-Mp.T[j].T.A[1][0])**2 			

			if error_opt == -1 or error < error_opt:
				error_opt = error

				#crop image before 2D Similarity Transformation, let mean key points be the Coordinate origin
				modify = max(im.size[0]/2+ui.A[0][0],im.size[1]/2+ui.A[1][0],im.size[0]/2-ui.A[0][0],im.size[1]/2-ui.A[1][0])
				box_pre = [int(im.size[0]/2+ui.A[0][0]-modify),int(im.size[1]/2+ui.A[1][0]-modify),int(im.size[0]/2+ui.A[0][0]+modify),int(im.size[1]/2+ui.A[1][0]+modify)]
				im_tmp = im.crop(tuple(box_pre))

				#2D Similarity Transformation (rotate and resize)
				if R.A[0][0]>1.0:
					theta = arccos(1.0)
				else:
					theta = arccos(R.A[0][0])
				if R.A[1][0] > 0:
					theta = -theta
				im_tmp = im_tmp.rotate(rad2deg(theta))

				#crop image after 2D Similarity Transformation, let image's size be the same as bounding box of prototype
				w_new = (box[2]-box[0])*w_s/s;
				h_new = (box[3]-box[1])*h_s/s;
				box_new = [int(max(im_tmp.size[0]/2-w_new/2,0)),int(max(im_tmp.size[1]/2-h_new/2,0)),int(min(im_tmp.size[0]/2+w_new/2,im_tmp.size[0])),int(min(im_tmp.size[1]/2+h_new/2,im_tmp.size[0]))]
				im_tmp = im_tmp.crop(tuple(box_new))

				im_opt = im_tmp 
				if i == 478:
					print k_set
				
				if k_set[2] == 10 or reversal == 1:
				#if keypoints[i][10][2] == 1:
					im_opt = im_opt.transpose(image.FLIP_LEFT_RIGHT)

	#save image
	if error_opt == -1:
		box = buldbox(keypoints[i],head)
		print "head"
		if box == -1:
			print "full"
			box = buldbox(keypoints[i],full)
		if box == -1:
			print "error"
			exit(0)
		im_opt = im.crop(box)
		if keypoints[i][10][2] == 1 or (keypoints[i][1][0] > max(keypoints[i][4][0],keypoints[i][5][0],keypoints[i][6][0],keypoints[i][9][0],keypoints[i][14][0])) or (keypoints[i][9][0] < max(keypoints[i][4][0],keypoints[i][5][0],keypoints[i][6][0])):
			im_opt = im_opt.transpose(image.FLIP_LEFT_RIGHT)
	#if keypoints[i][10][2] == 1:
	#				im_opt = im_opt.transpose(image.FLIP_LEFT_RIGHT)
	im_opt.save(image_root+normalized+path,'JPEG')
