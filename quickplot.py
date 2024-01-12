'''
Requirements: matplotlib, numpy, argparse, pandas

Function for quick visualization of 2D data, ignores headers, 
automatically handles comma, space, and tab delimiters, 
other delimiters can be specified if those listed above are not found.

Usage: argv-based, pass as many filenames as you want 
as command line arguments

> python quickplot.py file1 file2 file3...

'''

import argparse
import numpy as np
import pandas as pd
import string
import sys

import matplotlib.pyplot as plt
import matplotlib




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

def wire_read_file(filename):
	try:
		import renishaw_wire

	except ModuleNotFoundError:
		print('No module to read Renishaw files')
		sys.exit()

	x, y = renishaw_wire.wire_read(filename)

	return x, y


# ---------- Program Functions ---------------------------------

def offset_data(data, offset):
	return [datum+offset for datum in data]

def normalize_data(data):
	normalizer = max(data)
	return [datum/normalizer for datum in data]

def integrate(x, y, _range):
	start, end = _range

	if type(x) == list:
		_x = pd.DataFrame(x)
		_y = pd.DataFrame(y)
	

	rows = _x[0].between(start, end)

	area = np.trapz(_y[0][rows], x=_x[0][rows])

	return area


def ddx(x, y):
	dx = []
	dy = []
	for i in range((len(x)-1)):
		dy.append( (y[i+1] - y[i]) / (x[i+1] - x[i]) )
		dx.append(x[i])

	return dx, dy


# ---------- Main Program --------------------------------------

