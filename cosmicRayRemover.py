'''
Requirements: matplotlib, argparse, random, statistics, math, ufit

Function for removal of cosmic rays from 2D data, developed for
photoluminescence experiments where cosmic rays can affect
peak fitting.

Identifies cosmic rays as outliers in the first derivative.
Displays ray in plot and asks for user confirmation.
Replaces cosmic ray with a line fit of the same region with
pseudorandom noise generated from median of fit residuals.

Magic numbers/values:
	filenameModifier in write_file function
		default value: _rayremoved
		gets tacked onto the written filename to identify
		output file and prevent overwriting of original data

	threshold in find_ray function
		default value: 5
		controls threshold for identifying outliers in derivative

	chunkSize in main program
		default value: 50
		controls the size of the segment considered at a time
		larger values run faster
		smaller values replace cosmic rays better

Usage: argv-based, pass single filename as first argument

> python cosmicRayRemover.py file {option}

Options:
	unsupervised
		replaces all ray candidates and writes file without
		prompting user

'''

import sys
import argparse
import matplotlib.pyplot as plt
from random import uniform
from statistics import mean, median
from math import sqrt
from ufit.lab import *

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

	return x, y, delimiter


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


def write_file(filename, xValues, yValues, filename_modifier, delimiter):

	ext = '.' + filename.split('.')[-1]
	filename = filename.replace(ext, filename_modifier + ext)

	with open(filename, 'w') as f:
		for i in range(len(xValues)):
			f.write('%s%s %s \n' % (xValues[i], delimiter, yValues[i]))


# ---------- Program Functions ---------------------------------

def ddx(x, y):
	dx = []
	dy = []
	for i in range((len(x)-1)):
		dy.append( (y[i+1] - y[i]) / (x[i+1] - x[i]) )
		dx.append(x[i])

	return dx, dy


def find_ray(xValues, yValues):

	dx, dy = ddx(xValues, yValues)
	
	dyMean = mean([abs(val) for val in dy])

	threshold = 5
	foundRay = False
	for y in dy:
		if abs(y) > dyMean * threshold:
			foundRay = True
			break
		
	return foundRay


def replace_ray(x, y, dy, start, end):
	data = as_data(x[start:end], y[start:end], dy[start:end])

	model = StraightLine('line')

	result = model.fit(data)

	slope, intercept = result.paramvalues['line_slope'], result.paramvalues['line_y0']
	for i in range(start, end+1):
		noise = uniform(-1, 1) * median(result.residuals)
		y[i] = slope * x[i] + intercept + noise

	return y

def show_ray(x, y, rayX, rayY):
	plt.plot(x, y, rayX, rayY)
	plt.show()


# ---------- Main Program --------------------------------------

def main(args):

	files = args.data_files

	chunkSize = args.chunk_size

	for file in files:
		xValues, yValues, delimiter = read_2d_file(file)


		dyValues = [sqrt(y) for y in yValues]

		ufit.set_backend('lmfit')
		
		i = 0
		while i < (len(xValues) - chunkSize):
			start = i
			end = i + chunkSize-1
			xTest, yTest, dyTest = xValues[start:end], yValues[start:end], dyValues[start:end]

			foundRay = find_ray(xTest, yTest)
			if foundRay:

				if args.unsupervised:
					yValues = replace_ray(xValues, yValues, dyValues, start, end)

				else:
					show_ray(xValues, yValues, xTest, yTest)

					rayInSlice = input('Found ray? [y/N]').rstrip()
					if rayInSlice == '' or rayInSlice[0] not in ['y', 'Y']:
						pass
					else:
						yValues = replace_ray(xValues, yValues, dyValues, start, end)


			i += chunkSize
			if i + chunkSize >= len(xValues):
				i = len(xValues) - chunkSize

		if args.unsupervised:
			write_file(file, xValues, yValues, args.filename_modifier, delimiter)

		else:
			print('No (more) candidates found.')
			plt.plot(xValues, yValues)
			plt.show()

			done = input('Write file? [Y/n]').rstrip()
			if done == '' or done[0] not in ['n', 'N']:
				write_file(file, xValues, yValues, args.filename_modifier, delimiter)		
			else:
				sys.exit()


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Remove cosmic rays from 2D spectral data')
	parser.add_argument('data_files', nargs='+', help='Data files to remove rays from')

	parser.add_argument('-u', '--unsupervised', action='store_true', help='Do not prompt user to confirm suspected cosmic ray regions')
	parser.add_argument('-f', '--filename_modifier', type=str, default='-rayremoved', help='Modifier to data output file name')
	parser.add_argument('-c', '--chunk_size', type=int, default=50, help='Number of points to search for rays and replace if found')

	args = parser.parse_args()

	main(args)

