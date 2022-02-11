"""
"""

import sys
import time
import warnings
import logging
import tifffile
import numpy as np
import pandas as pd

import napari
from napari.qt import thread_worker
from PyQt5 import QtCore, QtWidgets

from magicgui import magicgui
from magicgui.widgets import Table

# set up logging
logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG)
streamHandler = logging.StreamHandler(sys.stdout)
consoleFormat = '%(levelname)5s %(name)8s  %(filename)s %(funcName)s() line:%(lineno)d -- %(message)s'
c_format = logging.Formatter(consoleFormat)
streamHandler.setFormatter(c_format)
logger.addHandler(streamHandler)

def _loadLine(path):
	skiprows = 7  # todo: read this from header comment
	df = pd.read_csv(path, skiprows=skiprows)
	print(df.head())

linePath = '/home/cudmore/Downloads/bil/d9/01/line/rr30a_s0_l.txt'
#_loadLine(linePath)


class myInterface():
	def __init__(self, viewer, layer):

		"""
		layer.data is list of list like:
		"""
		self._viewer = viewer
		self._layer = layer

		self._data = layer.data  # list of list of points

		print('*** layer.data:', layer.data)

		self._myListener = myInterfaceListener(viewer, layer)

		self._myListener.userSelect.connect(self.slot_UserSelect)
		self._myListener.userMove.connect(self.slot_UserMove)
		self._myListener.userNew.connect(self.slot_UserNew)
		self._myListener.userDelete.connect(self.slot_UserDelete)

		self.InitGui()

	def setRow(self, rowSet : set, pntList : list):
		"""
		set row to new values

		each element in pntList is an ndarray
		"""
		logger.info(f'rowSet:{rowSet}, pntList:{pntList}')

		# data is <class 'magicgui.widgets._table.DataView'>
		print('self.myTable.data:', type(self.myTable.data))
		print(self.myTable.data)

		for idx, row in enumerate(rowSet):
			print(f'  !!! idx:{idx} row:{row} {type(row)}')
			print('  ', pntList[idx], type(pntList[idx]))

			# I don't understand indexing here
			# this is giving me a column
			# this SHOULD WORK !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			#self.myTable.data[row,:] = pntList[idx]

	def InitGui(self):
		self.myTable = Table(value=self._data)

		# select one and only one row (not cells and not multiple rows)
		#self.myTable.native.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.myTable.native.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
		#self.myTable.native.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.myTable.native.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

		# this would allow user edits in table
		#myTable.native.itemChanged.connect(onItemChanged)

		# user select row -->> select in viewer layer
		self.myTable.native.itemClicked.connect(self.onItemClicked)

		self.myTable.show(run=True)

	def onItemClicked(self, item):
		"""
		Respond to user clicking table and select in viewer

		Params:
			item (QTableWidgetItem): The item clicked
		"""
		selectionModel = self.myTable.native.selectionModel()
		selectedRows = selectionModel.selectedRows()

		selectedRowList = []
		for selectedRow in selectedRows:
			print('  selectedRow:', selectedRow.row())
			selectedRowList.append(selectedRow.row())
		selectedRowSet = set(selectedRowList)

		#
		# emit back to viewer

		# select point set
		self._layer.selected_data = selectedRowSet

		# if one nt selected, snap z
		if len(selectedRowList) == 1:
			axis = 0 # assuming (z,y,x)
			selectedRow = selectedRowList[0]
			zSlice = self._data[selectedRow][0]
			logger.info(f'zSlice: {zSlice}')
			self._viewer.dims.set_point(axis, zSlice)

	def slot_UserSelect(self, pntSet : set):
		logger.info(f'pntSet: {pntSet}')

		if len(pntSet) == 0:
			self.myTable.native.clearSelection()
		else:
			for row in pntSet:
				self.myTable.native.selectRow(row)  # native gives us underlying Qt widget

	def slot_UserMove(self, idxList, pntSet):
		logger.info(f'idx: {idxList} pntSet:{pntSet}')
		self.setRow(idxList, pntSet)

	def slot_UserNew(self, idx, newPos):
		"""
		User created a new point, add it to our table list

		TODO: add to table data (self._data)
		"""
		logger.info(f'idx: {idx} newPos:{newPos} {type(newPos)}')

	def slot_UserDelete(self, pntSet):
		logger.info(f'pntSet: {pntSet}')

