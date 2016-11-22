#!/usr/bin/env python


import sys
import os
from numpy import *
from PIL import Image as image

N = 11788
Nt = 0
NN = 2000
INFINITY = float("inf")

fin = open(sys.argv[1])

#f = [[0 for i in range(N)] for j in range(Nt)]
#r = f = [[0 for i in range(N)] for j in range(Nt)]
#b = [0 for j in range(Nt)]
f = []
b = []

tmp = []

n_last = -1
while True:
	line = fin.readline()
	if line in ("",None):
		break
	data = line.split()
	p = int(data[0])
	k_set = (int(data[1]),int(data[2]),int(data[3]),int(data[4]))
	n = int(data[5])
	value = float(data[6])
	r = int(data[7])

	if n < n_last:
		for i in range(n_last+1,N):
			tmp.append((INFINITY,0))
		#print Nt,len(tmp)
		f.append(tmp)
		b.append((p,k_set))

		Nt += 1
		if Nt == NN:
			break
		tmp = []
		for i in range(n):
			tmp.append((INFINITY,0))

	for i in range(n_last+1,n):
		tmp.append((INFINITY,0))
	tmp.append((value,r))

	n_last = n


for i in range(n_last+1,N):
        tmp.append((INFINITY,0))
print Nt,len(tmp)
f.append(tmp)
b.append((p,k_set))

Nt += 1

for i in range(Nt-1):
	for j in range(i+1,Nt):
		sum_e = 0.0
		e_n = 0
		#print i,j,b[i],b[j]
		for k in range(N):
			#if b[j] == 3373:
			#	print Nt,i,j,k
			if min(f[i][k][0],f[j][k][0]) < INFINITY:
				sum_e += min(f[i][k][0],f[j][k][0])
				e_n += 1
		print b[i],b[j],sum_e,e_n
		#exit(0)

