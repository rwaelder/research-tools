'''
Requirements: matplotlib, numpy, argparse

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
import argparse

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

def offset_data(data, offset):
	return [datum+offset for datum in data]

def normalize_data(data):
	normalizer = max(data)
	return [datum/normalizer for datum in data]

# ---------- Main Program --------------------------------------

def main(files, options):

	if options.title:
		title = '-'.join(sys.argv[1].split('.')[:-1])
	else:
		title = options.title

	style = options.style


	colorspace = cm.get_cmap(name=options.color)
	colors = colorspace( np.linspace(0, 1, len(files)) )

	if options.presentation:
		plt.rcParams.update({'font.size' : 20})
	else:
		pass

	legend = []
	for i, file in enumerate(files):

		if options.legend_labels:
			label = options.legend_labels + ' ' + str(i+1)
			legend.append(label)
		else:

			# remove extension
			legendFilename = '.'.join( file.split('.')[:-1] )
			# slice based on optional arguments
			legendFilename = legendFilename[options.legend_start_cutoff:options.legend_end_cutoff]
			legend.append(legendFilename)

		x = []
		y = []

		x, y = read_2d_file(file)

		if options.offset != 0:
			offset = options.offset * i
			y = offset_data(y, offset)

		if options.normalize:
			y = normalize_data(y)

		if style == '' or style.lower()[0] == 'line'[0]:
			plt.plot(x,y, color=colors[i])

		elif style.lower()[0] == 'dot'[0]:
			plt.plot(x,y,'o', color=colors[i])

		elif style.lower()[0] == 'both'[0]:
			plt.plot(x,y,'-o', color=colors[i])

		else:
			plt.plot(x,y, color=colors[i])

	plt.xlabel(options.xlabel)
	plt.ylabel(options.ylabel)

	if not options.no_title:
		plt.title(title)

	if options.no_xticks:
		plt.xticks([])
	if options.no_yticks:
		plt.yticks([])

	if len(legend) > 1 and not options.no_legend:
		plt.legend(legend)

	if options.tight:
		plt.tight_layout()

	if options.save is None:
		plt.show()

	else:

		plt.savefig(options.save)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Generate a quick plot of 2D data.')
	parser.add_argument('data_files', nargs='+', help='Data files to plot')

	parser.add_argument('-x', '--xlabel', type=str, help='x axis label', default='')
	parser.add_argument('-y', '--ylabel', type=str, help='y axis label', default='')
	parser.add_argument('--no_xticks', action='store_true', help='don\'t show any ticks on x axis')
	parser.add_argument('--no_yticks', action='store_true', help='don\'t show any ticks on y axis')

	parser.add_argument('-t', '--title', type=str, help='plot title', default='')
	parser.add_argument('-s', '--style', type=str, help='plot as line, dot, or both', choices=['line', 'dot', 'both'], default='line')
	parser.add_argument('-o', '--offset', type=float, help='vertical offset between datasets', default=0)
	parser.add_argument('-c', '--color', type=str, help='color palette for plots. see https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html', default='gist_rainbow')
	parser.add_argument('-l', '--legend_labels', type=str, help='iterated labels to use in the legend for each dataset ', default='')
	parser.add_argument('--legend_start_cutoff', type=int, help='character to start cutoff of filenames for legend', default=0)
	parser.add_argument('--legend_end_cutoff', type=int, help='character to end cutoff of filenames for legend', default=None)
	parser.add_argument('--no_legend', action='store_true', help='don\'t display a legend')
	parser.add_argument('--normalize', action='store_true', help='normalize all data to max of 1')
	parser.add_argument('--tight', action='store_true', help='use a tight layout')
	parser.add_argument('--no_title', action='store_true', help='force no title on plot')
	parser.add_argument('--presentation', action='store_true', help='increase font size for use in slides')
	parser.add_argument('--save', type=str, default=None, help='save plot as file. pdf format if not specified')


	args = parser.parse_args()

	files = args.data_files

	main(files, args)
