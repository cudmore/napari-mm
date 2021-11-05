"""
Working out to write code to interact with Napari viewer.

In particular
    - USing either a Shape or Points layer
    - be notified of new shapes/points
    - be notified of user changing a point/shape (by dragging)
    - be notified when a shape/point is deleted
"""

import time
import napari
from napari.qt import thread_worker
from skimage.io import imread
from skimage.morphology import disk, ball
from skimage.filters.rank import gradient

import numpy as np
import pandas as pd

def _loadLine(path):
    skiprows = 7  # todo: read this from header comment
    df = pd.read_csv(path, skiprows=skiprows)
    print(df.head())

path = '/home/cudmore/Downloads/bil/d9/01/rr30a_s1_ch2.tif'
linePath = '/home/cudmore/Downloads/bil/d9/01/line/rr30a_s0_l.txt'

#_loadLine(linePath)

#image = imread(path)
#print(image.shape)

#image = image[20,:,:]
#image = image.astype(np.uint8)

# 2
'''
viewer = napari.Viewer()

imageLayer = viewer.add_image(image, colormap='green', blending='additive')

points = np.array([[100, 100], [200, 200], [300, 100]])
pointsLayer = viewer.add_points(points, size=30)
'''

#viewer.add_image(gradient(image, disk(5)), name='gradient', colormap='magenta', blending='additive')

#viewer.add_shapes([[ 100,80], [140, 150]], shape_type='path', edge_color='cyan', edge_width=3)

# 3
#from napari_plot_profile import PlotProfile
#profiler = PlotProfile(viewer)
#viewer.window.add_dock_widget(profiler, area='right')

# 4
#profiler._list_values()

# global to keep track of selected point/shape
gMySelectedPoint = None

def getPointFromSet(setOfPnts):
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


def mySelectionChanged(event):
    print('=== mySelectionChanged()')
    
def print_layer_name(event):
    """
    event is <class 'napari.utils.events.event.Event'>
    
    event.source.selected_data is a set of selected point indices
    
    use just the selected points to update out table

    on highlight, use selected_data {} and compare to stored value
    to determine if it is new
    """
    print('=== print_layer_name()')
    
    #print('vars(event):', vars(event))
    
    print('  type(event)', type(event))
    
    # event.source is the layer (like Points or Shapes)
    print('  type(event.source)', type(event.source))
    
    # event.source is a HUGE object
    #print('vars(event.source):', vars(event.source))
    #print('   ', type(event.source))
    
    # event.type is in {'interactive', 'mode', 'data'}
    print('  type(event.type):', type(event.type))
    print('  event.type:', event.type)
    
    # name is name of layer(can be set by user in interface)
    print('  event.source.name:', event.source.name)
    
    # mode is {'add', 'select', 'pan-zoom'}
    print('  event.source.mode:', event.source.mode)

    # 1) when mode is 'add' we get added point index in selected_data set
    #   point 3 would be selected_data={3}
    # 2) when mode is 'select' and user finishes dragging we get point that was moved
    # 3) when user deletes a point, select_data=set()
    #    we need to keep track of selected point with worker 'selectedDataWorker'(below)
    #    When we delete, be sure to set local copy of selectedData to none (handled in worker???)
    #       20211104 delete is not triggering any callbacks !!!!!!!!!!!!

    print('  event.source.selected_data:', event.source.selected_data)

    # list of list of points
    try:
        print('  event.value:', event.value)
    except (AttributeError) as e:
        print('  value: AttributeError')

    # event.source.data is a list of list of points (can be 1000's)
    #print('  data:', event.source.data)
    
    # see: https://napari.org/docs/0.3.7/_modules/napari/layers/points/points.html
    # we can always query layer for state (we can also set)
    # print('  pointsLayer.mode:', pointsLayer.mode)

    selectedDataIsEmpty = event.source.selected_data == set()
    
    isAdd = event.source.mode == 'add'
    isFinishedDrag = event.source.mode == 'select' and not selectedDataIsEmpty
    isDelete = event.source.selected_data == set()

    print(f'  isAdd: {isAdd}')
    print(f'  isFinishedDrag: {isFinishedDrag}')
    print(f'  isDelete: {isDelete}')

    if isAdd:
        # always last point
        newPnt = getPointFromSet(event.source.selected_data)
        print(f'    newPnt: {newPnt}')
        newPosition = event.source.data[newPnt]
        print(f'    new position: {newPosition}')
    elif isFinishedDrag:
        draggedPnt = getPointFromSet(event.source.selected_data)
        print(f'    draggedPnt: {draggedPnt}')
        newPosition = event.source.data[draggedPnt]
        print(f'    new position: {newPosition}')
    elif isDelete:
        # we need to use last pnt selection from worker thread
        print(f'    gMySelectedPoint: {gMySelectedPoint}')


# these work
# for a list of events, see
# https://napari.org/docs/0.3.7/_modules/napari/layers/base/base.html
#pointsLayer.events.refresh.connect(print_layer_name)
#pointsLayer.events.set_data.connect(print_layer_name)
#pointsLayer.events.mode.connect(print_layer_name)
#pointsLayer.events.interactive.connect(print_layer_name)
#pointsLayer.events.status.connect(print_layer_name)

# select/deselect are depreciated and do nothing
# I think they were to signal when entire layer is selected (no a single point/shape)
#pointsLayer.events.select.connect(print_layer_name)
#pointsLayer.events.deselect.connect(print_layer_name)

'''
def xxxOnSelection(event):
    print('xxx')
viewer.layers.selection.events.changed.connect(xxxOnSelection)
'''

# no work
# pointsLayer.events.inserting.connect(print_layer_name)

# viewer.layers.selection.events.changed
# inspect added and removed
#pointsLayer.selection.events.changed(print_layer_name)

# this triggers on mouse move
#pointsLayer.events.highlight.connect(print_layer_name)

# no work
# pointsLayer.events.add.connect(print_layer_name)

# I need this to get selected point (why so complicated)
# This simply polls pointsLayer.selected_data and trigger when it changes
def selectedDataWorker(pointsLayer, poll = 1):  
    """
    Show selected data
    """
    def onSelectedDataChanged(selectedData):
        if selectedData is not None:
            #if len(selectedData) > 0:
            
            # triggered when mode='select' and user click a point/shape
            # When user clicks canvas, all points are de-selected
            #   selectedData is empty set()
            global gMySelectedPoint
            gMySelectedPoint = getPointFromSet(selectedData)
            
            print()
            print('  === onSelectedDataChanged() WORKER', selectedData)
            print(f'    selectedData: {selectedData}')
            print(f'    gMySelectedPoint: {gMySelectedPoint}')
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



if __name__ == '__main__':
    path = '/home/cudmore/Downloads/bil/d9/01/rr30a_s1_ch2.tif'
    image = imread(path)

    viewer = napari.Viewer()

    imageLayer = viewer.add_image(image, colormap='green', blending='additive')

    points = np.array([[100, 100], [200, 200], [300, 100]])
    pointsLayer = viewer.add_points(points, size=30)

    # when we switch between layers
    viewer.layers.selection.events.changed.connect(mySelectionChanged)

    pointsLayer.events.data.connect(print_layer_name)

    worker = selectedDataWorker(pointsLayer, poll = 1/10)

    #
    napari.run() 