import lhsmdu
import sys
import math
import argparse
import pandas as pd


def ten_e_x(number):
	return math.log10(number)

def write_hypercube(n_points, var_names, var_values, filename='hypercube.csv'):

	for i, var_name in enumerate(var_names):
		var_names[i] = var_name.replace('_log_10', '')
		

	with open(filename, 'w') as f:
		f.write(','.join(var_names) + '\n')


		for row in range(n_points):
			line_contents = []
			for col in range(len(var_names)):
				line_contents.append( str(var_values[col][row]) )

			f.write(','.join(line_contents) + '\n')


		


def make_hypercube(n_points, var_names, var_ranges, precision):
	n_vars = len(var_names)

	unity_hypercube = lhsmdu.sample(n_vars, n_points)

	hypercube = pd.DataFrame()

	for n in range(n_vars):
		var_min, var_max = var_ranges[n]


		if '_log_10' in var_names[n]:
			e_min = ten_e_x(var_min)
			e_max = ten_e_x(var_max)
			e_diff = e_max - e_min
			row = [10 ** (e_diff * unity_hypercube[n, i] + e_min) for i in range(n_points)]

		else:
			diff = var_max - var_min
			row = [diff * unity_hypercube[n, i] + var_min for i in range(n_points)]

		row = [round(val, precision) for val in row]

		hypercube[var_names[n]] = row

	return hypercube


def main(n_points, var_names, var_ranges, precision, filename):

	hypercube = make_hypercube(n_points, var_names, var_ranges, precision)

	# write_hypercube(n_points, var_names, var_values, filename=filename)
	hypercube.to_csv(filename, index=False)


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Generate an n-dimensional Latin Hypercube DoE')
	parser.add_argument('dimensions', nargs='+', help='dimensions and limits formatted {var_name var_min var_max}. include _log_10 in var names for log values')

	parser.add_argument('-n', '--n_points', type=int, default=25, help='number of hypercube points to generate')
	parser.add_argument('-f', '--filename', default='hypercube.csv', help='output file name')
	parser.add_argument('-p', '--precision', type=int, default=3, help='decimal precision of hypercube points')

	args = parser.parse_args()

	var_names = []
	var_ranges = []

	for i in range(0, len(args.dimensions), 3):
		var_names.append(args.dimensions[i])

		var_min = float(args.dimensions[i+1])
		var_max = float(args.dimensions[i+2])

		var_ranges.append((var_min, var_max))

	main(args.n_points, var_names, var_ranges, args.precision, args.filename)

	# inputs = sys.argv[1:]

	# assert len(inputs) % 3 == 1, 'must have multiple of three inputs and n_points; [var_name var_min var_max] n_points'

	# var_names = []
	# var_ranges = []
	# n_points = int( inputs.pop(-1) )

	# for i in range(0, len(inputs), 3):
	# 	var_names.append(inputs[i])

	# 	var_min = float(inputs[i+1])
	# 	var_max = float(inputs[i+2])

	# 	var_ranges.append((var_min, var_max))


	# main(n_points, var_names, var_ranges)