def main(files, options):

	if options.sort_lambda:
		sort_func = lambda file : float(eval(options.sort_lambda))
		files.sort(key=sort_func)

	if not options.title:
		title = '-'.join(files[0].split('.')[:-1])
	else:
		title = options.title


	colorspace = matplotlib.colormaps.get_cmap(options.color)
	colors = colorspace( np.linspace(0, 1, len(files)) )

	if options.monochrome:
		colors = ['tab:gray' for file in files]

	if options.colors:
		if len(options.colors) == 1:
			colors = [options.colors[0] for file in files]
		else:
			assert len(options.colors) == len(files), 'must specify one or same number of colors and files'
			colors = options.colors

	if options.presentation:
		plt.rc('font', size=13)
		plt.rc('axes', labelsize=13)
		plt.rc('lines', markersize=9, linewidth=2)


	fig, ax = plt.subplots()

	if options.equation:
		x = np.linspace(options.range[0], options.range[1])
		y = eval(options.equation)
		ax.plot(x, y)

	legend = []
	for i, file in enumerate(files):
		if file.lower() == "none":
			continue


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
			if file[-4:] == '.wdf':
				x, y = wire_read_file(file)

			elif options.inverse:
				y, x = read_2d_file(file, options.columns)
			else:
				x, y = read_2d_file(file, options.columns)


		if options.normalize:
			y = normalize_data(y)

		if options.normalize_area[0] != options.normalize_area[1]:
			area = integrate(x, y, options.normalize_area)

			y = [datum/area for datum in y]

		if options.detrend > -1:
			# get first and last 5 elements
			x_fit = x[:5]
			x_fit.extend(x[-5:])
			y_fit = y[:5]
			y_fit.extend(y[-5:])

			# fit polynomial
			coefs = np.polyfit(x_fit, y_fit, options.detrend)

			# subtract polynomial fit
			y_fit = np.polyval(coefs, x)

			y = np.subtract(y, y_fit)

		if options.polyfit > -1:

			# fit polynomial
			coefs, cov = np.polyfit(x, y, options.polyfit, cov=True)
			
			y_poly = np.polyval(coefs, x)


			ax.plot(x, y_poly, color='k')

			coefs.reverse() # const. last
			func_text = '$y = '
			coefs_text = ''
			for n, coef in enumerate(coefs):
				power = len(coefs) - n
				if power > 0:
					func_text += '{c}x^{p} + '.format(c=string.ascii_lowercase[n], p=power)
					coefs_text += '${c}$ = {val} ± {var}\n'.format(c=string.ascii_lowercase[n], val=round(coef, ))
				else:
					func_text += '{c}$'.format(c=string.ascii_lowercase[n])


		if options.peak_area_over_time[0] != options.peak_area_over_time[1]:
			area = integrate(x, y, options.peak_area_over_time)
			y = area
			x = i
			options.xlabel = 'Experiment Number'
			options.style = 'scatter'

		
			



		if options.differentiate:
			for n in range(options.differentiate):
				x, y, = ddx(x, y)

		if options.offset != 0:
			offset = options.offset * i
			y = offset_data(y, offset)

		if options.style == '' or options.style.lower()[0] == 'line'[0]:
			ax.plot(x,y, color=colors[i])

		elif options.style.lower()[0] == 'scatter'[0]:
			ax.plot(x,y, marker=options.marker, color=colors[i])

		elif options.style.lower()[0] == 'both'[0]:
			ax.plot(x,y,'-o', marker=options.marker, color=colors[i])

		else:
			ax.plot(x,y, color=colors[i])

		if options.integrate[0] != options.integrate[1]:
			area = integrate(x, y, options.integrate)
			_x = pd.DataFrame(x)
			_y = pd.DataFrame(y)
			rows = _x[0].between(options.integrate[0], options.integrate[1])
			ax.fill_between(_x[0][rows], _y[0][rows], color='tab:gray', alpha=0.6, linewidth=0)

			_, xmax = ax.get_xlim()
			_, ymax = ax.get_ylim()
			ax.text(xmax*0.85, ymax*0.85, f'area: {area}', ha='right', bbox=dict(boxstyle='round', ec=(0, 0, 0), fc=(0.95, 0.95, 0.95)))


	ax.set_xlabel(options.xlabel)
	ax.set_ylabel(options.ylabel)

	if not options.no_title:
		ax.set_title(title)

	if options.no_xticks:
		ax.set_xticks([])
	if options.no_yticks:
		ax.set_yticks([])

	if options.xlim[0] != options.xlim[1]:
		ax.set_xlim(options.xlim)
	if options.ylim[0] != options.ylim[1]:
		ax.set_ylim(options.ylim)

	if len(legend) > 1 and not options.no_legend:
		fig.legend(legend, ncol=options.legend_columns)

	if options.tight:
		fig.tight_layout()


	if options.logx:
		ax.set_xscale('log')
	if options.logy:
		ax.set_yscale('log')


	if options.save is None:
		plt.show()

	else:

		fig.savefig(options.save, dpi=args.dpi)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Generate a quick plot of 2D data.')
	parser.add_argument('data_files', nargs='+', default=[], help='Data files to plot')

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
	parser.add_argument('--colors', type=str, nargs='+', help='specific colors to plot with specified individually', default=[])
	parser.add_argument('--monochrome', action='store_true', help='force a single color for all elements')
	parser.add_argument('--xkcd', action='store_true', help='xkcd styling')

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
	parser.add_argument('--dpi', type=int, default=300, help='dpi of saved figure if using --save {figname}')

	# math stuff
	parser.add_argument('--normalize', action='store_true', help='normalize all data to max of 1')
	parser.add_argument('--normalize_area', nargs=2, default=[0,0], type=float, help='normalize by an area between two points')
	parser.add_argument('--detrend', type=int, default=-1, help='fit and subtract polynomial function of degree {n} from whole domain')
	parser.add_argument('--differentiate', type=int, default=0, help='plot {n}th degree derivative')
	parser.add_argument('--polyfit', type=int, default=-1, help='fit {n}th degree polynomial')
	parser.add_argument('--hide_poly_coef', action='store_false', help='hide text box with polynomial coefficients')
	parser.add_argument('--peak_area_over_time', nargs=2, default=[0,0], type=float, help='integrate an area of data and plot area as time series')
	parser.add_argument('--equation', help='equation to plot as f(x). Example: e^x. Specify --range')
	parser.add_argument('--range', nargs=2, default=[-10, 10], type=float, help='range for custom --equation to be plotted over')
	parser.add_argument('--integrate', nargs=2, default=[0,0], type=float, help='integrate an area of data between two points')

	# pandas stuff
	parser.add_argument('--pandas', nargs=2, default=['', ''], help='use pandas to read file, plots {column_label_1} vs {column_label_2}. Only way to read excel files')



	args = parser.parse_args()

	files = args.data_files

	if args.xkcd:
		with plt.xkcd():
			main(files, args)
	else:
		main(files, args)


