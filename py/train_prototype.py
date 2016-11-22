#!/usr/bin/env python

#---two parameters:the beginning number of images(default 1),the end number of image(default the last one)---#

#the number in prototype file should be ordered#

import sys
import os
import copy
from numpy import *
from PIL import Image as image

#things to modify:
#done 1. read the key points of each image advance in an array 
#done 2. implement a function that can compute bounding box using boolean key points array 
#done 3. implement the first version: modify getting bounding box of prototype from file to from function below
#	 								 add a determining condition "if head[k]" during store Coordinate of key points
#4. pre resize *
#* make the same size
#done 5. change wapping image from PIL to opencv 
#6. implement the second version:don't use reading prototype parameters,
#								 instead loop all images, find a best one whoes avarage distance error is the min one 
#7. implement the third version: loop all images and all key points, 
#								 find a best one and best M-nearest ksy points whoes avarage distance error is the min one 
#								modify M 
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
		box = [0,0,std_w,std_h]

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

	return tuple(box)

def dis(point_a,point_b):
	if point_a[2] == 0 or point_b[2] == 0:
		return INFINITY
	else:
		return (point_a[0]-point_b[0])**2+(point_a[1]-point_b[1])**2

def k_nearest(kpoint,k):
	order = []
	flag = [False for i in range(len(kpoint))]
	n = 0
	for i in range(len(kpoint)):
		if head[i]:
			order.append((dis(kpoint[i],kpoint[k]),i))
		else:
			order.append((INFINITY,i))
	order.sort(key=lambda l:l[0])

	k_set = []
	for i in range(fix_K):
		if order[i][0] < INFINITY:
			n += 1
			flag[order[i][1]] = True
			k_set.append(order[i][1])
	k_set.sort()
	return [flag,n,tuple(k_set)]

#fixed parameters
image_root = '/work/cv2/haiwang/data/CUB200-2011/images/'  #change
keyfile =  '/work/cv2/haiwang/data/CUB200-2011/parts/part_locs.txt' #change
mapfile =  '/work/cv2/haiwang/data/CUB200-2011/parts/images.txt' #change
prototype = '/work/cv2/haiwang/data/CUB200-2011/parts/proto_order.txt' #change
original = 'original/'
normalized = 'normalization/' 
#image_root = '/Users/will/Documents/hiwi/3/images/'  #change
#keyfile =  '/Users/will/Documents/hiwi/3/part/part_locs.txt' #change
#mapfile =  '/Users/will/Documents/hiwi/3/part/images.txt' #change
#prototype = '/Users/will/Documents/hiwi/3/part/proto_order.txt' #change
#original = 'original/'
#normalized = 'normalization/'
ex_rate = 0.5
ex_min = 5
INFINITY = float("inf")
std_w = 150.0
std_h = 150.0
fix_K = 4
head = (False,True,False,False,True,True,True,False,False,True,True,False,False,False,True)
#		1	 2	3	 4	 5	6	7	8	 9	 10	11   12	13	14	15
K = 15 #the number of key points

#init parameters
keypoints = []
#Nt = 11788
Nt = 1000
N = 0 #the number of images
B = 1 #the beginning number of images
im_size = [] #the size of image
Ne = 0

#read image size
#imagemap = open(mapfile)
#for i in range(Nt):
#	path = imagemap.readline().split()[1]
#	classpath = path.split('/')[0]+'/'
#	im = image.open(image_root+original+path)	
#	im_size.append(im.size)

#read keypoints of each image and size of image
key = open(keyfile)
imagemap = open(mapfile)
line = key.readline()

while not line in (None,''):
	#print N
	path = imagemap.readline().split()[1]
	classpath = path.split('/')[0]+'/'
	im = image.open(image_root+original+path)
			
	im_size.append(im.size)

	kpoint = []
	for i in range(K):
		kpoint.append([float(line.split()[2]),float(line.split()[3]),int(line.split()[4])])
		line = key.readline()

	keypoints.append(kpoint)
	N += 1

sum_err_arr = []

for l in range(Nt):
	z = random.randint(0,N-1)

	#print "l",l,"z",z

	dict_k = {}
	for k in range(K):

		#print "k",k
		kpoints_p = keypoints[z]

		if kpoints_p[k][2] == 0 or not head[k]:
			continue
		[flag_k,n_k,k_set] = k_nearest(kpoints_p,k)
		if n_k < fix_K or dict_k.has_key(k_set):
			continue

		dict_k.setdefault(k_set,1)

		box = buldbox(kpoints_p,flag_k)
		w_s = std_w/(box[2]-box[0])
		h_s = std_h/(box[3]-box[1])

		M = [] 
		M_f = []
		for j in range(K):
			if flag_k[j]:
				M.append([(kpoints_p[j][0]-box[0])*w_s,(kpoints_p[j][1]-box[1])*h_s])
				M_f.append([(box[2]-kpoints_p[j][0])*w_s,(kpoints_p[j][1]-box[1])*h_s])
		
		M = matrix(M).T
		u = M.mean(1)
		M = M-u

		M_f = matrix(M_f).T
		u_f = M_f.mean(1)
		M_f = M_f-u_f

		Mps = [(M,0),(M_f,1)]

		error_N = 0
		sum_error = 0
		reverse_N = 0

		for i in range(N):

			#store Coordinate of key points

			Mi = []
			flag_match = True
			for j in range(K):	
				if flag_k[j]:
					if keypoints[i][j][2] == 1:
						Mi.append([keypoints[i][j][0]-im_size[i][0]/2,keypoints[i][j][1]-im_size[i][1]/2])
					else:
						flag_match = False
						break

			if not flag_match:
				continue

			Mi = matrix(Mi).T
			ui = Mi.mean(1)
			Mi = Mi-ui

			#select the best wraping parameters and relative wraping image	
			error_opt = -1
			reverse_flag = -1
			for [Mp,reverse] in Mps:

				#calculate parameters of 2D Similarity Transformation 
				U,S,V = linalg.svd(Mi*Mp.T)
				R = V.T*diag([1,linalg.det(V.T*U.T)])*U.T 
				s = trace(Mp.T*R*Mi)*1.0/trace(Mi.T*Mi)

				error = 0.0
				for j in range(fix_K):
					error += ((s*R*Mi.T[j].T).A[0][0]-Mp.T[j].T.A[0][0])**2 + ((s*R*Mi.T[j].T).A[1][0]-Mp.T[j].T.A[1][0])**2 			

				if error_opt == -1 or error < error_opt:
					error_opt = error
					reverse_flag = reverse

			#print error_opt
			if error_opt < 0:
				print error_opt,i
				#exit(0)
			else:
				sum_error += error_opt
				error_N += 1
				print z,k_set[0],k_set[1],k_set[2],k_set[3],i,error_opt,reverse_flag
				if reverse_flag == 0:
					reverse_N += 1

		#print sum_error*1.0/error_N,error_N,reverse_N,z,k_set[0],k_set[1],k_set[2]
		#sum_err_arr.append((sum_error*1.0/error_N,error_N,reverse_N,z,k_set[0],k_set[1],k_set[2]))

#sum_err_arr.sort(key=lambda l:l[0])

#for i in range(Nt):
#	print sum_err_arr[i]
