import sys, os
from PIL import Image

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Giffer():
	def __init__(self):
		self.source_files = []
		self.destination = ''
		self.frame_duration = 24
		self.loops = 0
		# self.sort = None
		self.exclusion_criteria = None

	def set_source_files(self, source_files):
		self.source_files = source_files

	def get_source_files(self):
		return self.source_files

	def set_destination(self, destination):
		self.destination = destination

	def get_destination(self):
		return self.destination

	def set_frame_duration(self, frame_duration):
		frame_duration = int(frame_duration)

		assert frame_duration > 0, 'frame duration must be positive'
		self.frame_duration = frame_duration

	def get_frame_duration(self):
		return self.frame_duration

	def set_loops(self, loops):
		loops = int(loops)

		assert loops > -1, 'loops must be 0 or positive integer'
		self.loops = loops

	def get_loops(self):
		return self.loops

	# def set_sort_lambda(self, sort_lambda):
	# 	self.sort = sort_lambda

	# def get_sort_lambda(self):
	# 	return str(self.sort)

	def set_exclusion_criteria(self, exclusion_criteria):
		self.exclusion_criteria = exclusion_criteria

	def get_exclusion_criteria(self):
		return self.exclusion_criteria

	def make_gif(self):

		if not self.source_files:
			return False, 'No source specified'

		# if self.sort:
		# 	sort_func = lambda file : eval(self.sort)
		# 	self.source_files.sort(key=sort_func)



		img, *imgs = [Image.open(file) for file in self.source_files if self.exclusion_criteria not in file.split(os.sep)[-1]]

		try:
			img.save(fp=self.destination, format='GIF', append_images=imgs,
				save_all=True, duration=self.frame_duration, loop=self.loops)
		except ValueError:
			return False, 'Cannot determine output format'
		except OSError:
			return False, 'File could not be written'

		return True, 'Successfully created gif'


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.title = 'Gifify'

		self.giffer = Giffer()

		self.init_UI()

	def init_UI(self):
		self.setWindowTitle(self.title)


		centralWidget = QWidget(self)
		centralLayout = QGridLayout(centralWidget)

		b1 = QPushButton('Choose Source', self)
		b2 = QPushButton('Choose Destination', self)
		b3 = QPushButton('Make GIF')

		b1.clicked.connect(lambda : self.open_source())
		b2.clicked.connect(lambda : self.choose_destination())
		b3.clicked.connect(lambda : self.go())

		centralLayout.addWidget(b1, 0,0)
		centralLayout.addWidget(b2, 0,1)
		centralLayout.addWidget(b3, 0,2)


		advanced_b = QPushButton('Advanced')
		advanced_b.clicked.connect(lambda : self.advanced_settings() )


		centralLayout.addWidget(advanced_b, 2,2)



		self.setCentralWidget(centralWidget)


	def open_source(self):
		source_files = self.open_file_dialog()
		if source_files:
			self.giffer.set_source_files(source_files)

	def choose_destination(self):
		destination = self.save_file_dialog()
		if destination:
			self.giffer.set_destination(destination)

	def go(self):
		success, message = self.giffer.make_gif()

		# if success

		self.user_message(message)

	def advanced_settings(self):
		advanced_window = AdvancedSettings(self)
		advanced_window.show()


	def user_message(self, message):
		msg = QMessageBox()
		# msg.setIcon(QMessageBox.Information)
		msg.setText(message)
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec_()

	def open_file_dialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		files, _ = QFileDialog.getOpenFileNames(self,"Open File", "",
			"Image Files (*.png *.jpg *.jpeg *.tif *.bmp *.gif)", options=options)
		if files:
			return files
		else:
			return None

	def save_file_dialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		filename, qfilter = QFileDialog.getSaveFileName(self,"Save File","","Graphics Interchange Format (*.gif)", options=options)
		if filename:
			filename += qfilter[-5:-1]
			return filename
		else:
			return None

class AdvancedSettings(QWidget):
	def __init__(self, parent):
		super().__init__()

		self.parent = parent

		self.init_UI()

	def init_UI(self):
		self.layout = QVBoxLayout(self)

		self.setWindowTitle('Advanced Settings')

		# duration
		duration_w = QWidget(self)
		duration_l = QHBoxLayout(duration_w)
		d_label = QLabel('Frame duration (ms)')
		d_value = QLineEdit()
		text = str(self.parent.giffer.get_frame_duration())
		d_value.setText(text)
		d_value.setValidator(QIntValidator())
		duration_l.addWidget(d_label)
		duration_l.addWidget(d_value)

		self.layout.addWidget(duration_w)
		self.duration_value = d_value


		# number of loops
		loop_w = QWidget(self)
		loop_l = QHBoxLayout(loop_w)
		l_label = QLabel('Number of gif loops\n(0 is infinite)')
		l_value = QLineEdit()
		text = str(self.parent.giffer.get_loops())
		l_value.setText(text)
		l_value.setValidator(QIntValidator())
		loop_l.addWidget(l_label)
		loop_l.addWidget(l_value)

		self.layout.addWidget(loop_w)
		self.loop_value = l_value



		# # sort lambda
		# sort_w = QWidget(self)
		# sort_l = QVBoxLayout(sort_w)
		# s_label = QLabel('File sorting lambda')
		# text = str(self.parent.giffer.get_sort_lambda())
		# s_lambda = QLineEdit(text)
		# sort_l.addWidget(s_label)
		# sort_l.addWidget(s_lambda)

		# self.layout.addWidget(sort_w)
		# self.sort_lambda = s_lambda


		# exclusion criteria
		exclude_w = QWidget(self)
		exclude_l = QHBoxLayout(exclude_w)
		x_label = QLabel('Exclude files with this in name')
		text = str(self.parent.giffer.get_exclusion_criteria())
		x_value = QLineEdit(text)
		exclude_l.addWidget(x_label)
		exclude_l.addWidget(x_value)

		self.layout.addWidget(exclude_w)
		self.exclusion_criteria = x_value



		# apply and cancel buttons
		actions_w = QWidget(self)
		actions_l = QHBoxLayout(actions_w)
		act_apply = QPushButton('Apply')
		act_cancel = QPushButton('Cancel')
		act_apply.clicked.connect(lambda : self.apply() )
		act_cancel.clicked.connect(lambda : self.cancel() )
		actions_l.addWidget(act_apply)
		actions_l.addWidget(act_cancel)

		self.layout.addWidget(actions_w)


		



	def apply(self):

		self.parent.giffer.set_frame_duration(self.duration_value.text())
		self.parent.giffer.set_loops(self.loop_value.text())

		# self.parent.giffer.set_sort_lambda(self.sort_lambda.text())
		self.parent.giffer.set_exclusion_criteria(self.exclusion_criteria.text())

		self.close()

	def cancel(self):
		self.close()

class App(QApplication):
	def __init__(self, *args):
		QApplication.__init__(self, *args)
		self.main = MainWindow()
		self.main.show()

	def byebye(self):
		self.exit(0)




def main(args):
	global app
	app = App(args)
	app.exec_()

if __name__ == '__main__':
	main(sys.argv)