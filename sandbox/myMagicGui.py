"""
Working out how to create magicgui interface objects

    - All magicgui interface objects have underlying Qt objects
        For example, a mgicgui 'Table' has and underlying QTableWidget object
"""
import pandas as pd

from magicgui import magicgui
from magicgui.widgets import Table

from enum import Enum

#
# Example off magicgui website

class Medium(Enum):
    Glass = 1.520
    Oil = 1.515
    Water = 1.333
    Air = 1.0003

# decorate your function with the @magicgui decorator
@magicgui(call_button="calculate", result_widget=True, layout='vertical')
def snells_law(aoi=30.0, n1=Medium.Glass, n2=Medium.Water, degrees=True):
    import math

    aoi = math.radians(aoi) if degrees else aoi
    try:
        result = math.asin(n1.value * math.sin(aoi) / n2.value)
        return math.degrees(result) if degrees else result
    except ValueError:
        return "Total internal reflection!"

# your function is now capable of showing a GUI


#
# Working out how to use magicgui Table (e.g. a QTableWidget)

# load some data
df = pd.read_csv('data/iris.csv')
print(len(df))
print(df.head())
dfDict = df.to_dict()

def myTableChanged(d : dict):
    """
    Respond to user editing a single cell.

    This is a convenience wrapper/callback provided by magicgui?


    Params:
        d (dict): Dictionary of new value and underlying row and column

        For example:
            d = {'data': <value>, 'row': int, 'column': int, 'column_header': str, 'row_header': str}

            Where <value> of 'data' will be new 'value'
            and <value> will be proper type, str if str, int if int, float if float
            does not support list or dict (they are received as str)
    """
    print('=== (1) myTableChanged()')
    print(f"  d['data'] is '{d['data']}' with type: {type(d['data'])}")
    print(d)

# see: https://doc.qt.io/qt-5.15/qtablewidget.html
# for definitions of (itemChanged, itemClicked)
def onItemChanged(item):
    """
    Resond to user editing a single cell.

    This is a native callback for PyQt?

    Params:
        item (QTableWidgetItem): The item that was edited

    Note:
        item.text() is the new str representation of the value (it is always a str)
    """
    print('=== (2) onItemChanged()')
    print('  item.row:', item.row())
    print('  item.col:', item.column())
    newText = item.text()
    print(f'  item.text: "{newText}" type:{type(newText)}')
    # ...
    # whatever you want to do with the new value

def onItemClicked(item):
    """
    Respond to user clicking table.

    Params:
        item (QTableWidgetItem): The item clicked
    """
    print('=== onItemClicked item:', item)
    print('  row:', item.row())
    print('  col:', item.column())

# Create a magicgui table from a dict
myTable = Table(value=dfDict)

# this seems to be provided as a convenience function from napari/magicgui
myTable.changed.connect(myTableChanged)

# this returns <magicgui.backends._qtpy.widgets._QTableExtended object at 0x7f4871304c10>
# print('myTable.native:', myTable.native)

# returns <magicgui.backends._qtpy.widgets.Table object at 0x7f258a5cfbe0>
#print(myTable._widget)


myTable.native.itemChanged.connect(onItemChanged)

myTable.native.itemClicked.connect(onItemClicked)

# Working on getting the underlying QTableWidget from the magicgui Table

# my style
from PyQt5 import QtWidgets

# their style
#from qtpy import QtWidgets as QtW

# both of these report type <class 'magicgui.backends._qtpy.widgets._QTableExtended'>
#   but ... it seems to really be a QTableWidget
print('myTable._widget._qwidget is:', type(myTable._widget._qwidget))
print('myTable.native is:', type(myTable.native))

# set selection modes so we can only select one row
myTable.native.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
myTable.native.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

# works
#myTable._widget._qwidget.setSelectionMode(QtW.QAbstractItemView.SingleSelection)
#myTable._widget._qwidget.setSelectionBehavior(QtW.QAbstractItemView.SelectRows)

# programatically select a row
# myTable._widget._qwidget.selectRow(3)
myTable.native.selectRow(3)


if __name__ == "__main__":
    # this works
    # snells_law.show(run=False)

    # this works
    myTable.show(run=True)
