import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from PIL import Image
from datetime import datetime







def make_deck(args):

	page_width, page_height = landscape(letter)
	c = canvas.Canvas(args.outfile, pagesize=landscape(letter))


	

	n_pages = len(args.figures)

	if args.title:
		c.setFont('Helvetica', 36)
		linespacing = 36 * 1.25
		c.drawCentredString(page_width//2, 3*page_height//5, args.title)
		c.setFont('Helvetica', 20)
		linespacing = 20 * 1.25
		if args.author:
			c.drawCentredString(page_width//2, 2*page_height//5, args.author)
		c.drawCentredString(page_width//2, 20, datetime.now().strftime('%m/%d/%Y'))
		c.showPage()

	if args.reverse:
		args.figures.reverse()

	for i, file in enumerate(args.figures):

		if i+1 < n_pages:
			print(f'Working on page {i+1}/{n_pages}', end='\r')
		else:
			print(f'Working on page {i+1}/{n_pages}')
		fig = Image.open(file)

		im_width, im_height = fig.size

		if im_width > page_width:
			scale = page_width / im_width / 1.1

		elif im_height > page_height:
			scale = page_height / im_height / 1.1
		else:
			scale = 1

		# fig = fig.resize(( int(im_width * scale), int(im_height*scale) ), resample=Image.Resampling.LANCZOS)
		# im_width, im_height = fig.size

		left = page_width//2 - im_width*scale//2
		bottom = page_height//2 - im_height*scale//2
		width = im_width*scale//1
		height = im_height*scale//1

		c.drawInlineImage(fig, left, bottom, width=width, height=height)

		if args.fignames:
			c.setFont('Helvetica', 24)
			linespacing = 24 * 1.25
			fig_name = '.'.join(file.split('.')[:-1])
			c.drawCentredString(page_width//2, bottom+height+4, fig_name)

		c.showPage()

	print('Saving...')
	c.save()
	print('Done!')










if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Quick pdf slide deck of figures')

	parser.add_argument('figures', nargs='+', help='series of images to make pdf slide deck')

	parser.add_argument('--reverse', action='store_true', help='reverse figure order')
	parser.add_argument('-o', '--outfile', default='quickdeck_output.pdf')
	parser.add_argument('--title', help='title for title slide')
	parser.add_argument('--author', help='author name')
	parser.add_argument('--fignames', action='store_true', help='include figure file names on slide')

	# parser.add_argument('--scaling', choices=['fit', 'fill', ''])

	args = parser.parse_args()

	if args.title and args.outfile == 'quickdeck_output.pdf':
		args.outfile = args.title

	if '.pdf' not in args.outfile:
		args.outfile += '.pdf'



	make_deck(args)