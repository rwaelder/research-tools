'''
Requirements: matplotlib, PyQt5

Gui-based matplotlib plotting software for quick visualization of data.

Usage: just launch it!

> python qtplot.py

'''

import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QInputDialog, 
	QLineEdit, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, 
	QFileDialog, QFormLayout, QComboBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


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

# ---------- Program Classes -----------------------------------

class App(QMainWindow):

	def __init__(self):
		super().__init__()
		self.left = 10
		self.top = 10
		self.title = 'Qt Plot'
		self.width = 640
		self.height = 480
		self.init_UI()

	def init_UI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		self.plotCanvas = PlotCanvas(self, width=5, height=4)
		self.plotCanvas.move(0,0)

		newButton = QPushButton('New Plot', self)
		newButton.setToolTip('Delete current plot and visualize new data')
		newButton.clicked.connect(lambda : self.new_button_click())
		newButton.move(500,0)
		newButton.resize(140,50)


		addButton = QPushButton('Add Data', self)
		addButton.setToolTip('Add another dataset to current axes')
		addButton.clicked.connect(lambda : self.add_button_click())
		addButton.move(500,50)
		addButton.resize(140,50)
		
		saveButton = QPushButton('Save Figure', self)
		saveButton.setToolTip('Save the current figure to image file')
		saveButton.clicked.connect(lambda : self.save_button_click())
		saveButton.move(500,100)
		saveButton.resize(140,50)


		labelButton = QPushButton('Plot Labels', self)
		labelButton.setToolTip('Set/edit axes labels and title')
		labelButton.clicked.connect(lambda : self.labels_button_click())
		labelButton.move(500,150)
		labelButton.resize(140,50)


		styleBox = QComboBox(self)
		styleBox.addItems(['Dots', 'Line', 'Connected Dots'])
		styleBox.currentIndexChanged.connect(lambda : self.style_box_changed(styleBox.currentText()))
		styleBox.move(500, 300)
		styleBox.resize(140, 50)

		self.show()
		return

	def open_file_dialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;CSV Files (*.csv);;Text files (*.txt)", options=options)
		if filename:
			return filename
		else:
			return None

	def save_file_dialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		filename, qfilter = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","Portable Network Graphic (*.png);; Portable Docuent Format (*.pdf);; Scalable Vector Graphics (*.svg);;", options=options)
		if filename:
			filename += qfilter[-5:-1]
			return filename
		else:
			return None


	def new_button_click(self):
		filename = self.open_file_dialog()
		if filename:
			x, y = read_2d_file(filename)

			self.plotCanvas.new_data(x, y)
		else:
			return

	def add_button_click(self):
		filename = self.open_file_dialog()
		if filename:
			x, y = read_2d_file(filename)

			self.plotCanvas.add_data(x, y)
		else:
			return

	def save_button_click(self):
		filename = self.save_file_dialog()
		if filename:
			self.plotCanvas.save_figure(filename)
		else:
			return

	def labels_button_click(self):
		xlabel = self.getText('X Label:')
		ylabel = self.getText('Y Label:')
		title = self.getText('Title:')

		self.plotCanvas.set_labels(xlabel, ylabel, title)

	def style_box_changed(self, currentSelection):
		self.plotCanvas.set_style(currentSelection)


	def getText(self, prompt):
		text, okPressed = QInputDialog.getText(self, "",prompt, QLineEdit.Normal, "")
		if okPressed and text != '':
			return text



