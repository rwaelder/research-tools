'''
Requirements: matplotlib, numpy

Function for quick visualization of 2D data, ignores headers, 
automatically handles comma, space, and tab delimiters, 
other delimiters can be specified if those listed above are not found.

Usage: argv-based, pass as many filenames as you want 
as command line arguments

> python quickplot.py file1 file2 file3...

'''


import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import sys

# ---------- Helper functions ----------------------------------

def read_2d_file(filename):
	x, y = [], []
	delimiter = get_delimiter(filename)

	with open(filename) as f:
		for line in f:
			lineSplit = line.split(delimiter)

			if is_number(lineSplit[0]):
				x.append( float( lineSplit[0] ))
				y.append( float( lineSplit[1] ))
			else:
				continue

	return x, y

def get_delimiter(filename):
	if '.csv' in filename:
		delimiter = ','

	elif '.txt' in filename:
		with open(filename) as f:
			line = f.readline()

		if '\t' in line:
			delimiter = '\t'
		elif ' ' in line:
			delimiter = ' '

	else:
		delimiter = input('Please specify delimiter for %s:\n' % filename)

	return delimiter

def is_number(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

# ---------- Program Functions ---------------------------------

# ---------- Main Program --------------------------------------

xlabel = input('X label:\n')
ylabel = input('Y label:\n')
title = input('Title:\n')
if title == '':
	title = '-'.join(sys.argv[1].split('.')[:-1])

style = input('Line, dot, or both?\n')

colors = cm.gist_rainbow( np.linspace(0, 1, len(sys.argv)-1) )

legend = []
for i, filename in enumerate(sys.argv[1:]):

	legendFilename = '.'.join( filename.split('.')[:-1] )
	legend.append(legendFilename)

	x = []
	y = []

	x, y = read_2d_file(filename)

	if style == '' or style.lower()[0] == 'line'[0]:
		plt.plot(x,y, color=colors[i])

	elif style.lower()[0] == 'dot'[0]:
		plt.plot(x,y,'o', color=colors[i])

	elif style.lower()[0] == 'both'[0]:
		plt.plot(x,y,'-o', color=colors[i])

	else:
		plt.plot(x,y, color=colors[i])

plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(title)

if len(legend) > 1:
	plt.legend(legend)

plt.show()