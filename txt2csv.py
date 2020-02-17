'''
Creates a comma-separated copy of a tab- or space-delimited file

Usage: argv-based

> python txt2csv.py file
'''

import sys

def txtDelimiter(filename):
	with open(filename) as f:
		line = f.readline()
	f.close()

	if '\t' in line:
		return '\t'
	elif ' ' in line:
		return ' '
	else:
		return input('Delimiter:\n')


infile = sys.argv[1]
if len(sys.argv) > 2:
	outfile = sys.argv[2]
else:
	outfile = infile.replace('.txt', '.csv')

dataRead = open(infile)
dataWrite = open(outfile, 'w')

if '.txt' in infile:
	delim = txtDelimiter(infile)
elif '.csv' in infile:
	delim = ','
else:
	delim = input('Delimiter:')

for line in dataRead:
	dataWrite.write(line.replace(delim, ','))