"""
"""

import time
import tifffile
import napari
from napari.qt import thread_worker
#from skimage.io import imread
#from skimage.morphology import disk, ball
#from skimage.filters.rank import gradient

import numpy as np
import pandas as pd

def _loadLine(path):
    skiprows = 7  # todo: read this from header comment
    df = pd.read_csv(path, skiprows=skiprows)
    print(df.head())
linePath = '/home/cudmore/Downloads/bil/d9/01/line/rr30a_s0_l.txt'
#_loadLine(linePath)


class myClass():
    def __init__(self, viewer, pointsLayer):
        self._pointsLayer = pointsLayer
        self._mySelectedPoint = None

        # when we switch between layers
        viewer.layers.selection.events.changed.connect(self.mySelectionChanged)

        pointsLayer.events.data.connect(self.print_layer_name)

        self._worker = self.selectedDataWorker(pointsLayer, poll = 1/10)

    def selectedDataWorker(self, pointsLayer, poll = 1):
        """
        Show selected data
        """
        def onSelectedDataChanged(selectedData):
            if selectedData is not None:
                #if len(selectedData) > 0:

                # triggered when mode='select' and user click a point/shape
                # When user clicks canvas, all points are de-selected
                #   selectedData is empty set()
                self._mySelectedPoint = self._getPointFromSet(selectedData)

                print()
                print('  === onSelectedDataChanged() WORKER', selectedData)
                print(f'    selectedData: {selectedData}')
                print(f'    _mySelectedPoint: {self._mySelectedPoint}')
                print()

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

    def mySelectionChanged(self, event):
        print('=== mySelectionChanged()')

    def print_layer_name(self, event):
        print('=== print_layer_name()')

        selectedDataIsEmpty = event.source.selected_data == set()

        isAdd = event.source.mode == 'add'
        isFinishedDrag = event.source.mode == 'select' and not selectedDataIsEmpty
        isDelete = event.source.selected_data == set()

        print(f'  isAdd: {isAdd}')
        print(f'  isFinishedDrag: {isFinishedDrag}')
        print(f'  isDelete: {isDelete}')

        if isAdd:
            # always last point
            newPnt = self._getPointFromSet(event.source.selected_data)
            print(f'    newPnt: {newPnt}')
            newPosition = event.source.data[newPnt]
            print(f'    new position: {newPosition}')
        elif isFinishedDrag:
            draggedPnt = self._getPointFromSet(event.source.selected_data)
            print(f'    draggedPnt: {draggedPnt}')
            newPosition = event.source.data[draggedPnt]
            print(f'    new position: {newPosition}')
        elif isDelete:
            # we need to use last pnt selection from worker thread
            print(f'    _mySelectedPoint: {self._mySelectedPoint}')


    def _getPointFromSet(self, setOfPnts):
        """
        Retun one index from a set of index.

        Args:
            setOfPnts (set): Set of point indices

        Note:
            todo: currently modifies setOfPnts with pop !!!
        """
        if len(setOfPnts) != 1:
            print(f'error getSelectedPoint() expecting set of length 1 but got length {len(setOfPnts)}, setOfPnts: {setOfPnts}')
            return None
        item = setOfPnts.pop()
        return item

if __name__ == '__main__':
    path = '/home/cudmore/Downloads/bil/d9/01/rr30a_s1_ch2.tif'
    image = tifffile.imread(path)

    viewer = napari.Viewer()

    imageLayer = viewer.add_image(image, colormap='green', blending='additive')

    points = np.array([[100, 100], [200, 200], [300, 100]])
    pointsLayer = viewer.add_points(points, size=30)

    aMyClass = myClass(viewer,pointsLayer)
    #
    napari.run()
