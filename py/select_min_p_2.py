#!/usr/bin/env python

import sys

fin = open(sys.argv[1])
fin.readline()
opt_data = []
opt_min = float("inf")

def str2int(s):
	ans = 0
	for i in range(len(s)):
		if s[i] >= '0' and s[i] <= '9':
			ans = ans * 10 + int(s[i])
	return ans

while True:
	line = fin.readline()
	#print line
	if line in ('',None):
		break
	#data = map(float,line.split())
	data = line.split()
	l = len(data)
	if int(data[l-1]) > 11600 and float(data[l-2])/int(data[l-1]) < opt_min:
                opt_min = float(data[l-2])/int(data[l-1])
                opt_data = line
	#if (1,5,6) == (str2int(data[1]),str2int(data[2]),str2int(data[3])) and (1,5,10) == (str2int(data[5]),str2int(data[6]),str2int(data[7])) and float(data[8])/int(data[9]) < opt_min and int(data[9]) >11570 :
	#	opt_min = float(data[10])/int(data[11])
	#	opt_data = line
        #if (1,5,10) == (str2int(data[1]),str2int(data[2]),str2int(data[3])) and (1,5,6) == (str2int(data[5]),str2int(data[6]),str2int(data[7])) and float(data[8])/int(data[9]) < opt_min and int(data[9]) >11570 :
        #        opt_min = float(data[8])/int(data[9])
        #        opt_data = line
print opt_data