class myInterfaceListener(QtCore.QObject):
	# signals
	userSelect = QtCore.pyqtSignal(set)
	userMove = QtCore.pyqtSignal(set, np.ndarray)
	userNew = QtCore.pyqtSignal(int, list) # always one pnt
	userDelete = QtCore.pyqtSignal(set)

	def __init__(self, viewer, pointsLayer):
		super().__init__()

		self._pointsLayer = pointsLayer
		self._mySelectedPoint = None

		# when we switch between layers
		viewer.layers.selection.events.changed.connect(self.mySelectionChanged)

		# respond to changes in data including (select, move, new, delete)
		pointsLayer.events.data.connect(self.print_layer_name)

		# worker to monitor mouse move and more importantly user selection
		# see: https://github.com/vispy/vispy/issues/2212
		self._worker = self._selectedDataWorker(pointsLayer, poll = 1/10)

	def userSelectPoint(self, idx):
		"""
		The user selected a point
		"""
		#logger.info(f'idx:{idx}')
		self._mySelectedPoint = idx
		self.userSelect.emit(self._mySelectedPoint)

	def userNewPoint(self, idx, pos):
		"""
		Args:
			pos (list)

		TODO:
			fix type we are passed, it is currently a list of lists (numpy)
		"""
		logger.info(f'idx:{idx} pos:{pos} {type(pos)}')

		pos = pos.tolist()

		self.userNew.emit(self._mySelectedPoint, pos)

	def userMovePoint(self, idx, newPos):
		"""
		The user dragged a point

		Args:
			idx (int)
			newPos (np.ndarray)
		"""
		#logger.info(f'idx:{idx} newPos:{newPos}')
		self.userMove.emit(self._mySelectedPoint, newPos)

	def userDeletePoint(self, idx):
		"""
		The user deleted a point
		"""
		#logger.info(f'idx: {idx}')
		self.userDelete.emit(idx)

	def mySelectionChanged(self, event):
		"""
		When user selects a different layer
		"""
		print('=== mySelectionChanged() event:', event)

	def print_layer_name(self, event):
		#logger.info('')

		selectedDataIsEmpty = event.source.selected_data == set()

		# use event.source to decide on the type of action
		isAdd = event.source.mode == 'add'
		isFinishedDrag = event.source.mode == 'select' and not selectedDataIsEmpty
		isDelete = event.source.selected_data == set()

		'''
		print(f'  isAdd: {isAdd}')
		print(f'  isFinishedDrag: {isFinishedDrag}')
		print(f'  isDelete: {isDelete}')
		'''

		#print('=== event.source.selected_data:', event.source.selected_data)

		if isAdd:
			# always one point
			# always the last point
			#newPnt = self._getPointFromSet(event.source.selected_data)
			newPnt = list(event.source.selected_data)
			newPosition = event.source.data[newPnt]  # np.ndarray
			'''
			print(f'	newPnt: {newPnt}')
			print(f'	new position: {newPosition}')
			'''
			self.userNewPoint(newPnt, newPosition)
		elif isFinishedDrag:
			#draggedPnt = self._getPointFromSet(event.source.selected_data)
			draggedSet = event.source.selected_data
			draggedList = list(draggedSet)
			newPositions = event.source.data[draggedList]
			'''
			print(f'	draggedPnt: {draggedPnt}')
			print(f'	new position: {newPosition}')
			'''
			self.userMovePoint(draggedSet, newPositions)
		elif isDelete:
			# we need to use last pnt selection from worker thread
			# delete the selected point
			#print(f'	_mySelectedPoint: {self._mySelectedPoint}')
			currentPoint = self._mySelectedPoint
			self.userDeletePoint(currentPoint)
		else:
			logger.info('No action taken')

	# this is triggering warnings on mouse move
	# see: https://github.com/napari/napari/issues/3214
	def _selectedDataWorker(self, pointsLayer, poll = 1):
		"""
		Show selected data
		"""
		def onSelectedDataChanged(selectedData):
			"""
			selectedData (set)
			"""
			if selectedData is not None:
				#if len(selectedData) > 0:

				# triggered when mode='select' and user click a point/shape
				# When user clicks canvas, all points are de-selected
				#   selectedData is empty set()
				#self._mySelectedPoint = self._getPointFromSet(selectedData)

				'''
				selectedPoint = self._getPointFromSet(selectedData)
				self.userSelectPoint(selectedPoint)
				'''
				#newSelection = list(selectedData)
				#self.userSelectPoint(newSelection)
				self.userSelectPoint(selectedData)

				'''
				print()
				print('  === onSelectedDataChanged() WORKER', selectedData)
				print(f'	selectedData: {selectedData}')
				#print(f'	_mySelectedPoint: {self._mySelectedPoint}')
				print()
				'''

		"""
		Listen to selected data changes
		When connect parameter is not None the worker starts automatically
		Otherwise need to call worker.start()
		"""
		@thread_worker(connect={'yielded': onSelectedDataChanged})
		def _watchSelectedData(pointsLayer):
			selectedData = None

			while True:
				time.sleep(poll)
				oldSelectedData = selectedData

				# here we are repeatedly polling the pointsLayer.selected_data
				selectedData = pointsLayer.selected_data

				if oldSelectedData != selectedData:
					yield selectedData

				yield None

		return(_watchSelectedData(pointsLayer))

if __name__ == '__main__':
	#path = '/home/cudmore/Downloads/bil/d9/01/rr30a_s1_ch2.tif'
	path = '/media/cudmore/data/richard/rr30a/raw/rr30a_s0_ch2.tif'

	image = tifffile.imread(path)
	print('image is', image.shape, image.dtype)

	viewer = napari.Viewer()

	#print(viewer.dims.indices)
	print('viewer.dims.point:', viewer.dims.point)
	print('viewer.dims.order:', viewer.dims.order)

	imageLayer = viewer.add_image(image, colormap='green', blending='additive')

	# set viewer to slice zSLice
	axis = 0
	zSlice = 29
	viewer.dims.set_point(axis, zSlice)

	# synthetic points
	points = np.array([[zSlice, 100, 100], [zSlice, 200, 200], [zSlice, 300, 300], [zSlice, 400, 400]])

	pointsLayer = viewer.add_points(points, size=20, name='My Points')
	pointsLayer.mode = 'select'

	aMyInterface = myInterface(viewer, pointsLayer)
	#interfaceListener = myInterfaceListener(viewer,pointsLayer)
	#
	napari.run()
