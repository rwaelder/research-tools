import argparse
import cv2 as cv
import numpy as np
import os
import pandas as pd
# from PIL import Image
import sys


def points_on_circle(x_center, y_center, radius): # midpoint circle algirithm
	x = 0
	y = radius
	d = 5/4 - radius
	points = []

	while x <= y:
		offset_x = x+x_center
		offset_y = y+y_center

		points.append( (x+x_center, y+y_center) )
		points.append( (y+x_center, x+y_center) )
		points.append( (-x+x_center, -y+y_center) )
		points.append( (-y+x_center, -x+y_center) )
		points.append( (x+x_center, -y+y_center) )
		points.append( (y+x_center, -x+y_center) )
		points.append( (-x+x_center, y+y_center) )
		points.append( (-y+x_center, x+y_center) )

		if d < 0:
			d = d + 2*x + 3
		else:
			d = d + 2*x - 2*y + 5
			y -= 1

		x += 1

	return list(set(points))

def show_step(image, step_name):
	cv.imshow(step_name, image)
	cv.waitKey(0)

def main(files, args):
	
	if len(files) > 10:
		args.show_progress = True

	for i, file in enumerate(files):

		if args.show_progress:
			bar_length = 20
			pct_done = int( i / len(files) * bar_length)
			bar = ''
			for j in range(bar_length):
				if j < pct_done:
					bar += '#'
				else:
					bar += '-'
			out_bar = f'{bar} {i+1}/{len(files)}'

			print(out_bar, end='\r')

		image = cv.imread(file, cv.IMREAD_COLOR)
		image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
		gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)



		if args.show_steps:
			show_step(gray, 'grayscale')

		if args.cutoff_top > 0:
			height = gray.shape[0]
			cutoff = int( height * (args.cutoff_top/100) )
			gray = gray[cutoff:, :]

		if args.cutoff_bottom > 0:
			height = gray.shape[0]
			cutoff = int( height * (1 - (args.cutoff_bottom/100)) )

			gray = gray[:cutoff, :]

		if args.show_steps:
			show_step(gray, 'cutoff')


		gray = cv.addWeighted(gray, args.contrast, np.zeros(gray.shape, gray.dtype), 0, args.brightness)

		if args.show_steps and (args.contrast != 1 or args.brightness != 0):
			show_step(gray, 'brightness and contrast')

		if args.binary > -1:
			ret, gray = cv.threshold(gray, args.binary, 255, cv.THRESH_BINARY)
			if args.show_steps:
				show_step(gray, 'threshold')

		if args.blur > 0:
			gray = cv.blur(gray, (args.blur, args.blur))

			if args.show_steps:
				show_step(gray, 'blurred')


		# find center of circle
		xvals, yvals = [], []

		height, width = gray.shape
		for j in range(height):
			for i in range(width):
				if gray[j][i] > 0:
					xvals.append(i)
					yvals.append(j)

		x_center = int(np.mean(xvals))
		y_center = int(np.mean(yvals))

		if args.cutoff_top > 0:
			y_center += int( height * (args.cutoff_top/100) )


		outer_radius = np.max(yvals) - np.min(yvals)
		cv.circle(image, (x_center, y_center), 10, (0, 0, 255), -1)
		cv.circle(image, (x_center, y_center), outer_radius, (0, 255, 0), 5)

		if args.show_steps:
			show_step(image, 'processed')

		height, width = image_gray.shape
		dist_to_edge = np.min([x_center, width-x_center, y_center, height-y_center])
		radius = []
		intensities = []
		'''
		for r in range(1, dist_to_edge):
			radius.append(r)
			intensity = 0
			for theta in range(360):
				radtheta = np.deg2rad(theta)
				i = int( r * np.cos(radtheta) )
				j = int( r * np.sin(radtheta) )
				intensity += image_gray[x_center+i][y_center+j]

				cv.rectangle(image, (x_center+i, y_center+j), (x_center+i, y_center+j), (0, 255, 0), -1)
			intensities.append(intensity)
		'''

		for r in range(1, dist_to_edge):
			radius.append(r)
			intensity = 0
			points = points_on_circle(x_center, y_center, r)

			for point in points:
				intensity += image_gray[point[0]][point[1]]

				cv.rectangle(image, (point[0], point[1]), (point[0], point[1]), (0, 255, 0), -1)
			if args.average:
				intensities.append(intensity / len(points))
			else:
				intensities.append(intensity)
		if args.show_steps:
			show_step(image, 'counted points')


		if args.scale:
			radial_profile = pd.DataFrame({
				'radius (nm-1)' : [r / args.scale for r in radius],
				'intensity' : intensities
				})
		else:
			radial_profile = pd.DataFrame({
				'radius (pixels)' : radius,
				'intensity' : intensities
				})

		csvfile = '.'.join(file.split('.')[:-1])
		radial_profile.to_csv(f'{csvfile}.csv', index=False)




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Generate radial intensity profile from electron diffraction image')
	parser.add_argument('images', nargs='+', default=[], help='Image file or files to process')

	# preprocessing
	parser.add_argument('--blur', type=int, default=0, help='Blur image using {n x n} kernel')
	parser.add_argument('--contrast', type=float, default=1.0, help='Change contrast. < 1 decreases contrast, > 1 increases')
	parser.add_argument('--brightness', type=int, default=0, help='Increase or decrease brightness')
	parser.add_argument('--binary', type=int, default=127, help='Threshold image to binary across grayscale value 0 - 255')
	parser.add_argument('--cutoff_top', type=int, default=0, help='Percent of image height to remove from top' )
	parser.add_argument('--cutoff_bottom', type=int, default=0, help='Percent of image height to remove from bottom')
	
	# misc
	parser.add_argument('--show_steps', action='store_true', help='Show steps of process')
	# parser.add_argument('--save_steps', action='store_true', help='Save process steps as individual images')
	parser.add_argument('--show_progress', action='store_true', help='Display progress bar. Automatically turned on if more than 10 files are supplied')
	parser.add_argument('--average', action='store_true', help='Average radial intensity instead of summing')
	# data
	parser.add_argument('--scale', type=int, default=0, help='Scale in pixels per nm-1')

	args = parser.parse_args()

	files = args.images

	main(files, args)