class PlotCanvas(FigureCanvas):

	def __init__(self, parent=None, width=5, height=4, dpi=100):
		self.parent = parent
		self.qwidth = width
		self.qheight = height
		self.qdpi = dpi

		self.plotStyle = 'o'
		self.title = ''
		self.xlabel = ''
		self.ylabel = ''

		self.xData = []
		self.yData = []

		self.setup_new_figure()
		self.plot_onOpen()

	def set_labels(self, xlabel, ylabel, title):
		self.xlabel = xlabel
		self.ylabel = ylabel
		self.title = title

		self.plot()

	def set_style(self, newStyle):
		['Dots', 'Line', 'Connected Dots']
		if newStyle == 'Dots':
			styleText = 'o'
		elif newStyle == 'Line':
			styleText = '-'
		else:
			styleText = '-o'

		if self.plotStyle != styleText:
			self.plotStyle = styleText
			self.plot()

	def save_figure(self, filename):
		self.figure.savefig(filename)


	def setup_new_figure(self):
		fig = Figure(figsize=(self.qwidth, self.qheight), dpi=self.qdpi)
		self.axes = fig.gca()

		FigureCanvas.__init__(self, fig)
		self.setParent(self.parent)

		FigureCanvas.setSizePolicy(self,
				QSizePolicy.Expanding,
				QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		

	def new_data(self, x, y):
		self.xData = []
		self.yData = []

		self.add_data(x, y)


	def add_data(self, x, y):
		self.xData.append(x)
		self.yData.append(y)

		self.plot()


	def plot_onOpen(self):
		ax = self.figure.add_subplot(111)
		ax.plot(dinoX, dinoY, 'ko')
		ax.set_title('Datasaurus wishes you happy plotting!')


	def plot(self):
		self.axes.clear()
		ax = self.figure.add_subplot(111)
		for i in range(len(self.xData)):
			ax.plot(self.xData[i], self.yData[i], self.plotStyle)

		ax.set_title(self.title)
		ax.set_xlabel(self.xlabel)
		ax.set_ylabel(self.ylabel)

		self.draw()

# ---------- Main Program? -------------------------------------

dinoX = [55.3846, 51.5385, 46.1538, 42.8205, 40.7692, 38.7179, 35.641, 33.0769, 28.9744, 26.1538, 23.0769, 22.3077, 22.3077, 23.3333, 25.8974, 29.4872, 32.8205, 35.3846, 40.2564, 44.1026, 46.6667, 50.0, 53.0769, 56.6667, 59.2308, 61.2821, 61.5385, 61.7949, 57.4359, 54.8718, 52.5641, 48.2051, 49.4872, 51.0256, 45.3846, 42.8205, 38.7179, 35.1282, 32.5641, 30.0, 33.5897, 36.6667, 38.2051, 29.7436, 29.7436, 30.0, 32.0513, 35.8974, 41.0256, 44.1026, 47.1795, 49.4872, 51.5385, 53.5897, 55.1282, 56.6667, 59.2308, 62.3077, 64.8718, 67.9487, 70.5128, 71.5385, 71.5385, 69.4872, 46.9231, 48.2051, 50.0, 53.0769, 55.3846, 56.6667, 56.1538, 53.8462, 51.2821, 50.0, 47.9487, 29.7436, 29.7436, 31.2821, 57.9487, 61.7949, 64.8718, 68.4615, 70.7692, 72.0513, 73.8462, 75.1282, 76.6667, 77.6923, 79.7436, 81.7949, 83.3333, 85.1282, 86.4103, 87.9487, 89.4872, 93.3333, 95.3846, 98.2051, 56.6667, 59.2308, 60.7692, 63.0769, 64.1026, 64.359, 74.359, 71.2821, 67.9487, 65.8974, 63.0769, 61.2821, 58.7179, 55.1282, 52.3077, 49.7436, 47.4359, 44.8718, 48.7179, 51.2821, 54.1026, 56.1538, 52.0513, 48.7179, 47.1795, 46.1538, 50.5128, 53.8462, 57.4359, 60.0, 64.1026, 66.9231, 71.2821, 74.359, 78.2051, 67.9487, 68.4615, 68.2051, 37.6923, 39.4872, 91.2821, 50.0, 47.9487, 44.1026]
dinoY = [97.1795, 96.0256, 94.4872, 91.4103, 88.3333, 84.8718, 79.8718, 77.5641, 74.4872, 71.4103, 66.4103, 61.7949, 57.1795, 52.9487, 51.0256, 51.0256, 51.0256, 51.4103, 51.4103, 52.9487, 54.1026, 55.2564, 55.641, 56.0256, 57.9487, 62.1795, 66.4103, 69.1026, 55.2564, 49.8718, 46.0256, 38.3333, 42.1795, 44.1026, 36.4103, 32.5641, 31.4103, 30.2564, 32.1795, 36.7949, 41.4103, 45.641, 49.1026, 36.0256, 32.1795, 29.1026, 26.7949, 25.2564, 25.2564, 25.641, 28.718, 31.4103, 34.8718, 37.5641, 40.641, 42.1795, 44.4872, 46.0256, 46.7949, 47.9487, 53.718, 60.641, 64.4872, 69.4872, 79.8718, 84.1026, 85.2564, 85.2564, 86.0256, 86.0256, 82.9487, 80.641, 78.718, 78.718, 77.5641, 59.8718, 62.1795, 62.5641, 99.4872, 99.1026, 97.5641, 94.1026, 91.0256, 86.4103, 83.3333, 79.1026, 75.2564, 71.4103, 66.7949, 60.2564, 55.2564, 51.4103, 47.5641, 46.0256, 42.5641, 39.8718, 36.7949, 33.718, 40.641, 38.3333, 33.718, 29.1026, 25.2564, 24.1026, 22.9487, 22.9487, 22.1795, 20.2564, 19.1026, 19.1026, 18.3333, 18.3333, 18.3333, 17.5641, 16.0256, 13.718, 14.8718, 14.8718, 14.8718, 14.1026, 12.5641, 11.0256, 9.8718, 6.0256, 9.4872, 10.2564, 10.2564, 10.641, 10.641, 10.641, 10.641, 10.641, 10.641, 8.718, 5.2564, 2.9487, 25.7692, 25.3846, 41.5385, 95.7692, 95.0, 92.6923]

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())