## Install Napari

### Linux/Debian/Ubuntu

```
sudo apt-get install python3-pyqt5
sudo apt-get install python3-pyqt5.qtopengl

# clone
git clone https://github.com/napari/napari.git

# virtual environment
python -m venv mm_env
source mm_env/bin/activate

# force particular version of PyQt (newer versions do not work)
pip install PyQt5==5.12.3

pip install -e napari/.[PyQt5]
```
### macOS

Will only work on x86 architecture. On M1 mac need to use Rosetta.

### Windows

Follow Napari recipe

## Keep track of a layer

- Select: worker
- Deselect: worker
- Move: simple callback
- Add: simple callback
- Subtract: simple callback (that uses select from worker to know what was deleted)

## SWC file format

From: http://www.neuromorpho.org/myfaq.jsp

The three dimensional structure of a neuron can be represented in a SWC format (Cannon et al., 1998). SWC is a simple Standardized format. Each line has 7 fields encoding data for a single neuronal compartment:
an integer number as compartment identifier
type of neuronal compartment
   0 - undefined
   1 - soma
   2 - axon
   3 - basal dendrite
   4 - apical dendrite
   5 - custom (user-defined preferences)
   6 - unspecified neurites
   7 - glia processes

x coordinate of the compartment
y coordinate of the compartment
z coordinate of the compartment
radius of the compartment
parent compartment
Every compartment has only one parent and the parent compartment for the first point in each file is always -1 (if the file does not include the soma information then the originating point of the tree will be connected to a parent of -1). The index for parent compartments are always less than child compartments. Loops and unconnected branches are excluded. All trees should originate from the soma and have parent type 1 if the file includes soma information. Soma can be a single point or more than one point. When the soma is encoded as one line in the SWC, it is interpreted as a "sphere". When it is encoded by more than 1 line, it could be a set of tapering cylinders (as in some pyramidal cells) or even a 2D projected contour ("circumference").