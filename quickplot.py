'''
Requirements: matplotlib, numpy, argparse, pandas

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
import pandas as pd
import sys
import argparse

# ---------- Helper functions ----------------------------------

def read_2d_file(filename, columns):
	x_col, y_col = columns

	x, y = [], []
	delimiter = find_delimiter(filename)

	with open(filename) as f:
		line = f.readline()

		num_cols = len( line.split(delimiter) )

		assert x_col < num_cols, \
		'specified x column index {x} greater than number of columns in data file {file}'.format(x=x_col, file=filename)

		assert y_col < num_cols, \
		'specified y column index {y} greater than number of columns in data file {file}'.format(y=y_col, file=filename)

	with open(filename) as f:
		for line in f:
			lineSplit = line.split(delimiter)

			if is_number(lineSplit[x_col]) and is_number(lineSplit[y_col]):
				x.append( float( lineSplit[x_col] ))
				y.append( float( lineSplit[y_col] ))
			else:
				continue

	return x, y

def find_delimiter(filename):
	delimiters = [',', ';', '\t', ' ']

	with open(filename) as f:
		line = f.readline()

	# try common delimiters, return if found
	for delimiter in delimiters:
		if try_delimiter(delimiter, line):
			return delimiter

	# if common delimiters are not found, prompt user for delimiter and check
	while delimiter not in line:
		delimiter = input('Please specify delimiter for %s:\n' % filename)

	return delimiter

	

def try_delimiter(delimiter, line):
	if delimiter in line:
		return True
	else:
		return False

def is_number(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def pandas_read_file(filename, column_labels):
	if '.xlsx' in filename or '.xls' in filename:
		datafile = pd.read_excel(filename).dropna()
	elif '.csv' in filename:
		datafile = pd.read_csv(filename).dropna()
	elif '.txt' in filename:
		#TODO
		print('txt not yet supported')
		sys.exit()

	x = datafile[column_labels[0]].tolist()
	y = datafile[column_labels[1]].tolist()

	return x, y


# ---------- Program Functions ---------------------------------

def offset_data(data, offset):
	return [datum+offset for datum in data]

def normalize_data(data):
	normalizer = max(data)
	return [datum/normalizer for datum in data]

def ddx(x, y):
	dx = []
	dy = []
	for i in range((len(x)-1)):
		dy.append( (y[i+1] - y[i]) / (x[i+1] - x[i]) )
		dx.append(x[i])

	return dx, dy

# ---------- Font Formats --------------------------------------

lgd_pres = {'family': 'sans',
		'size': 12,
		}
txt_pres = {'family': 'sans',
		'fontweight': 'normal',
		'size': 14,
		'fontstyle': 'normal'
		}
axs_pres = {'family': 'sans',
		'fontweight': 'normal',
		'size': 18,
		'fontstyle': 'normal'
		}

# ---------- Main Program --------------------------------------

def main(files, options):

	if options.sort_lambda:
		sort_func = lambda file : eval(options.sort_lambda)
		files.sort(key=sort_func)

	if not options.title:
		title = '-'.join(files[0].split('.')[:-1])
	else:
		title = options.title

	style = options.style


	colorspace = cm.get_cmap(name=options.color)
	colors = colorspace( np.linspace(0, 1, len(files)) )

	if options.presentation:
		lgd_fontdict = lgd_pres
		axes_fontdict = axs_pres
		text_fontdict = txt_pres
	else:
		lgd_fontdict = None
		axes_fontdict = None
		text_fontdict = None

	legend = []
	for i, file in enumerate(files):

		if options.legend_labels:
			label = options.legend_labels + ' ' + str(i+1)
			legend.append(label)

		elif options.legend_lambda:
			label = lambda file : eval(options.legend_lambda)
			legend.append(label(file))
		else:

			# remove extension
			legendFilename = '.'.join( file.split('.')[:-1] )
			# slice based on optional arguments
			legendFilename = legendFilename[options.legend_start_cutoff:options.legend_end_cutoff]
			legend.append(legendFilename)

		x = []
		y = []

		if options.pandas[0] != '':
			x, y, = pandas_read_file(file, options.pandas)

		else:
			if options.inverse:
				y, x = read_2d_file(file, options.columns)
			else:
				x, y = read_2d_file(file, options.columns)


		if options.normalize:
			y = normalize_data(y)

		if options.detrend > -1:
			# get first and last 5 elements
			x_fit = x[:5]
			x_fit.extend(x[-5:])
			y_fit = y[:5]
			y_fit.extend(y[-5:])

			# fit polynomial
			coefs = np.polyfit(x_fit, y_fit, options.detrend).tolist()
			coefs.reverse() # largest order last

			# subtract polynomial fit
			for n, coef in enumerate(coefs):
				if n == 0:
					y = [yi - coef for yi in y]
				else:
					y = [y[i] - coef*x[i]**n for i in range(len(x))]

		if options.differentiate:
			for n in range(options.differentiate):
				x, y, = ddx(x, y)

		if options.offset != 0:
			offset = options.offset * i
			y = offset_data(y, offset)

		if style == '' or style.lower()[0] == 'line'[0]:
			plt.plot(x,y, color=colors[i])

		elif style.lower()[0] == 'scatter'[0]:
			plt.plot(x,y,options.marker, color=colors[i])

		elif style.lower()[0] == 'both'[0]:
			plt.plot(x,y,'-o', color=colors[i])

		else:
			plt.plot(x,y, color=colors[i])

	plt.xlabel(options.xlabel, fontdict=axes_fontdict)
	plt.ylabel(options.ylabel, fontdict=axes_fontdict)

	if not options.no_title:
		plt.title(title, fontdict=axes_fontdict)

	if options.no_xticks:
		plt.xticks([])
	if options.no_yticks:
		plt.yticks([])

	if options.xlim[0] != options.xlim[1]:
		plt.xlim(options.xlim)
	if options.ylim[0] != options.ylim[1]:
		plt.ylim(options.ylim)

	if len(legend) > 1 and not options.no_legend:
		plt.legend(legend, ncol=options.legend_columns, prop=lgd_fontdict)

	if options.tight:
		plt.tight_layout()


	if options.logx:
		plt.xscale('log')
	if options.logy:
		plt.yscale('log')


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
	parser.add_argument('--xlim', type=float, nargs=2, help='specify x limits for graph area', default=[0,0])
	parser.add_argument('--ylim', type=float, nargs=2, help='specify y limits for graph area', default=[0,0])
	parser.add_argument('--logx', action='store_true', help='use log scale for x axis')
	parser.add_argument('--logy', action='store_true', help='use log scale for y axis')



	parser.add_argument('--title', type=str, help='plot title', default='')
	parser.add_argument('--no_title', action='store_true', help='force no title on plot')
	parser.add_argument('--style', type=str, help='plot as line, scatter, or both', choices=['line', 'scatter', 'both'], default='line')
	parser.add_argument('--marker', help='marker for scatter plot', default='o')
	parser.add_argument('--offset', type=float, help='vertical offset between datasets', default=0)
	parser.add_argument('--color', type=str, help='color palette for plots. see https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html', default='gist_rainbow')

	# legend stuff
	parser.add_argument('--legend_labels', type=str, help='iterated labels to use in the legend for each dataset ', default='')
	parser.add_argument('--legend_start_cutoff', type=int, help='character to start cutoff of filenames for legend', default=0)
	parser.add_argument('--legend_end_cutoff', type=int, help='character to end cutoff of filenames for legend', default=-1)
	parser.add_argument('--legend_lambda', type=str, help='specify a lambda {file} function to parse filenames for legend labels', default='')
	parser.add_argument('--no_legend', action='store_true', help='don\'t display a legend')
	parser.add_argument('--legend_columns', type=int, help='number of columns to use for legend', default=1)

	# misc
	parser.add_argument('--tight', action='store_true', help='use a tight layout')
	parser.add_argument('--presentation', action='store_true', help='increase font size for use in slides')
	parser.add_argument('--save', type=str, default=None, help='save plot as file, pdf format if not specified')
	parser.add_argument('--inverse', action='store_true', help='flip x and y')
	parser.add_argument('--columns', nargs=2, default=[0, 1], type=int, help='columns of data file to read, 0-indexed')
	parser.add_argument('--sort_lambda', type=str, help='lambda {file} function to parse filenames to sort files', default='')

	# math stuff
	parser.add_argument('--normalize', action='store_true', help='normalize all data to max of 1')
	parser.add_argument('--detrend', type=int, default=-1, help='fit and subtract polynomial function of degree {n} from whole domain')
	parser.add_argument('--differentiate', type=int, default=0, help='plot {n}th degree derivative')

	# pandas stuff
	parser.add_argument('--pandas', nargs=2, default=['', ''], help='use pandas to read file, plots {column_label_1} vs {column_label_2}. Only way to read excel files')



	args = parser.parse_args()

	files = args.data_files

	main(files, args)
